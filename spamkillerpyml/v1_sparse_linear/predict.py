from __future__ import annotations

import json
import sys
from pathlib import Path

from train import LinearSpamClassifier


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "artifacts" / "model.json"


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python spamkillerpyml/v1_sparse_linear/predict.py "문자 내용을 여기에 입력"')

    payload = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    model = LinearSpamClassifier.from_dict(payload["model"])
    text = " ".join(sys.argv[1:])
    label, probabilities = model.predict(text)

    print(
        json.dumps(
            {"text": text, "label": label, "probabilities": probabilities},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
