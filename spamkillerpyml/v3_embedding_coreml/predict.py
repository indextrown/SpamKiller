from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
CONFIG_PATH = ARTIFACTS_DIR / "config.json"
MLMODEL_PATH = ARTIFACTS_DIR / "SpamKillerEmbeddingClassifier.mlmodel"


def load_dependencies():
    try:
        import coremltools as ct
    except ImportError as error:
        raise SystemExit(
            "coremltools가 설치되어 있지 않습니다.\n"
            "먼저 `pip install -r requirements.txt` 를 실행해주세요."
        ) from error

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise SystemExit(
            "sentence-transformers가 설치되어 있지 않습니다.\n"
            "먼저 `pip install -r requirements.txt` 를 실행해주세요."
        ) from error

    return ct, SentenceTransformer


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            'Usage: python spamkillerpyml/v3_embedding_coreml/predict.py "문자 내용을 여기에 입력"'
        )

    if not CONFIG_PATH.exists() or not MLMODEL_PATH.exists():
        raise SystemExit(
            "먼저 `python spamkillerpyml/v3_embedding_coreml/train.py` 로 모델을 학습해주세요."
        )

    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    text = " ".join(sys.argv[1:])

    ct, SentenceTransformer = load_dependencies()
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    embedding_model = SentenceTransformer(
        payload["embedding_model"],
        local_files_only=True,
    )
    coreml_model = ct.models.MLModel(str(MLMODEL_PATH))

    vector = embedding_model.encode(
        [text],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )[0]

    prediction = coreml_model.predict({"embedding": vector})

    print(
        json.dumps(
            {
                "text": text,
                "label": prediction["label"],
                "probabilities": prediction["labelProbabilities"],
                "embedding_model": payload["embedding_model"],
                "mlmodel_path": str(MLMODEL_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
