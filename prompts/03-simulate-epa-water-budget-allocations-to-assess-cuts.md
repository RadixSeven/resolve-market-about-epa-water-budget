Write a program that reads from `epa_fy2025_hr1968_div_a_title_vii.json` and
`epa_fy2026_hr6938_div_b_title_ii.json` and samples from distributions of money
allocations to water quality programs, based on the relevance and certainty
classifications in the data.

# Sample generation

## Year

To create a sample for a year, the program will sample independently from
each line item (leaf node) in the data for that year.

## Line item

To create a sample for a line-item, it will first sample from a distribution of
the fraction allocated to water quality programs (`frac`), based on the `water_quality_relevance` classification for that line item.

| Value                                    | Distribution      |
|------------------------------------------|-------------------|
| `"for water quality programs"`           | constant=100%     |
| `"partially for water quality programs"` | uniform[1%, 75%]  |
| `"not for water quality programs"`       | constant=100%     |
| `"unknown"`                              | uniform[0%, 100%] |

Then sample from a distribution of certainty, based on the
`water_quality_relevance_certainty` classification for that line item.
I reproduce the table from `EPA-budget-schema.md` here for convenience.

| Value | Meaning                 |
|-------|-------------------------|
| `5`   | Certainty > 99 %        |
| `4`   | 90 % < certainty ≤ 99 % |
| `3`   | 50 % < certainty ≤ 90 % |
| `2`   | 25 % < certainty ≤ 50 % |
| `1`   | Certainty ≤ 25 %        |

Draw a random number for the certainty using a uniform distribution over
the range indicated by the `water_quality_relevance_certainty` value.
For example, if `water_quality_relevance_certainty` is `3`, then draw a
random number from a uniform distribution over the range `(0.5, 0.9]`.

Next, draw a random number for correctness. If the correctness is less than the certainty, then the relevance classification is correct. Add `frac * amount`
to the total for water quality programs (where `amount` is the amount allocated
to that line item). If the correctness is greater than the certainty, then the relevance classification is incorrect. Add `(1-frac) * amount` to the total for water quality programs.

## Fraction cut

Once you've sampled each year, you'll have a total for the year allocated
to water quality programs. The fraction cut is
`(amount_2026 - amount_2025) / amount_2025`. It is OK if this is negative
(indicating an increase in funding for water quality programs).

# Command line

The program should take the number of samples to generate, an optional
random seed to use (default to 20266938), and an optional file to output
the results to (default to `epa_cut_samples.csv`).

The results should be a CSV file with the following columns:
"2026 amount", "2025 amount", and "Percent cut". ("Percent cut" is just
fraction cut times 100, no percent sign is needed.)

After generating the samples, it will give the mean, standard deviation, and
a 97% credible interval for the "Percent cut" column.

It will also give the percent of the time the amount cut was >= 10%.