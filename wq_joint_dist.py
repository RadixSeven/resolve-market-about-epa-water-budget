#!/usr/bin/env python3
"""Show the joint distribution of water_quality_relevance_certainty and water_quality_relevance."""

import json
import sys
from collections import Counter


def extract_pairs(obj):
    """Recursively find all (certainty, relevance) pairs in the JSON."""
    pairs = []
    if isinstance(obj, dict):
        if "water_quality_relevance_certainty" in obj and "water_quality_relevance" in obj:
            pairs.append((obj["water_quality_relevance_certainty"], obj["water_quality_relevance"]))
        for v in obj.values():
            pairs.extend(extract_pairs(v))
    elif isinstance(obj, list):
        for item in obj:
            pairs.extend(extract_pairs(item))
    return pairs


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <json-file> [json-file ...]", file=sys.stderr)
        sys.exit(1)

    counts = Counter()
    for path in sys.argv[1:]:
        with open(path) as f:
            data = json.load(f)
        for certainty, relevance in extract_pairs(data):
            counts[(certainty, relevance)] += 1

    for (certainty, relevance), count in sorted(counts.items()):
        print(f"{count} certainty: {certainty} relevance: {relevance}")


if __name__ == "__main__":
    main()
