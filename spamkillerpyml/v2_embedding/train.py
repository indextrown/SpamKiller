from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT.parent / "data"
DEFAULT_DATASET = DATA_DIR / "train.csv"
DEFAULT_VALIDATION_DATASET = DATA_DIR / "validation.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts"
LABELS = ("ham", "spam")
NEGATIVE_LABEL = "ham"
POSITIVE_LABEL = "spam"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "문장을 임베딩 벡터로 바꾼 뒤, 그 벡터 위에 로지스틱 회귀 분류기를 학습합니다."
        )
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="학습에 사용할 CSV 경로. 기본값: spamkillerpyml/data/train.csv",
    )
    parser.add_argument(
        "--validation-dataset",
        type=Path,
        default=DEFAULT_VALIDATION_DATASET,
        help="검증에 사용할 CSV 경로. 기본값: spamkillerpyml/data/validation.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="산출물 저장 폴더",
    )
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_EMBEDDING_MODEL,
        help="sentence-transformers 모델 이름 또는 로컬 경로",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="학습 데이터 비율. 기본값 0.8",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="데이터 셔플 고정 시드",
    )
    return parser.parse_args()


def load_dataset(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip().lower()
            if not text or label not in LABELS:
                continue
            rows.append((text, label))
    if not rows:
        raise ValueError(f"No valid rows found in {path}")
    return rows


def split_dataset(
    rows: list[tuple[str, str]],
    train_ratio: float,
    seed: int,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    shuffled = rows[:]
    random.Random(seed).shuffle(shuffled)
    split_index = max(1, min(len(shuffled) - 1, int(len(shuffled) * train_ratio)))
    return shuffled[:split_index], shuffled[split_index:]


def save_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


@dataclass
class EmbeddingArtifacts:
    embedding_dimension: int
    train_metrics: dict[str, float | int]
    test_metrics: dict[str, float | int]
    label_distribution: dict[str, int]


def evaluate_classifier(classifier, vectors, labels) -> dict[str, float | int]:
    from sklearn.metrics import accuracy_score, classification_report

    predictions = classifier.predict(vectors)
    report = classification_report(
        labels,
        predictions,
        labels=[NEGATIVE_LABEL, POSITIVE_LABEL],
        output_dict=True,
        zero_division=0,
    )
    return {
        "accuracy": round(float(accuracy_score(labels, predictions)), 4),
        "samples": len(labels),
        "ham_precision": round(float(report[NEGATIVE_LABEL]["precision"]), 4),
        "ham_recall": round(float(report[NEGATIVE_LABEL]["recall"]), 4),
        "spam_precision": round(float(report[POSITIVE_LABEL]["precision"]), 4),
        "spam_recall": round(float(report[POSITIVE_LABEL]["recall"]), 4),
    }


def build_embedding_model(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise SystemExit(
            "sentence-transformers가 설치되어 있지 않습니다.\n"
            "먼저 `pip install -r requirements.txt` 를 실행해주세요."
        ) from error

    return SentenceTransformer(model_name)


def encode_texts(model, texts: list[str]):
    return model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )


def train_embedding_classifier(train_vectors, train_labels):
    try:
        from sklearn.linear_model import LogisticRegression
    except ImportError as error:
        raise SystemExit(
            "scikit-learn이 설치되어 있지 않습니다.\n"
            "먼저 `pip install -r requirements.txt` 를 실행해주세요."
        ) from error

    classifier = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )
    classifier.fit(train_vectors, train_labels)
    return classifier


def save_artifacts(
    output_dir: Path,
    classifier,
    embedding_model_name: str,
    artifacts: EmbeddingArtifacts,
) -> None:
    try:
        import joblib
    except ImportError as error:
        raise SystemExit(
            "joblib이 설치되어 있지 않습니다.\n"
            "먼저 `pip install -r requirements.txt` 를 실행해주세요."
        ) from error

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "classifier.joblib"
    config_path = output_dir / "config.json"
    metrics_path = output_dir / "metrics.json"

    joblib.dump(classifier, model_path)

    save_json(
        config_path,
        {
            "model_type": "embedding_plus_logistic_regression",
            "embedding_model": embedding_model_name,
            "embedding_dimension": artifacts.embedding_dimension,
            "negative_label": NEGATIVE_LABEL,
            "positive_label": POSITIVE_LABEL,
            "model_artifact": str(model_path),
            "notes": [
                "이 산출물은 임베딩 모델 자체를 포함하지 않습니다.",
                "예측 시에도 같은 sentence-transformers 모델로 임베딩을 다시 만들어야 합니다.",
                "Core ML로 바로 배포하려면 임베딩 모델까지 포함한 전체 파이프라인 설계가 추가로 필요합니다.",
            ],
        },
    )
    save_json(
        metrics_path,
        {
            "train": artifacts.train_metrics,
            "test": artifacts.test_metrics,
            "label_distribution": artifacts.label_distribution,
        },
    )


def main() -> None:
    args = parse_args()
    train_rows = load_dataset(args.dataset)
    validation_rows = load_dataset(args.validation_dataset) if args.validation_dataset.exists() else []

    train_texts = [text for text, _ in train_rows]
    train_labels = [label for _, label in train_rows]
    validation_texts = [text for text, _ in validation_rows]
    validation_labels = [label for _, label in validation_rows]

    print(f"Loaded {len(train_rows)} train rows from {args.dataset}")
    print(f"Loaded {len(validation_rows)} validation rows from {args.validation_dataset}")
    print(f"Embedding model: {args.embedding_model}")

    embedding_model = build_embedding_model(args.embedding_model)

    print("Encoding train texts...")
    train_vectors = encode_texts(embedding_model, train_texts)
    validation_vectors = None
    if validation_texts:
        print("Encoding validation texts...")
        validation_vectors = encode_texts(embedding_model, validation_texts)

    classifier = train_embedding_classifier(train_vectors, train_labels)

    train_metrics = evaluate_classifier(classifier, train_vectors, train_labels)
    validation_metrics = (
        evaluate_classifier(classifier, validation_vectors, validation_labels)
        if validation_vectors is not None
        else {"accuracy": 0.0, "samples": 0}
    )

    label_distribution = Counter(label for _, label in train_rows + validation_rows)
    artifacts = EmbeddingArtifacts(
        embedding_dimension=int(train_vectors.shape[1]),
        train_metrics=train_metrics,
        test_metrics=validation_metrics,
        label_distribution=dict(label_distribution),
    )
    save_artifacts(args.output_dir, classifier, args.embedding_model, artifacts)

    print(f"Saved classifier to {args.output_dir / 'classifier.joblib'}")
    print(f"Saved config to {args.output_dir / 'config.json'}")
    print(f"Saved metrics to {args.output_dir / 'metrics.json'}")
    if validation_rows:
        print(f"Validation accuracy: {validation_metrics['accuracy']}")


if __name__ == "__main__":
    main()
