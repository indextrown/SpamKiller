from __future__ import annotations

import csv
import json
import math
import random
import re
import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT.parent / "data"
DEFAULT_DATASET = DATA_DIR / "train.csv"
DEFAULT_VALIDATION_DATASET = DATA_DIR / "validation.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts"
TOKEN_PATTERN = re.compile(r"[가-힣A-Za-z0-9]+")
LABELS = ("ham", "spam")
NEGATIVE_LABEL = "ham"
POSITIVE_LABEL = "spam"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="희소 토큰 선형 분류기를 학습하고 Core ML .mlmodel을 생성합니다."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--validation-dataset", type=Path, default=DEFAULT_VALIDATION_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--learning-rate", type=float, default=0.03)
    parser.add_argument("--l2-penalty", type=float, default=0.0001)
    return parser.parse_args()


def tokenize(text: str) -> list[str]:
    lowered = text.lower().strip()
    tokens = TOKEN_PATTERN.findall(lowered)
    joined = lowered.replace(" ", "")
    for size in (2, 3):
        if len(joined) >= size:
            tokens.extend(joined[index : index + size] for index in range(len(joined) - size + 1))
    return tokens


def token_counts(text: str) -> dict[str, float]:
    counts = Counter(tokenize(text))
    return {token: float(count) for token, count in counts.items()}


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
    rows: list[tuple[str, str]], train_ratio: float = 0.8
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    shuffled = rows[:]
    random.Random(42).shuffle(shuffled)
    split_index = max(1, min(len(shuffled) - 1, int(len(shuffled) * train_ratio)))
    return shuffled[:split_index], shuffled[split_index:]


def build_vocabulary(rows: list[tuple[str, str]], min_count: int = 1) -> list[str]:
    counts = Counter()
    for text, _ in rows:
        counts.update(tokenize(text))
    return sorted(token for token, count in counts.items() if count >= min_count)


def sigmoid(value: float) -> float:
    clipped = max(min(value, 35.0), -35.0)
    return 1.0 / (1.0 + math.exp(-clipped))


@dataclass
class LinearSpamClassifier:
    feature_names: list[str]
    weights: dict[str, float]
    bias: float
    negative_label: str = NEGATIVE_LABEL
    positive_label: str = POSITIVE_LABEL

    def predict_from_feature_counts(self, features: dict[str, float]) -> tuple[str, dict[str, float]]:
        score = self.bias
        for token, count in features.items():
            score += self.weights.get(token, 0.0) * count

        positive_probability = sigmoid(score)
        probabilities = {
            self.negative_label: 1.0 - positive_probability,
            self.positive_label: positive_probability,
        }
        predicted_label = (
            self.positive_label if positive_probability >= 0.5 else self.negative_label
        )
        return predicted_label, probabilities

    def predict(self, text: str) -> tuple[str, dict[str, float]]:
        return self.predict_from_feature_counts(token_counts(text))

    def to_dict(self) -> dict[str, object]:
        return {
            "feature_names": self.feature_names,
            "weights": self.weights,
            "bias": self.bias,
            "negative_label": self.negative_label,
            "positive_label": self.positive_label,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "LinearSpamClassifier":
        return cls(
            feature_names=[str(value) for value in payload["feature_names"]],
            weights={str(k): float(v) for k, v in dict(payload["weights"]).items()},
            bias=float(payload["bias"]),
            negative_label=str(payload.get("negative_label", NEGATIVE_LABEL)),
            positive_label=str(payload.get("positive_label", POSITIVE_LABEL)),
        )


def train_model(
    rows: list[tuple[str, str]],
    epochs: int = 80,
    learning_rate: float = 0.03,
    l2_penalty: float = 0.0001,
) -> LinearSpamClassifier:
    feature_names = build_vocabulary(rows)
    weights = {feature_name: 0.0 for feature_name in feature_names}
    bias = 0.0
    rng = random.Random(42)
    encoded_rows = [(token_counts(text), label) for text, label in rows]
    label_counts = Counter(label for _, label in rows)
    positive_weight = (
        label_counts[NEGATIVE_LABEL] / label_counts[POSITIVE_LABEL]
        if label_counts[POSITIVE_LABEL]
        else 1.0
    )

    for epoch in range(epochs):
        rng.shuffle(encoded_rows)
        step_size = learning_rate / (1.0 + epoch * 0.08)

        for features, label in encoded_rows:
            if not features:
                continue

            target = 1.0 if label == POSITIVE_LABEL else 0.0
            score = bias
            for token, count in features.items():
                score += weights.get(token, 0.0) * count

            probability = sigmoid(score)
            error = probability - target
            if target == 1.0:
                error *= positive_weight

            for token, count in features.items():
                weights[token] -= step_size * (error * count + l2_penalty * weights[token])

            bias -= step_size * error

    return LinearSpamClassifier(feature_names=feature_names, weights=weights, bias=bias)


def evaluate(model: LinearSpamClassifier, rows: list[tuple[str, str]]) -> dict[str, float | int]:
    if not rows:
        return {"accuracy": 0.0, "samples": 0}

    correct = 0
    per_label_total = Counter()
    per_label_correct = Counter()

    for text, expected in rows:
        predicted, _ = model.predict(text)
        per_label_total[expected] += 1
        if predicted == expected:
            correct += 1
            per_label_correct[expected] += 1

    metrics: dict[str, float | int] = {
        "accuracy": round(correct / len(rows), 4),
        "samples": len(rows),
    }
    for label in LABELS:
        total = per_label_total[label]
        metrics[f"{label}_recall"] = round(per_label_correct[label] / total, 4) if total else 0.0
    return metrics


def save_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def export_coreml_model(model: LinearSpamClassifier, output_path: Path) -> None:
    import coremltools as ct
    from coremltools import proto
    from coremltools.models import datatypes
    from coremltools.models._interface_management import (
        set_classifier_interface_params,
        set_transform_interface_params,
    )
    from coremltools.models.feature_vectorizer import create_feature_vectorizer
    from coremltools.models.pipeline import PipelineClassifier
    from coremltools.models.utils import save_spec

    input_name = "token_counts"
    sparse_name = "__sparse_vector_features__"
    dense_name = "__dense_features__"

    pipeline = PipelineClassifier(
        input_features=[(input_name, datatypes.Dictionary(datatypes.String()))],
        class_labels=[model.negative_label, model.positive_label],
        output_features=[
            ("label", datatypes.String()),
            ("labelProbabilities", datatypes.Dictionary(datatypes.String())),
        ],
    )

    dict_vectorizer_spec = proto.Model_pb2.Model()
    dict_vectorizer_spec.specificationVersion = ct.SPECIFICATION_VERSION
    for feature_name in model.feature_names:
        dict_vectorizer_spec.dictVectorizer.stringToIndex.vector.append(feature_name)
    set_transform_interface_params(
        dict_vectorizer_spec,
        [(input_name, datatypes.Dictionary(datatypes.String()))],
        [(sparse_name, datatypes.Dictionary(key_type=int))],
    )
    pipeline.add_model(dict_vectorizer_spec)

    feature_vectorizer_spec, _ = create_feature_vectorizer(
        [(sparse_name, datatypes.Dictionary(key_type=int))],
        dense_name,
        {sparse_name: len(model.feature_names)},
    )
    pipeline.add_model(feature_vectorizer_spec)

    classifier_spec = proto.Model_pb2.Model()
    classifier_spec.specificationVersion = ct.SPECIFICATION_VERSION
    set_classifier_interface_params(
        classifier_spec,
        [(dense_name, datatypes.Array(len(model.feature_names)))],
        [model.negative_label, model.positive_label],
        "glmClassifier",
        output_features=[
            ("label", datatypes.String()),
            ("labelProbabilities", datatypes.Dictionary(datatypes.String())),
        ],
    )

    glm_classifier = classifier_spec.glmClassifier
    glm_classifier.classEncoding = glm_classifier.OneVsRest
    glm_classifier.postEvaluationTransform = glm_classifier.Logit
    glm_classifier.offset.append(model.bias)

    weights_row = glm_classifier.weights.add()
    for feature_name in model.feature_names:
        weights_row.value.append(model.weights.get(feature_name, 0.0))

    pipeline.add_model(classifier_spec)

    pipeline.spec.description.metadata.shortDescription = (
        "SpamKiller Python text classifier. Input must be token_counts dictionary."
    )
    pipeline.spec.description.metadata.author = "Codex"
    pipeline.spec.description.metadata.versionString = "1.0"
    pipeline.spec.description.metadata.userDefined["input_format"] = (
        "Dictionary<String, Double> token_counts generated with v1_sparse_linear/tokenize() rules."
    )
    pipeline.spec.description.metadata.userDefined["positive_label"] = model.positive_label
    pipeline.spec.description.metadata.userDefined["negative_label"] = model.negative_label

    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_spec(pipeline.spec, str(output_path))


def main() -> None:
    args = parse_args()
    dataset_path = args.dataset
    validation_path = args.validation_dataset
    output_dir = args.output_dir

    train_rows = load_dataset(dataset_path)
    validation_rows = load_dataset(validation_path) if validation_path.exists() else []
    model = train_model(
        train_rows,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        l2_penalty=args.l2_penalty,
    )
    train_metrics = evaluate(model, train_rows)
    validation_metrics = evaluate(model, validation_rows)

    model_json_path = output_dir / "model.json"
    metrics_json_path = output_dir / "metrics.json"
    mlmodel_path = output_dir / "SpamKillerPyTextClassifier.mlmodel"

    save_json(
        model_json_path,
        {
            "dataset": str(dataset_path),
            "validation_dataset": str(validation_path),
            "labels": LABELS,
            "model_type": "linear_logistic_regression",
            "hyperparameters": {
                "epochs": args.epochs,
                "learning_rate": args.learning_rate,
                "l2_penalty": args.l2_penalty,
            },
            "model": model.to_dict(),
        },
    )
    save_json(
        metrics_json_path,
        {
            "train": train_metrics,
            "validation": validation_metrics,
            "train_samples": len(train_rows),
            "validation_samples": len(validation_rows),
        },
    )

    print(f"Saved model to {model_json_path}")
    print(f"Saved metrics to {metrics_json_path}")
    if validation_rows:
        print(f"Validation accuracy: {validation_metrics['accuracy']}")

    try:
        export_coreml_model(model, mlmodel_path)
        print(f"Saved Core ML model to {mlmodel_path}")
    except Exception as error:
        print(f"Skipped Core ML export: {error}")


if __name__ == "__main__":
    main()
