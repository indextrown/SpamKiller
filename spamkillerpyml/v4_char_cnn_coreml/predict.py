from __future__ import annotations

import json
import math
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
CONFIG_PATH = ARTIFACTS_DIR / "config.json"
VOCAB_PATH = ARTIFACTS_DIR / "vocab.json"
MODEL_PATH = ARTIFACTS_DIR / "SpamKillerCharCNN.mlpackage"
WEIGHTS_PATH = ARTIFACTS_DIR / "weights.pt"
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"


def encode_text(text: str, vocab: dict[str, int], max_length: int) -> list[int]:
    encoded = [vocab.get(char, vocab[UNK_TOKEN]) for char in text[:max_length]]
    if len(encoded) < max_length:
        encoded.extend([vocab[PAD_TOKEN]] * (max_length - len(encoded)))
    return encoded


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def predict_with_pytorch(encoded: list[int], config: dict[str, object]) -> tuple[str, dict[str, float]]:
    import torch
    try:
        from .train import build_model_from_config
    except ImportError:
        from v4_char_cnn_coreml.train import build_model_from_config

    model = build_model_from_config(config)
    state_dict = torch.load(WEIGHTS_PATH, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()

    with torch.no_grad():
        tensor = torch.tensor([encoded], dtype=torch.long)
        logits = model(tensor)
        spam_probability = sigmoid(float(logits[0].item()))

    label = config["positive_label"] if spam_probability >= 0.5 else config["negative_label"]
    probabilities = {
        config["negative_label"]: round(1.0 - spam_probability, 6),
        config["positive_label"]: round(spam_probability, 6),
    }
    return label, probabilities


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            'Usage: python spamkillerpyml/v4_char_cnn_coreml/predict.py "문자 내용을 여기에 입력"'
        )

    if not CONFIG_PATH.exists() or not VOCAB_PATH.exists():
        raise SystemExit(
            "먼저 `python spamkillerpyml/v4_char_cnn_coreml/train.py` 로 모델을 학습해주세요."
        )

    try:
        import coremltools as ct
    except ImportError as error:
        raise SystemExit(
            "coremltools가 설치되어 있지 않습니다.\n먼저 `pip install -r requirements.txt` 를 실행해주세요."
        ) from error

    temp_dir = ARTIFACTS_DIR / ".tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    os.environ["TMPDIR"] = str(temp_dir.resolve())
    tempfile.tempdir = str(temp_dir.resolve())

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    vocab = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    text = " ".join(sys.argv[1:])
    encoded = encode_text(text, vocab, config["max_length"])

    label = None
    probabilities = None

    if MODEL_PATH.exists():
        try:
            model = ct.models.MLModel(str(MODEL_PATH))
            prediction = model.predict({"char_ids": [encoded]})
            logits = float(prediction["logits"][0])
            spam_probability = sigmoid(logits)
            label = config["positive_label"] if spam_probability >= 0.5 else config["negative_label"]
            probabilities = {
                config["negative_label"]: round(1.0 - spam_probability, 6),
                config["positive_label"]: round(spam_probability, 6),
            }
        except Exception:
            if not WEIGHTS_PATH.exists():
                raise
            label, probabilities = predict_with_pytorch(encoded, config)
    else:
        if not WEIGHTS_PATH.exists():
            raise SystemExit("mlpackage와 weights.pt가 모두 없습니다.")
        label, probabilities = predict_with_pytorch(encoded, config)

    print(
        json.dumps(
            {
                "text": text,
                "label": label,
                "probabilities": probabilities,
                "mlmodel_path": config["mlmodel_artifact"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
