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
sample_year, a line item named `name` is given a given fraction of the budget
allocated to water quality programs (`frac`) then, when the other year attempts
to sample a line item with the same name, it should be given the same fraction
but multiplied by that year's amound. For example, suppose that in 2025, there
is a line item named "Clean Water Act grants" and 80% of its funding is
allocated to water quality programs. If its "amount" is $100, then it would add
$80 to the total for water quality programs. If 2026 contains a line item named
"Clean Water Act grants" should also have 80% of its funding allocated to water
quality programs. If its amount is $200, then it would add $160 to the total for
water quality programs in 2026. This way, the fraction of funding for water
quality programs remains consistent for items with the same name across
different years.

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