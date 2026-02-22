This repo records my data for resolving [the prediction marketI created about water quality program funding cuts](https://manifold.markets/EricMoyer/epa-budget-for-water-quality-progra).

# Process

After the extracting the JSON and attaching the first ratings (that would be prompts 01 and 02 in the `prompts` directory), the distributions of the confidence ratings were:

```console
$ rg 'water_quality_relevance_certainty":' epa_fy2026_hr6938_div_b_title_i
i.json |  sed -E 's/ *"(water_quality_relevance_certainty)": *
([0-9]+).*/\1: \2/' | sort | uniq -c

      7 water_quality_relevance_certainty: 2
     21 water_quality_relevance_certainty: 3
      6 water_quality_relevance_certainty: 4
     28 water_quality_relevance_certainty: 5

$ rg 'water_quality_relevance_certainty"' epa_fy2025_hr1968_div_a_title_vi
i.json |  sed -E 's/ *"(water_quality_relevance_certainty)": *
([0-9]+).*/\1: \2/' | sort | uniq -c

      2 water_quality_relevance_certainty: 1
      3 water_quality_relevance_certainty: 2
     16 water_quality_relevance_certainty: 3
      6 water_quality_relevance_certainty: 4
     20 water_quality_relevance_certainty: 5
```
