#!/usr/bin/env python3
"""Show the joint distribution of water_quality_relevance_certainty and water_quality_relevance."""

import json
import sys
from collections import Counter


type JsonValue = None | bool | int | float | str | list[JsonValue] | JsonObject
type JsonObject = dict[str, JsonValue]

def extract_pairs(obj: JsonValue) -> list[tuple[int, str]]:
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


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <json-file> [json-file ...]", file=sys.stderr)
        sys.exit(1)

    max_relevance_len = 0
    counts = Counter()
    for path in sys.argv[1:]:
        with open(path) as f:
            data = json.load(f)
        for certainty, relevance in extract_pairs(data):
            max_relevance_len = max(max_relevance_len, len(relevance))
            counts[(relevance, certainty, )] += 1

    print("|Relevance|Certainty|Count|")
    print("|---|---|---|")
    for (relevance, certainty), count in sorted(counts.items(), key=lambda x: (-x[1], x[0][1], x[0][0])):
        print(f"|{relevance:{max_relevance_len}}| {certainty} | {count:2} |")


if __name__ == "__main__":
    main()
