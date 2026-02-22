Please review the FY2025 and FY2026 EPA appropriations JSON files for consistency in their water quality classifications and evidence ratings.

## Files to compare

- `epa_fy2025_hr1968_div_a_title_vii.json`
- `epa_fy2026_hr6938_div_b_title_ii.json`

## What to check

### 1. Match line items across years

Match items by `name` field. Items may appear at different nesting depths or under renamed parent accounts, so match on the item name itself rather than its position in the tree. The name may slightly shift from year to year but still match.

Report any items that exist in one year but not the other (new, removed, or renamed).

### 2. Compare water quality classifications

For each matched pair, compare:

- `water_quality_relevance` — the categorical label
- `water_quality_relevance_certainty` — the 1–5 certainty score

Flag any pair where the categorical label differs. A certainty difference of 1 point is acceptable; flag differences of 2 or more.

### 3. Compare evidence ratings

For each matched pair, compare the seven `wq_evidence_*` fields:

- `wq_evidence_name_reference`
- `wq_evidence_authorizing_statute`
- `wq_evidence_infrastructure`
- `wq_evidence_monitoring`
- `wq_evidence_contamination`
- `wq_evidence_general_purpose`
- `wq_evidence_non_water`

Flag any field where the two years differ by 2 or more points. A 1-point difference is acceptable.

### 4. When differences are acceptable

A difference is justified if the bill text shows a genuine semantic change between fiscal years, such as:

- A program was restructured or merged with another
- Earmarks or provisos redirect funding to a different purpose
- New statutory language materially changes the scope

When you find a justified difference, note the reason briefly.

## Output format

Produce a summary with:

1. **Items only in FY2025** — list with name and parent account
2. **Items only in FY2026** — list with name and parent account
3. **Classification mismatches** — table with columns: Item Name, FY2025 relevance, FY2026 relevance, FY2025 certainty, FY2026 certainty, Justified? (yes/no + reason)
4. **Evidence rating mismatches** (difference >= 2) — table with columns: Item Name, Field, FY2025 value, FY2026 value, Justified? (yes/no + reason)
5. **Recommendations** — specific changes to make to either file to restore consistency, or explanations for why the difference should stand

## Apply fixes

After producing the summary, update both JSON files to resolve unjustified inconsistencies:

- For each unjustified classification or evidence mismatch, pick the more defensible rating (based on the bill text and the schema definitions in `EPA-budget-schema.md`) and apply it to both years.
- If neither year's rating is clearly better, choose the rating that best fits the bill text and apply it to both.
- Do not change ratings where the difference is justified by a genuine semantic change between fiscal years.
- Preserve all other fields (amounts, notes, statutory references, etc.) exactly as they are.
