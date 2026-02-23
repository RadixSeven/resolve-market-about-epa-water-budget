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
from typing import NamedTuple

type JsonValue = None | bool | int | float | str | list[JsonValue] | JsonObject
type JsonObject = dict[str, JsonValue]

type Classification = str
class CumulativeEntry(NamedTuple):
    cumulative_count: int
    classification: Classification


class ItemInfo(NamedTuple):
    amount_2025: float
    amount_2026: float
    relevance: str
    certainty: int


type ReclassificationTable = list[CumulativeEntry]
type ReclassifyTables = dict[Classification, ReclassificationTable]

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


def count_relevance_classes(*datasets: JsonValue) -> dict[Classification, int]:
    """Count occurrences of each water_quality_relevance across all datasets."""
    counts: dict[Classification, int] = {}
    for data in datasets:
        for leaf in extract_leaf_nodes(data):
            cls: Classification = leaf["water_quality_relevance"]
            counts[cls] = counts.get(cls, 0) + 1
    return counts


def build_reclassify_tables(counts: dict[Classification, int]) -> ReclassifyTables:
    """Build a cumulative reclassification table for each classification.

    For each classification, the table contains cumulative counts of all
    *other* classifications, so we can sample a replacement when the
    original classification is deemed incorrect.
    """
    tables: ReclassifyTables = {}
    for excluded in counts:
        table: ReclassificationTable = []
        cumulative: int = 0
        for cls, count in counts.items():
            if cls == excluded:
                continue
            cumulative += count
            table.append(CumulativeEntry(cumulative, cls))
        tables[excluded] = table
    return tables


def sample_reclassification(
    table: ReclassificationTable, rng: random.Random
) -> Classification:
    """Pick a replacement classification from a cumulative table."""
    total: int = table[-1].cumulative_count
    pick: int = rng.randint(0, total - 1)
    for entry in table:
        if pick < entry.cumulative_count:
            return entry.classification
    return table[-1].classification  # unreachable, satisfies type checker


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


def sample_year(
    data: JsonValue,
    rng: random.Random,
    reclassify_tables: ReclassifyTables,
    name_to_frac: dict[str, float],
) -> float:
    """Return a single sampled total for water quality programs for one year.

    Args:
        data: The JSON data for the year as dicts
        rng: The random number generator for sampling
        reclassify_tables: The precomputed reclassification tables for sampling
            new classifications when the original is deemed incorrect.
        name_to_frac: A dict mapping line item names to their sampled fraction
            of funding allocated to water quality. This ensures that the same
            program gets the same fraction across different years.

    Returns:
        A sample from the distribution of total water quality funding for the
        year represented by `data`.
    """
    total: float = 0.0
    for leaf in extract_leaf_nodes(data):
        amount: float = leaf["amount"]
        name: str = leaf["name"]

        if name in name_to_frac:
            total += name_to_frac[name] * amount
            continue

        relevance: Classification = leaf["water_quality_relevance"]
        cert_level: int = leaf["water_quality_relevance_certainty"]

        certainty: float = sample_certainty(cert_level, rng)
        correctness: float = rng.random()

        if correctness >= certainty:
            relevance = sample_reclassification(
                reclassify_tables[relevance], rng
            )

        frac: float = sample_frac(relevance, rng)
        name_to_frac[name] = frac

        total += frac * amount

    return total


# ---------------------------------------------------------------------------
# Uncertainty report
# ---------------------------------------------------------------------------

def build_item_info(data_2025: JsonValue, data_2026: JsonValue) -> dict[str, ItemInfo]:
    """Build a mapping of item name to metadata from both years' JSON trees."""
    amounts_2025: dict[str, float] = {}
    relevance_2025: dict[str, str] = {}
    certainty_2025: dict[str, int] = {}
    for leaf in extract_leaf_nodes(data_2025):
        name: str = leaf["name"]
        amounts_2025[name] = leaf["amount"]
        relevance_2025[name] = leaf["water_quality_relevance"]
        certainty_2025[name] = leaf["water_quality_relevance_certainty"]

    amounts_2026: dict[str, float] = {}
    relevance_2026: dict[str, str] = {}
    certainty_2026: dict[str, int] = {}
    for leaf in extract_leaf_nodes(data_2026):
        name = leaf["name"]
        amounts_2026[name] = leaf["amount"]
        relevance_2026[name] = leaf["water_quality_relevance"]
        certainty_2026[name] = leaf["water_quality_relevance_certainty"]

    all_names = set(amounts_2025) | set(amounts_2026)
    info: dict[str, ItemInfo] = {}
    for name in all_names:
        info[name] = ItemInfo(
            amount_2025=amounts_2025.get(name, 0.0),
            amount_2026=amounts_2026.get(name, 0.0),
            relevance=relevance_2025.get(name, relevance_2026.get(name, "unknown")),
            certainty=certainty_2025.get(name, certainty_2026.get(name, 0)),
        )
    return info


def write_uncertainty_report(
    path: str,
    item_info: dict[str, ItemInfo],
    frac_samples: dict[str, list[float]],
) -> None:
    """Write a CSV ranking items by their contribution to overall variance."""
    rows: list[dict[str, object]] = []
    for name, info in item_info.items():
        fracs = frac_samples[name]
        n = len(fracs)
        mean_frac = sum(fracs) / n
        var_frac = sum((f - mean_frac) ** 2 for f in fracs) / (n - 1) if n > 1 else 0.0
        std_frac = math.sqrt(var_frac)
        net_amount = info.amount_2025 - info.amount_2026
        var_contribution = var_frac * net_amount ** 2
        std_contribution = math.sqrt(var_contribution)
        rows.append({
            "name": name,
            "amount_2025": info.amount_2025,
            "amount_2026": info.amount_2026,
            "net_amount": net_amount,
            "relevance": info.relevance,
            "certainty": info.certainty,
            "mean_frac": mean_frac,
            "std_frac": std_frac,
            "var_contribution": var_contribution,
            "std_contribution": std_contribution,
        })

    total_var = sum(r["var_contribution"] for r in rows)
    for r in rows:
        r["pct_of_total_var"] = (
            r["var_contribution"] / total_var * 100.0 if total_var > 0 else 0.0
        )

    rows.sort(key=lambda r: r["var_contribution"], reverse=True)

    fieldnames = [
        "name", "amount_2025", "amount_2026", "net_amount",
        "relevance", "certainty", "mean_frac", "std_frac",
        "var_contribution", "std_contribution", "pct_of_total_var",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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
    parser.add_argument(
        "--uncertainty-report",
        type=str,
        default="uncertainty_report.csv",
        help="Output CSV file path for uncertainty contribution report (default: uncertainty_report.csv)",
    )
    args: argparse.Namespace = parser.parse_args()

    base: Path = Path(__file__).resolve().parent

    with open(base / "epa_fy2025_hr1968_div_a_title_vii.json") as f:
        data_2025: JsonValue = json.load(f)
    with open(base / "epa_fy2026_hr6938_div_b_title_ii.json") as f:
        data_2026: JsonValue = json.load(f)

    item_info: dict[str, ItemInfo] = build_item_info(data_2025, data_2026)

    counts: dict[Classification, int] = count_relevance_classes(data_2025, data_2026)
    reclassify_tables: ReclassifyTables = build_reclassify_tables(counts)

    rng: random.Random = random.Random(args.seed)

    frac_samples: dict[str, list[float]] = {name: [] for name in item_info}
    samples: list[tuple[float, float, float]] = []
    for _ in range(args.num_samples):
        name_to_frac: dict[str, float] = {}
        amt_2025 = sample_year(data_2025, rng, reclassify_tables, name_to_frac)
        amt_2026 = sample_year(data_2026, rng, reclassify_tables, name_to_frac)
        pct_cut = 0 if amt_2025 == 0 else (
            amt_2025 - amt_2026) / amt_2025 * 100.0
        samples.append((amt_2026, amt_2025, pct_cut))
        for name in item_info:
            frac_samples[name].append(name_to_frac[name])

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

    pct_ge_10: float = sum(1 for p in pcts if p >= 10.0) / n * 100.0

    print(f"Samples: {n}")
    print(f"Mean percent cut: {mean:.2f}%")
    print(f"Std dev: {std:.2f}%")
    print(f"97% credible interval for cut: [{ci_lo:.2f}%, {ci_hi:.2f}%]")
    print(f"Percent of samples with >= 10% cut: {pct_ge_10:.1f}%")
    print(f"Results written to {args.output}")

    write_uncertainty_report(args.uncertainty_report, item_info, frac_samples)
    print(f"Uncertainty report written to {args.uncertainty_report}")


if __name__ == "__main__":
    main()
