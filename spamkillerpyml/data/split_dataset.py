from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DATASET = ROOT / "sample.csv"
DEFAULT_OUTPUT_DIR = ROOT / "data"
LABELS = ("ham", "spam")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="원본 CSV를 train/validation/test로 stratified split 합니다."
    )
    parser.add_argument("--dataset", type=Path, default=SOURCE_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--validation-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip().lower()
            if text and label in LABELS:
                rows.append({"text": text, "label": label})
    if not rows:
        raise ValueError(f"No valid rows found in {path}")
    return rows


def stratified_split(
    rows: list[dict[str, str]],
    train_ratio: float,
    validation_ratio: float,
    test_ratio: float,
    seed: int,
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["label"]].append(row)

    rng = random.Random(seed)
    train_rows: list[dict[str, str]] = []
    validation_rows: list[dict[str, str]] = []
    test_rows: list[dict[str, str]] = []

    for label in LABELS:
        label_rows = grouped[label][:]
        rng.shuffle(label_rows)
        total = len(label_rows)
        if total == 0:
            continue

        train_count = int(total * train_ratio)
        validation_count = int(total * validation_ratio)

        # Keep at least one sample for test when possible.
        if total >= 3:
            train_count = max(1, train_count)
            validation_count = max(1, validation_count)

        while train_count + validation_count >= total and validation_count > 0:
            validation_count -= 1
        while train_count + validation_count >= total and train_count > 1:
            train_count -= 1

        test_count = total - train_count - validation_count

        train_rows.extend(label_rows[:train_count])
        validation_rows.extend(label_rows[train_count : train_count + validation_count])
        test_rows.extend(label_rows[train_count + validation_count : train_count + validation_count + test_count])

    rng.shuffle(train_rows)
    rng.shuffle(validation_rows)
    rng.shuffle(test_rows)
    return train_rows, validation_rows, test_rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["text", "label"])
        writer.writeheader()
        writer.writerows(rows)


def describe(rows: list[dict[str, str]]) -> dict[str, object]:
    return {
        "samples": len(rows),
        "label_distribution": dict(Counter(row["label"] for row in rows)),
    }


def main() -> None:
    args = parse_args()
    ratio_sum = args.train_ratio + args.validation_ratio + args.test_ratio
    if abs(ratio_sum - 1.0) > 1e-9:
        raise SystemExit("train/validation/test 비율 합은 1.0이어야 합니다.")

    rows = load_rows(args.dataset)
    train_rows, validation_rows, test_rows = stratified_split(
        rows,
        train_ratio=args.train_ratio,
        validation_ratio=args.validation_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )

    write_rows(args.output_dir / "train.csv", train_rows)
    write_rows(args.output_dir / "validation.csv", validation_rows)
    write_rows(args.output_dir / "test.csv", test_rows)

    summary = {
        "source_dataset": str(args.dataset),
        "seed": args.seed,
        "ratios": {
            "train": args.train_ratio,
            "validation": args.validation_ratio,
            "test": args.test_ratio,
        },
        "splits": {
            "train": describe(train_rows),
            "validation": describe(validation_rows),
            "test": describe(test_rows),
        },
    }
    summary_path = args.output_dir / "split_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
