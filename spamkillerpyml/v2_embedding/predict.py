from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
CONFIG_PATH = ARTIFACTS_DIR / "config.json"
CLASSIFIER_PATH = ARTIFACTS_DIR / "classifier.joblib"


def load_dependencies():
    try:
        import joblib
    except ImportError as error:
        raise SystemExit(
            "joblib이 설치되어 있지 않습니다.\n"
            "먼저 `pip install -r requirements.txt` 를 실행해주세요."
        ) from error

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise SystemExit(
            "sentence-transformers가 설치되어 있지 않습니다.\n"
            "먼저 `pip install -r requirements.txt` 를 실행해주세요."
        ) from error

    return joblib, SentenceTransformer


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            'Usage: python spamkillerpyml/v2_embedding/predict.py "문자 내용을 여기에 입력"'
        )

    if not CONFIG_PATH.exists() or not CLASSIFIER_PATH.exists():
        raise SystemExit(
            "먼저 `python spamkillerpyml/v2_embedding/train.py` 로 모델을 학습해주세요."
        )

    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    text = " ".join(sys.argv[1:])

    joblib, SentenceTransformer = load_dependencies()
    embedding_model = SentenceTransformer(payload["embedding_model"])
    classifier = joblib.load(CLASSIFIER_PATH)

    vector = embedding_model.encode(
        [text],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    label = classifier.predict(vector)[0]

    probabilities = None
    if hasattr(classifier, "predict_proba"):
        raw_probabilities = classifier.predict_proba(vector)[0]
        probabilities = {
            label_name: round(float(probability), 6)
            for label_name, probability in zip(classifier.classes_, raw_probabilities)
        }

    print(
        json.dumps(
            {
                "text": text,
                "label": label,
                "probabilities": probabilities,
                "embedding_model": payload["embedding_model"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
