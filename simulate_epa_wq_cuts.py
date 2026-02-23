#!/usr/bin/env python3
"""Monte Carlo simulation of EPA water quality budget allocations to assess cuts.

Reads FY2025 and FY2026 EPA budget JSON files, samples from distributions
of water quality relevance and certainty for each line item, and computes
the percent change in water quality funding between the two years.
"""

import argparse
import csv
import json
import math
import random
import sys
from collections.abc import Generator
from pathlib import Path

type JsonValue = None | bool | int | float | str | list[JsonValue] | JsonObject
type JsonObject = dict[str, JsonValue]

# ---------------------------------------------------------------------------
# JSON traversal — duplicated from wq_joint_dist.py so this script is
# self-contained.
# ---------------------------------------------------------------------------

def extract_leaf_nodes(obj: JsonValue) -> Generator[JsonObject, None, None]:
    """Recursively yield leaf-node dicts (items with no sub_items)."""
    if isinstance(obj, dict):
        subs = obj.get("sub_items")
        if (not subs) and "water_quality_relevance" in obj:
            yield obj
        for v in obj.values():
            yield from extract_leaf_nodes(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from extract_leaf_nodes(item)


# ---------------------------------------------------------------------------
# Sampling helpers
# ---------------------------------------------------------------------------

def sample_frac(relevance: str, rng: random.Random) -> float:
    """Sample the fraction allocated to water quality based on relevance."""
    if relevance == "for water quality programs":
        return 1.0
    elif relevance == "partially for water quality programs":
        return rng.uniform(0.01, 0.75)
    elif relevance == "not for water quality programs":
        return 0.0
    elif relevance == "unknown":
        return rng.uniform(0.0, 1.0)
    else:
        raise ValueError(f"Unexpected water_quality_relevance: {relevance!r}")


def sample_certainty(cert_level: int, rng: random.Random) -> float:
    """Sample a certainty probability from the range for the given level."""
    if cert_level == 5:
        return rng.uniform(0.99, 1.0)
    elif cert_level == 4:
        return rng.uniform(0.90, 0.99)
    elif cert_level == 3:
        return rng.uniform(0.50, 0.90)
    elif cert_level == 2:
        return rng.uniform(0.25, 0.50)
    elif cert_level == 1:
        return rng.uniform(0.00, 0.25)
    else:
        raise ValueError(f"Unexpected certainty level: {cert_level!r}")


def sample_year(data: JsonValue, rng: random.Random) -> float:
    """Return a single sampled total for water quality programs for one year."""
    total: float = 0.0
    for leaf in extract_leaf_nodes(data):
        amount: float = leaf["amount"]
        relevance: str = leaf["water_quality_relevance"]
        cert_level: int = leaf["water_quality_relevance_certainty"]

        frac: float = sample_frac(relevance, rng)
        certainty: float = sample_certainty(cert_level, rng)
        correctness: float = rng.random()

        if correctness < certainty:
            total += frac * amount
        else:
            total += (1 - frac) * amount

    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Monte Carlo simulation of EPA water quality budget cuts."
    )
    parser.add_argument(
        "-n", "--num-samples",
        type=int,
        default=10000,
        help="Number of Monte Carlo samples (default: 10000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20266938,
        help="Random seed (default: 20266938)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="epa_cut_samples.csv",
        help="Output CSV file path (default: epa_cut_samples.csv)",
    )
    args: argparse.Namespace = parser.parse_args()

    base: Path = Path(__file__).resolve().parent

    with open(base / "epa_fy2025_hr1968_div_a_title_vii.json") as f:
        data_2025: JsonValue = json.load(f)
    with open(base / "epa_fy2026_hr6938_div_b_title_ii.json") as f:
        data_2026: JsonValue = json.load(f)

    rng: random.Random = random.Random(args.seed)

    samples: list[tuple[float, float, float]] = []
    for _ in range(args.num_samples):
        amt_2025: float = sample_year(data_2025, rng)
        amt_2026: float = sample_year(data_2026, rng)
        if amt_2025 == 0:
            pct_cut: float = 0.0
        else:
            pct_cut = (amt_2026 - amt_2025) / amt_2025 * 100.0
        samples.append((amt_2026, amt_2025, pct_cut))

    # Write CSV
    with open(args.output, "w", newline="") as f:
        writer: csv.writer[str] = csv.writer(f)
        writer.writerow(["2026 amount", "2025 amount", "Percent cut"])
        for row in samples:
            writer.writerow(row)

    # Summary statistics
    pcts: list[float] = [s[2] for s in samples]
    n: int = len(pcts)
    mean: float = sum(pcts) / n
    variance: float = sum((p - mean) ** 2 for p in pcts) / (n - 1)
    std: float = math.sqrt(variance)

    pcts_sorted: list[float] = sorted(pcts)
    lo_idx: int = int(math.floor(0.015 * n))
    hi_idx: int = int(math.ceil(0.985 * n)) - 1
    ci_lo: float = pcts_sorted[lo_idx]
    ci_hi: float = pcts_sorted[hi_idx]

    pct_ge_10: float = sum(1 for p in pcts if p <= -10.0) / n * 100.0

    print(f"Samples: {n}")
    print(f"Mean percent change: {mean:.2f}%")
    print(f"Std dev: {std:.2f}%")
    print(f"97% credible interval: [{ci_lo:.2f}%, {ci_hi:.2f}%]")
    print(f"Percent of samples with >= 10% cut: {pct_ge_10:.1f}%")
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
