from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import sys
import tempfile
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data"
DATASET_PATH = DATA_DIR / "test.csv"
TMPDIR_PATH = ROOT / "benchmarks" / ".tmp"
DEFAULT_OUTPUT_JSON = ROOT / "benchmarks" / "last_benchmark.json"
LABELS = ("ham", "spam")
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"

V0_MODEL_PATH = ROOT / "v0_default" / "artifacts" / "SpamKitMLV1.mlmodel"
V1_MODEL_PATH = ROOT / "v1_sparse_linear" / "artifacts" / "SpamKillerPyTextClassifier.mlmodel"
V3_MODEL_PATH = ROOT / "v3_embedding_coreml" / "artifacts" / "SpamKillerEmbeddingClassifier.mlmodel"
V3_CONFIG_PATH = ROOT / "v3_embedding_coreml" / "artifacts" / "config.json"
V4_MODEL_PATH = ROOT / "v4_char_cnn_coreml" / "artifacts" / "SpamKillerCharCNN.mlpackage"
V4_CONFIG_PATH = ROOT / "v4_char_cnn_coreml" / "artifacts" / "config.json"
V4_VOCAB_PATH = ROOT / "v4_char_cnn_coreml" / "artifacts" / "vocab.json"
PROJECT_VENV_PYTHON = ROOT / ".venv" / "bin" / "python"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="v0, v1, v3, v4 mlmodel 벤치마크를 실행하고 결과를 JSON으로 출력합니다."
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=DEFAULT_OUTPUT_JSON,
        help="결과 JSON을 저장할 경로 (기본값: benchmarks/last_benchmark.json)",
    )
    return parser.parse_args()


@dataclass
class BenchmarkResult:
    model_name: str
    status: str
    accuracy: float | None
    samples: int
    avg_latency_ms: float | None
    p95_latency_ms: float | None
    details: str


def configure_temp_paths() -> None:
    TMPDIR_PATH.mkdir(parents=True, exist_ok=True)
    resolved = str(TMPDIR_PATH.resolve())
    os.environ["TMPDIR"] = resolved
    os.environ["TEMP"] = resolved
    os.environ["TMP"] = resolved
    tempfile.tempdir = resolved


def load_dataset(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip().lower()
            if text and label in LABELS:
                rows.append((text, label))
    return rows


def percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int((len(sorted_values) - 1) * ratio)
    return sorted_values[index]


def encode_char_text(text: str, vocab: dict[str, int], max_length: int) -> list[int]:
    encoded = [vocab.get(char, vocab[UNK_TOKEN]) for char in text[:max_length]]
    if len(encoded) < max_length:
        encoded.extend([vocab[PAD_TOKEN]] * (max_length - len(encoded)))
    return encoded


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def current_python_hint() -> str:
    current = Path(sys.executable).resolve()
    if PROJECT_VENV_PYTHON.exists() and current != PROJECT_VENV_PYTHON.resolve():
        return (
            "현재 인터프리터에는 필요한 패키지가 없을 수 있습니다. "
            f"권장 실행: {PROJECT_VENV_PYTHON} {Path(__file__).resolve()}"
        )
    return f"현재 인터프리터: {current}"


def missing_dependency_result(model_name: str, package_name: str) -> BenchmarkResult:
    return BenchmarkResult(
        model_name=model_name,
        status="skipped",
        accuracy=None,
        samples=0,
        avg_latency_ms=None,
        p95_latency_ms=None,
        details=f"{package_name} not installed. {current_python_hint()}",
    )


def summarize(model_name: str, latencies_ms: list[float], expected: list[str], predicted: list[str]) -> BenchmarkResult:
    correct = sum(1 for a, b in zip(expected, predicted) if a == b)
    accuracy = round(correct / len(expected), 4) if expected else 0.0
    return BenchmarkResult(
        model_name=model_name,
        status="ok",
        accuracy=accuracy,
        samples=len(expected),
        avg_latency_ms=round(statistics.mean(latencies_ms), 3) if latencies_ms else 0.0,
        p95_latency_ms=round(percentile(latencies_ms, 0.95), 3) if latencies_ms else 0.0,
        details="",
    )


def benchmark_v1(rows: list[tuple[str, str]]) -> BenchmarkResult:
    try:
        from coremltools.models import MLModel
    except ImportError:
        return missing_dependency_result("v1_sparse_linear", "coremltools")

    from v1_sparse_linear.train import token_counts

    if not V1_MODEL_PATH.exists():
        return BenchmarkResult("v1_sparse_linear", "skipped", None, 0, None, None, "mlmodel file not found")

    try:
        model = MLModel(str(V1_MODEL_PATH))
        latencies_ms: list[float] = []
        expected: list[str] = []
        predicted: list[str] = []

        for text, label in rows:
            start = time.perf_counter()
            output = model.predict({"token_counts": token_counts(text)})
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            latencies_ms.append(elapsed_ms)
            expected.append(label)
            predicted.append(output["label"])

        return summarize("v1_sparse_linear", latencies_ms, expected, predicted)
    except Exception as error:
        return BenchmarkResult("v1_sparse_linear", "skipped", None, 0, None, None, str(error))


def benchmark_v0(rows: list[tuple[str, str]]) -> BenchmarkResult:
    try:
        from coremltools.models import MLModel
    except ImportError:
        return missing_dependency_result("v0_default", "coremltools")

    if not V0_MODEL_PATH.exists():
        return BenchmarkResult("v0_default", "skipped", None, 0, None, None, "mlmodel file not found")

    try:
        model = MLModel(str(V0_MODEL_PATH))
        latencies_ms: list[float] = []
        expected: list[str] = []
        predicted: list[str] = []

        for text, label in rows:
            start = time.perf_counter()
            output = model.predict({"text": text})
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            latencies_ms.append(elapsed_ms)
            expected.append(label)
            predicted.append(output["label"])

        return summarize("v0_default", latencies_ms, expected, predicted)
    except Exception as error:
        return BenchmarkResult("v0_default", "skipped", None, 0, None, None, str(error))


def benchmark_v3(rows: list[tuple[str, str]]) -> BenchmarkResult:
    try:
        from coremltools.models import MLModel
    except ImportError:
        return missing_dependency_result("v3_embedding_coreml", "coremltools")

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return missing_dependency_result("v3_embedding_coreml", "sentence-transformers")

    if not V3_MODEL_PATH.exists() or not V3_CONFIG_PATH.exists():
        return BenchmarkResult("v3_embedding_coreml", "skipped", None, 0, None, None, "artifacts not found")

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    try:
        payload = json.loads(V3_CONFIG_PATH.read_text(encoding="utf-8"))
        embedding_model = SentenceTransformer(payload["embedding_model"], local_files_only=True)
        model = MLModel(str(V3_MODEL_PATH))

        latencies_ms: list[float] = []
        expected: list[str] = []
        predicted: list[str] = []

        for text, label in rows:
            start = time.perf_counter()
            vector = embedding_model.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0]
            output = model.predict({"embedding": vector})
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            latencies_ms.append(elapsed_ms)
            expected.append(label)
            predicted.append(output["label"])

        return summarize("v3_embedding_coreml", latencies_ms, expected, predicted)
    except Exception as error:
        return BenchmarkResult("v3_embedding_coreml", "skipped", None, 0, None, None, str(error))


def benchmark_v4(rows: list[tuple[str, str]]) -> BenchmarkResult:
    try:
        from coremltools.models import MLModel
    except ImportError:
        MLModel = None

    if not V4_MODEL_PATH.exists() or not V4_CONFIG_PATH.exists() or not V4_VOCAB_PATH.exists():
        return BenchmarkResult("v4_char_cnn_coreml", "skipped", None, 0, None, None, "mlmodel file not found")

    try:
        config = json.loads(V4_CONFIG_PATH.read_text(encoding="utf-8"))
        vocab = json.loads(V4_VOCAB_PATH.read_text(encoding="utf-8"))
        latencies_ms: list[float] = []
        expected: list[str] = []
        predicted: list[str] = []
        runtime_label = "coreml"

        model = None
        if MLModel is not None:
            try:
                model = MLModel(str(V4_MODEL_PATH))
            except Exception:
                model = None

        pytorch_predict = None
        if model is None:
            try:
                from v4_char_cnn_coreml.predict import predict_with_pytorch

                pytorch_predict = predict_with_pytorch
                runtime_label = "pytorch-fallback"
            except ImportError:
                return missing_dependency_result("v4_char_cnn_coreml", "coremltools or torch")

        for text, label in rows:
            start = time.perf_counter()
            char_ids = encode_char_text(text, vocab, config["max_length"])
            if model is not None:
                try:
                    output = model.predict({"char_ids": [char_ids]})
                    spam_probability = sigmoid(float(output["logits"][0]))
                    predicted_label = (
                        config["positive_label"] if spam_probability >= 0.5 else config["negative_label"]
                    )
                except Exception:
                    if pytorch_predict is None:
                        try:
                            from v4_char_cnn_coreml.predict import predict_with_pytorch

                            pytorch_predict = predict_with_pytorch
                            runtime_label = "pytorch-fallback"
                        except ImportError:
                            raise
                    predicted_label, _ = pytorch_predict(char_ids, config)
            else:
                predicted_label, _ = pytorch_predict(char_ids, config)
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            latencies_ms.append(elapsed_ms)
            expected.append(label)
            predicted.append(predicted_label)

        result = summarize("v4_char_cnn_coreml", latencies_ms, expected, predicted)
        result.details = runtime_label
        return result
    except Exception as error:
        return BenchmarkResult("v4_char_cnn_coreml", "skipped", None, 0, None, None, str(error))


def main() -> None:
    args = parse_args()
    configure_temp_paths()
    rows = load_dataset(DATASET_PATH)
    if not rows:
        raise SystemExit(f"No valid rows found in {DATASET_PATH}")

    results = [
        benchmark_v0(rows),
        benchmark_v1(rows),
        benchmark_v3(rows),
        benchmark_v4(rows),
    ]

    payload = {
        "dataset": str(DATASET_PATH),
        "samples": len(rows),
        "label_distribution": dict(Counter(label for _, label in rows)),
        "results": [
            {
                "model_name": result.model_name,
                "status": result.status,
                "accuracy": result.accuracy,
                "samples": result.samples,
                "avg_latency_ms": result.avg_latency_ms,
                "p95_latency_ms": result.p95_latency_ms,
                "details": result.details,
            }
            for result in results
        ],
    }
    output_text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(output_text)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(output_text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
