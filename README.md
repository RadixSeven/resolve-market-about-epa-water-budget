This repo records my data for resolving [the prediction market I created about water quality program funding cuts](https://manifold.markets/EricMoyer/epa-budget-for-water-quality-progra).

# Process

## Produce the initial JSON files

I excerpted files from the EPA appropriations text into `EPA-appropriations-text-FY2024-HR4366.txt`, `EPA-appropriations-text-FY2025-HR1968.html`, and `EPA-appropriations-text-FY2026-HR6938.html`. I had Claude create `EPA-budget-schema.md` based on `EPA-appropriations-text-FY2026-HR6938.html`
It then created the initial JSON files `epa_fy2025_hr1968_div_a_title_vii.json` and `epa_fy2026_hr6938_div_b_title_ii.json` based on the schema and the text files.
Next, I created the `prompts` directory and added `01-schema-update-prompt.md`,
asking Claude Code to update the schema to include fields for classifying water quality relevance and certainty, and to add those fields to the existing JSON files.
Then, I added `02-consistency-check.md` to do a quick check between the two
JSON files. It caught one place that would be good to rename for easier
comparison.

## Distribution of relevance
After the extracting the JSON and attaching the first ratings (that would be prompts 01 and 02 in the `prompts` directory), the distributions of the confidence ratings were:

```console
$ rg 'water_quality_relevance_certainty":' epa_fy2026_hr6938_div_b_title_ii.json |  sed -E 's/ *"(water_quality_relevance_certainty)": *
([0-9]+).*/\1: \2/' | sort | uniq -c

      7 water_quality_relevance_certainty: 2
     21 water_quality_relevance_certainty: 3
      6 water_quality_relevance_certainty: 4
     28 water_quality_relevance_certainty: 5

$ rg 'water_quality_relevance_certainty"' epa_fy2025_hr1968_div_a_title_vii.json |  sed -E 's/ *"(water_quality_relevance_certainty)": *
([0-9]+).*/\1: \2/' | sort | uniq -c

      2 water_quality_relevance_certainty: 1
      3 water_quality_relevance_certainty: 2
     16 water_quality_relevance_certainty: 3
      6 water_quality_relevance_certainty: 4
     20 water_quality_relevance_certainty: 5
```

## Joint distribution of relevance and certainty

Then I asked Claude to write a script to show the joint distribution of certainty and relevance. After a bit of tweaking, I got the following output:
```bash
python3 wq_joint_dist.py epa_fy2025_hr1968_div_a_title_vii.json
```
| Relevance                            | Certainty | Count |
|--------------------------------------|-----------|-------|
| for water quality programs           | 5         | 17    |
| partially for water quality programs | 3         | 13    |
| partially for water quality programs | 4         | 4     |
| not for water quality programs       | 5         | 3     |
| unknown                              | 1         | 2     |
| partially for water quality programs | 2         | 2     |
| not for water quality programs       | 3         | 2     |
| unknown                              | 2         | 1     |
| for water quality programs           | 3         | 1     |
| for water quality programs           | 4         | 1     |
| not for water quality programs       | 4         | 1     |


```bash
python3 wq_joint_dist.py epa_fy2026_hr6938_div_b_title_ii.json
```
| Relevance                            | Certainty | Count |
|--------------------------------------|-----------|-------|
| for water quality programs           | 5         | 24    |
| partially for water quality programs | 3         | 18    |
| partially for water quality programs | 2         | 4     |
| partially for water quality programs | 4         | 4     |
| not for water quality programs       | 5         | 4     |
| unknown                              | 2         | 3     |
| not for water quality programs       | 3         | 2     |
| for water quality programs           | 3         | 1     |
| for water quality programs           | 4         | 1     |
| not for water quality programs       | 4         | 1     |

(You need to use the version at 25888cc127f6d606136563236a7ddba3890a3445 to get
these results.)

## Redo for line-items only

After looking at the above and doing some spot-checks, I realized I only
cared about certainty and relevance for line items (i.e., leaf nodes in the
budget hierarchy). So I went back and added a filter to only include line items.

```bash
python3 wq_joint_dist.py epa_fy2025_hr1968_div_a_title_vii.json
```

| Relevance                            | Certainty | Count |
|--------------------------------------|-----------|-------|
| for water quality programs           | 5         | 16    |
| for water quality programs           | 4         | 1     |
| for water quality programs           | 3         | 1     |
| not for water quality programs       | 5         | 3     |
| not for water quality programs       | 4         | 1     |
| not for water quality programs       | 3         | 2     |
| partially for water quality programs | 4         | 2     |
| partially for water quality programs | 3         | 9     |
| partially for water quality programs | 2         | 2     |
| unknown                              | 2         | 1     |
| unknown                              | 1         | 2     |

```bash
python3 wq_joint_dist.py epa_fy2026_hr6938_div_b_title_ii.json
```

| Relevance                            | Certainty | Count |
|--------------------------------------|-----------|-------|
| for water quality programs           | 5         | 20    |
| for water quality programs           | 4         | 1     |
| for water quality programs           | 3         | 1     |
| not for water quality programs       | 5         | 4     |
| not for water quality programs       | 4         | 1     |
| not for water quality programs       | 3         | 2     |
| partially for water quality programs | 4         | 2     |
| partially for water quality programs | 3         | 13    |
| partially for water quality programs | 2         | 4     |
| unknown                              | 2         | 2     |

## Add earmarks data

After looking at the FY2026 data labeled "partially for water quality programs"
(which I generally agreed with), I started to look at the "unknown" items, which
were all earmarks.

I added the earmarks data from the FY2026 bill to the repository. But that
will be a lot of work to incorporate (and to find the FY2025 earmarks data).

I want to see how certain the conclusions are given the current data before
I try to get more certainty.

## Try the first Monte Carlo simulation
I added `03-simulate-epa-water-budget-allocations-to-assess-cuts.md` to ask Claude to write a Monte Carlo simulation based on the current data.

```bash
python3 simulate_epa_wq_cuts.py -n 100000
```

Yields:
```
Samples: 100000
Mean percent change: 0.96%
Std dev: 17.75%
97% credible interval: [-42.94%, 32.91%]
Percent of samples with >= 10% cut: 32.9%
Results written to epa_cut_samples.csv
```

This looks like ![Plot of cut percentages with a long tail to the not-cut side](epa_cut_samples_distribution_100000.png). (This was a plot generated
by Claude based on the `epa_cut_samples.csv` output from the above simulation.)

Unfortunately, 33% of the samples show a cut of 10% or more. And the mean is
a 1% cut. So, I need to do more work to reduce the uncertainty. The first thing
to try is to fix the simplistic "flip" for incorrect relevance classifications.
Since it will no longer be switching 0% to 100% or vice versa, that should
reduce the variance.

## Add a more realistic model for incorrect classifications

I added `04-dont-use-flip-incorrectness.md` but pasted it into a planning
session in the same conversation that implemented the simulation to take
advantage of the context.

The result:
```bash
python3 simulate_epa_wq_cuts.py -n 100000
```

```
Samples: 100000
Mean percent change: -0.15%
Std dev: 23.62%
97% credible interval: [-60.28%, 40.23%]
Percent of samples with >= 10% cut: 37.2%
Results written to epa_cut_samples.csv
```

This has more variation and a higher percentage of samples with >= 10% cuts.

The next improvement is to fix the low probability of "unknown" being correct.
It's pretty clear that they are unknown. I'll increase the certainty and mark
my manual change in the data. I don't expect this to change much, but it is
an inexpensive step and improves the accuracy of the model.

## Make the "unknown" items more certain

I marked all the "unknown" items as certainty 5.

After running the simulation again, I got:

```
Samples: 100000
Mean percent change: -0.06%
Std dev: 23.61%
97% credible interval: [-59.75%, 40.24%]
Percent of samples with >= 10% cut: 37.3%
Results written to epa_cut_samples.csv
```

So, now an even higher percentage of samples show >= 10% cuts, but the CI is
smaller.

## Identically-named branches

### Harmonize names

I asked Claude Code:

> How many line items (those without members in "sub_items") are the same
> between @epa_fy2025_hr1968_div_a_title_vii.json and
> @epa_fy2026_hr6938_div_b_title_ii.json - I want to
> know whether it is worth making sure their fraction assigned to water
> quality programs are the same for both years rather than choosing
> the fraction independently.

Claude responded with `2025-2026_matching_leaves.txt` and the following summary:

> Key finding: 33 of 34 already have identical WQ evidence scores
>
> The only difference is Long Island Sound — FY2025 has infra=3,
> monitoring=3 while FY2026 has infra=2, monitoring=4.
> Both still have the same relevance category ("for water quality programs")
> and certainty (5).
>
> Items that are leaves in one file but not the other (6 cases)
>
> These are the structural mismatches where a program is a leaf in one year but subdivided in the other:
>
>  - S&T: Research National Priorities — leaf in FY2025, split into CDS + remainder in FY2026
>  - STAG: CW SRF — leaf in FY2025, split into CPF/CDS + formula in FY2026
>  - STAG: DW SRF — leaf in FY2025, split into CPF/CDS + formula in FY2026
>  - STAG: Categorical/multi-media grants — leaf in FY2025, split into 5 sub-items in FY2026
>  - STAG: CDS items — $0 in FY2025 (zeroed), $20,364,000 as item (16) in FY2026
>  - STAG: Prior-year rescission — FY2025 only
>
> And FY2026 has 4 items with no FY2025 counterpart: Energy Star, Grants (impl/training), Above-ground leaking fuel tank, Lake Pontchartrain.
>
> Bottom line
>
> It is absolutely worth enforcing the same water quality fraction for both years on matching leaves —
> the evidence scores are already virtually identical (33/34), confirming these are the same
> programs. You'd just need to reconcile the one Long Island Sound discrepancy and handle the 6
> structural mismatches where granularity differs.

After fixing the one discrepancy, I asked Claude Code

> I harmonized the evidence scores for Long Island Sound. Please ensure that
> the names for the matching line items are character-for-character identical
> between the two years. When you modify a file to do this, add a note to the
> "notes" array (or add a new notes array if the item didn't have one before)
> recording the original name. Follow the pattern in the 2026
> "Long Island Sound grants (FWPCA section 124)" line item. Choose the more
> informative name or if both are the same, the one that seems easier to
> understand for a layperson, if neither is easier, choose the one that comes
> first when sorted lexically.

Claude did this, leaving the following summary:

> All 34 matching leaf items now have character-for-character identical names
> across both files. The JSON is valid in both files.
>
> Summary of changes made:
>
> - 3 edits to FY2025 (adopted FY2026's more informative names):
>
>    - "Unallocated/general" (under S&T) → "Science and Technology (general/unallocated)"
>    - "Unallocated/general" (under EPM) → "Environmental Programs and Management (general/unallocated)"
>    - "Unallocated/general (CERCLA response activities)" → "Superfund cleanup and response activities (remainder)"
> - 19 edits to FY2026 (adopted FY2025's more descriptive names, stripping bill-specific (N) prefixes):
>    - "Alaska Native contamination cleanup grants" → "Alaska Native contaminated lands grants"
>    - "LUST cleanup activities under SWDA section 9003(h)" → "Leaking underground storage tank cleanup (SWDA section 9003(h))"
>  - 17 STAG sub-items stripped of (N) prefixes and adopted FY2025's more descriptive names (e.g., "(7) SDWA 1459A(a)-(j) grants..." → "Small and disadvantaged community drinking water assistance (SDWA section 1459A(a)-(j))")
>
> Every renamed item has an "Originally named: ..." note recording its
> original name, following the Long Island Sound pattern.
>
> The 6 FY2025-only and 16 FY2026-only leaves are items that exist in only one
> year or have different structural granularity (leaf vs. parent), so no name
> harmonization was needed.

I'll deal with the different granularity items later if this is 
not enough to reduce the uncertainty. But the next step is to enforce the
same water quality funding fraction for all 34 of the matching leaves.