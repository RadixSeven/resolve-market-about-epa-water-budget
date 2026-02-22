Write a Python program that reads from `epa_fy2025_hr1968_div_a_title_vii.json`
and `epa_fy2026_hr6938_div_b_title_ii.json` and samples from distributions of
money allocations to water quality programs, based on the relevance and
certainty classifications in the data.

The program should be self-contained (no local imports). See `wq_joint_dist.py`
for an example of how to traverse the JSON and extract leaf nodes, but
duplicate rather than import that logic so the simulation can be run
stand-alone.

# Sample generation

## Year

To create a sample for a year, the program will sample independently from
each line item (leaf node) in the data for that year. A leaf node is an
item that has no `sub_items` key or whose `sub_items` array is empty.
Only leaf nodes are summed to avoid double-counting with parent totals.

Ignore `transfers_in` and `transfers_out`; they are informational only.
Use the `amount` field as-is.

## Line item

To create a sample for a line-item, it will first sample from a distribution of
the fraction allocated to water quality programs (`frac`), based on the `water_quality_relevance` classification for that line item.

| Value                                    | Distribution      |
|------------------------------------------|-------------------|
| `"for water quality programs"`           | constant=100%     |
| `"partially for water quality programs"` | uniform[1%, 75%]  |
| `"not for water quality programs"`       | constant=0%       |
| `"unknown"`                              | uniform[0%, 100%] |

Then sample from a distribution of certainty, based on the
`water_quality_relevance_certainty` classification for that line item.
I reproduce the table from `EPA-budget-schema.md` here for convenience.

| Value | Meaning                 | Range for sampling |
|-------|-------------------------|--------------------|
| `5`   | Certainty > 99 %        | `(0.99, 1.0]`     |
| `4`   | 90 % < certainty ≤ 99 % | `(0.90, 0.99]`    |
| `3`   | 50 % < certainty ≤ 90 % | `(0.50, 0.90]`    |
| `2`   | 25 % < certainty ≤ 50 % | `(0.25, 0.50]`    |
| `1`   | Certainty ≤ 25 %        | `[0.00, 0.25]`    |

Draw a random number for the certainty using a uniform distribution over
the range indicated by the `water_quality_relevance_certainty` value.
For example, if `water_quality_relevance_certainty` is `3`, then draw a
random number from a uniform distribution over the range `(0.5, 0.9]`.
Note the lower bound for certainty=1 is closed (includes 0).

Next, draw a random number for correctness from uniform[0, 1]. If the
correctness is less than the certainty, then the relevance classification
is correct. Add `frac * amount` to the total for water quality programs
(where `amount` is the amount allocated to that line item). If the
correctness is greater than the certainty, then the relevance
classification is incorrect. Add `(1-frac) * amount` to the total for
water quality programs.

(This binary flip is a first-pass model for simplicity. If the conclusion
is robust to this level of uncertainty, finer modeling is unnecessary.)

## Fraction cut

Once you've sampled each year, you'll have a total for the year allocated
to water quality programs. The fraction cut is
`(amount_2026 - amount_2025) / amount_2025`. It is OK if this is negative
(indicating an increase in funding for water quality programs).

# Command line

The program should accept command-line arguments (e.g. via `argparse`) for:
the number of samples to generate, an optional random seed (default
20266938), and an optional output file path (default `epa_cut_samples.csv`).

The results should be a CSV file with the following columns:
"2026 amount", "2025 amount", and "Percent cut". ("Percent cut" is just
fraction cut times 100, no percent sign is needed.)

After generating the samples, it will give the mean, standard deviation, and
a 97% credible interval for the "Percent cut" column.

It will also give the percent of the time the amount cut was >= 10%.