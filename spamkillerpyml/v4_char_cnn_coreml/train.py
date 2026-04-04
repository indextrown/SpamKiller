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
MAX_LENGTH = 128
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="문자 기반 CNN을 학습하고 Core ML .mlmodel 파일을 생성합니다."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--validation-dataset", type=Path, default=DEFAULT_VALIDATION_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=80)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--embedding-dim", type=int, default=64)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=0.03)
    return parser.parse_args()


def load_dataset(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip().lower()
            if text and label in LABELS:
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


def build_vocab(rows: list[tuple[str, str]]) -> dict[str, int]:
    characters = sorted({char for text, _ in rows for char in text})
    vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1}
    for index, char in enumerate(characters, start=2):
        vocab[char] = index
    return vocab


def encode_text(text: str, vocab: dict[str, int], max_length: int = MAX_LENGTH) -> list[int]:
    encoded = [vocab.get(char, vocab[UNK_TOKEN]) for char in text[:max_length]]
    if len(encoded) < max_length:
        encoded.extend([vocab[PAD_TOKEN]] * (max_length - len(encoded)))
    return encoded


def encode_rows(rows: list[tuple[str, str]], vocab: dict[str, int]):
    import torch

    texts = torch.tensor([encode_text(text, vocab) for text, _ in rows], dtype=torch.long)
    labels = torch.tensor([1 if label == POSITIVE_LABEL else 0 for _, label in rows], dtype=torch.float32)
    return texts, labels


class CharCNNClassifier:
    def __init__(self, vocab_size: int, embedding_dim: int, hidden_dim: int):
        import torch.nn as nn

        class Model(nn.Module):
            def __init__(self):
                super().__init__()
                self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
                self.conv = nn.Conv1d(embedding_dim, hidden_dim, kernel_size=5, padding=2)
                self.relu = nn.ReLU()
                self.pool = nn.AdaptiveMaxPool1d(1)
                self.fc = nn.Linear(hidden_dim, 1)

            def forward(self, x):
                embedded = self.embedding(x)
                embedded = embedded.transpose(1, 2)
                features = self.conv(embedded)
                features = self.relu(features)
                pooled = self.pool(features).squeeze(-1)
                logits = self.fc(pooled).squeeze(-1)
                return logits

        self.model = Model()


def build_model_from_config(config: dict[str, object]):
    wrapper = CharCNNClassifier(
        vocab_size=int(config["vocab_size"]),
        embedding_dim=int(config["embedding_dim"]),
        hidden_dim=int(config["hidden_dim"]),
    )
    return wrapper.model


def train_model(
    model,
    train_inputs,
    train_labels,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> None:
    import torch
    import torch.nn as nn

    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.BCEWithLogitsLoss()

    dataset_size = train_inputs.size(0)
    for _ in range(epochs):
        permutation = torch.randperm(dataset_size)
        for start in range(0, dataset_size, batch_size):
            indices = permutation[start : start + batch_size]
            batch_inputs = train_inputs[indices]
            batch_labels = train_labels[indices]

            optimizer.zero_grad()
            logits = model(batch_inputs)
            loss = criterion(logits, batch_labels)
            loss.backward()
            optimizer.step()


def evaluate_model(model, inputs, labels) -> dict[str, float | int]:
    import torch

    with torch.no_grad():
        logits = model(inputs)
        probabilities = torch.sigmoid(logits)
        predictions = (probabilities >= 0.5).long()

    expected = labels.long()
    correct = int((predictions == expected).sum().item())
    samples = int(labels.size(0))

    metrics: dict[str, float | int] = {
        "accuracy": round(correct / samples, 4) if samples else 0.0,
        "samples": samples,
    }

    for label_name, encoded_value in ((NEGATIVE_LABEL, 0), (POSITIVE_LABEL, 1)):
        total = int((expected == encoded_value).sum().item())
        matched = int(((predictions == encoded_value) & (expected == encoded_value)).sum().item())
        metrics[f"{label_name}_recall"] = round(matched / total, 4) if total else 0.0

    return metrics


def export_coreml_model(model, output_path: Path) -> None:
    import coremltools as ct
    import torch

    example_input = torch.zeros((1, MAX_LENGTH), dtype=torch.long)
    traced = torch.jit.trace(model, example_input)
    mlmodel = ct.convert(
        traced,
        convert_to="mlprogram",
        inputs=[ct.TensorType(name="char_ids", shape=example_input.shape, dtype=int)],
        outputs=[ct.TensorType(name="logits")],
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mlmodel.save(str(output_path))


@dataclass
class TrainArtifacts:
    train_metrics: dict[str, float | int]
    test_metrics: dict[str, float | int]
    label_distribution: dict[str, int]


def main() -> None:
    import torch

    args = parse_args()
    train_rows = load_dataset(args.dataset)
    validation_rows = load_dataset(args.validation_dataset) if args.validation_dataset.exists() else []
    vocab = build_vocab(train_rows)

    train_inputs, train_labels = encode_rows(train_rows, vocab)
    validation_inputs, validation_labels = encode_rows(validation_rows, vocab) if validation_rows else (None, None)

    wrapper = CharCNNClassifier(
        vocab_size=len(vocab),
        embedding_dim=args.embedding_dim,
        hidden_dim=args.hidden_dim,
    )
    model = wrapper.model
    model.eval()

    torch.manual_seed(args.seed)
    train_model(
        model,
        train_inputs,
        train_labels,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
    )

    train_metrics = evaluate_model(model, train_inputs, train_labels)
    validation_metrics = (
        evaluate_model(model, validation_inputs, validation_labels)
        if validation_inputs is not None and validation_labels is not None
        else {"accuracy": 0.0, "samples": 0}
    )
    label_distribution = Counter(label for _, label in train_rows + validation_rows)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    vocab_path = args.output_dir / "vocab.json"
    config_path = args.output_dir / "config.json"
    metrics_path = args.output_dir / "metrics.json"
    weights_path = args.output_dir / "weights.pt"
    mlmodel_path = args.output_dir / "SpamKillerCharCNN.mlpackage"

    torch.save(model.state_dict(), weights_path)
    save_json(vocab_path, vocab)
    save_json(
        config_path,
        {
            "model_type": "char_cnn_coreml",
            "max_length": MAX_LENGTH,
            "vocab_size": len(vocab),
            "embedding_dim": args.embedding_dim,
            "hidden_dim": args.hidden_dim,
            "negative_label": NEGATIVE_LABEL,
            "positive_label": POSITIVE_LABEL,
            "weights_artifact": str(weights_path),
            "mlmodel_artifact": str(mlmodel_path),
        },
    )
    save_json(
        metrics_path,
        {
            "train": train_metrics,
            "validation": validation_metrics,
            "label_distribution": dict(label_distribution),
        },
    )
    export_coreml_model(model, mlmodel_path)

    print(f"Saved vocab to {vocab_path}")
    print(f"Saved config to {config_path}")
    print(f"Saved metrics to {metrics_path}")
    print(f"Saved weights to {weights_path}")
    print(f"Saved Core ML model to {mlmodel_path}")
    if validation_rows:
        print(f"Validation accuracy: {validation_metrics['accuracy']}")


if __name__ == "__main__":
    main()
