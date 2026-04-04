from __future__ import annotations

import argparse
import csv
import json
import os
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
            "문장을 임베딩 벡터로 바꿔 로지스틱 회귀를 학습하고, "
            "임베딩 벡터 입력용 Core ML .mlmodel 까지 생성합니다."
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
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Hugging Face 캐시에 이미 받은 모델만 사용합니다.",
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


def build_embedding_model(model_name: str, local_files_only: bool):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise SystemExit(
            "sentence-transformers가 설치되어 있지 않습니다.\n"
            "먼저 `pip install -r requirements.txt` 를 실행해주세요."
        ) from error

    if local_files_only:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    return SentenceTransformer(model_name, local_files_only=local_files_only)


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


def export_coreml_classifier(classifier, embedding_dimension: int, output_path: Path) -> None:
    import coremltools as ct
    import numpy as np
    from coremltools import proto
    from coremltools.models import datatypes
    from coremltools.models._interface_management import set_classifier_interface_params
    from coremltools.models.utils import save_spec

    coefficients = np.asarray(classifier.coef_, dtype=np.float32)
    intercepts = np.asarray(classifier.intercept_, dtype=np.float32)
    if coefficients.shape[0] != 1 or intercepts.shape[0] != 1:
        raise ValueError("현재 v3 export는 이진 로지스틱 회귀만 지원합니다.")

    spec = proto.Model_pb2.Model()
    spec.specificationVersion = ct.SPECIFICATION_VERSION
    set_classifier_interface_params(
        spec,
        [("embedding", datatypes.Array(embedding_dimension))],
        [NEGATIVE_LABEL, POSITIVE_LABEL],
        "glmClassifier",
        output_features=[
            ("label", datatypes.String()),
            ("labelProbabilities", datatypes.Dictionary(datatypes.String())),
        ],
    )

    glm_classifier = spec.glmClassifier
    glm_classifier.classEncoding = glm_classifier.OneVsRest
    glm_classifier.postEvaluationTransform = glm_classifier.Logit
    glm_classifier.offset.append(float(intercepts[0]))

    weights_row = glm_classifier.weights.add()
    for value in coefficients[0]:
        weights_row.value.append(float(value))

    spec.description.metadata.shortDescription = (
        "SpamKiller v3 embedding classifier. Input must be a normalized embedding vector."
    )
    spec.description.metadata.author = "Codex"
    spec.description.metadata.versionString = "3.0"
    spec.description.metadata.userDefined["input_format"] = (
        "MLMultiArray float embedding produced by the configured sentence-transformers model."
    )
    spec.description.metadata.userDefined["positive_label"] = POSITIVE_LABEL
    spec.description.metadata.userDefined["negative_label"] = NEGATIVE_LABEL

    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_spec(spec, str(output_path))


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
    mlmodel_path = output_dir / "SpamKillerEmbeddingClassifier.mlmodel"

    joblib.dump(classifier, model_path)
    export_coreml_classifier(classifier, artifacts.embedding_dimension, mlmodel_path)

    save_json(
        config_path,
        {
            "model_type": "embedding_plus_logistic_regression_coreml_classifier",
            "embedding_model": embedding_model_name,
            "embedding_dimension": artifacts.embedding_dimension,
            "negative_label": NEGATIVE_LABEL,
            "positive_label": POSITIVE_LABEL,
            "classifier_artifact": str(model_path),
            "mlmodel_artifact": str(mlmodel_path),
            "notes": [
                "이 버전은 실제 Core ML .mlmodel 파일을 생성합니다.",
                "다만 .mlmodel 입력은 원문 문자열이 아니라 임베딩 벡터입니다.",
                "실제 앱 배포에서는 같은 임베딩 모델로 먼저 벡터를 만든 뒤 이 mlmodel에 넣어야 합니다.",
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

    embedding_model = build_embedding_model(
        args.embedding_model,
        local_files_only=args.local_files_only,
    )

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
    print(f"Saved Core ML model to {args.output_dir / 'SpamKillerEmbeddingClassifier.mlmodel'}")
    if validation_rows:
        print(f"Validation accuracy: {validation_metrics['accuracy']}")


if __name__ == "__main__":
    main()
