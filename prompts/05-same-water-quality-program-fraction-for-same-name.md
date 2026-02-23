Please update @simulate_epa_wq_cuts.py to keep the same fraction of the funding
for water quality programs for items with the same name in a given
"Percent cut" sample.

To review the main sampling loop is:

```python
    samples: list[tuple[float, float, float]] = []
    for _ in range(args.num_samples):
        amt_2025: float = sample_year(data_2025, rng, reclassify_tables)
        amt_2026: float = sample_year(data_2026, rng, reclassify_tables)
        if amt_2025 == 0:
            pct_cut: float = 0.0
        else:
            pct_cut = (amt_2025 - amt_2026) / amt_2025 * 100.0
        samples.append((amt_2026, amt_2025, pct_cut))
```

Each loop generates a tuple: amt_2026, amt_2025, pct_cut. If in one run of
sample_year, a line item with a given `name` (i.e. `leaf["name"]`) is assigned a
fraction `frac` of its amount to water quality programs, then when the other
year's call to sample_year encounters a line item with the same name, it should
reuse that same fraction rather than sampling a new one. Inside sample_year, the
logic should be: if `name` is already in `name_to_frac`, use the stored
fraction; otherwise, sample a new fraction (via `sample_frac` and the certainty
calculation as currently implemented) and store it in `name_to_frac` before
using it.

For example, suppose that in 2025 there is a line item named "Clean Water Act
grants" and 80% of its funding is allocated to water quality programs. If its
amount is \$100, then it would add \$80 to the total for water quality programs.
If 2026 contains a line item also named "Clean Water Act grants", it should also
have 80% of its funding allocated to water quality programs. If its amount is
\$200, then it would add \$160 to the total for water quality programs in 2026.
This way, the fraction of funding for water quality programs remains consistent
for items with the same name across different years.

A simple implementation would be to maintain a dictionary that maps line item
names to their fractions:

```python
    samples: list[tuple[float, float, float]] = []
    for _ in range(args.num_samples):
        name_to_frac: dict[str, float] = {}
        amt_2025: float = sample_year(data_2025, rng, reclassify_tables, name_to_frac)
        amt_2026: float = sample_year(data_2026, rng, reclassify_tables, name_to_frac)
        if amt_2025 == 0:
            pct_cut: float = 0.0
        else:
            pct_cut = (amt_2025 - amt_2026) / amt_2025 * 100.0
        samples.append((amt_2026, amt_2025, pct_cut))
```