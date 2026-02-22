#!/usr/bin/env python3
"""Show the joint distribution of water_quality_relevance_certainty and water_quality_relevance for line items."""

import json
import sys
from collections import Counter
from collections.abc import Generator

type JsonValue = None | bool | int | float | str | list[JsonValue] | JsonObject
type JsonObject = dict[str, JsonValue]

def extract_pairs(obj: JsonValue) -> Generator[tuple[int, str], None, None]:
    """Recursively find all (certainty, relevance) pairs in the JSON."""
    if isinstance(obj, dict):
        if "water_quality_relevance_certainty" in obj and "water_quality_relevance" in obj and "sub_items" not in obj:
            yield obj["water_quality_relevance_certainty"], obj["water_quality_relevance"]
        for v in obj.values():
            yield from extract_pairs(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from extract_pairs(item)
    return None



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
    for (relevance, certainty), count in sorted(counts.items(), key=lambda x: (x[0][0], -x[0][1])):
        print(f"|{relevance:{max_relevance_len}}| {certainty} | {count:2} |")


if __name__ == "__main__":
    main()
