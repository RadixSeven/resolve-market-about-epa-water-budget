# EPA Appropriations JSON Schema

## Top-level structure

```json
{
  "metadata": {
    "bill": "H.R. 6938",
    "congress": 119,
    "fiscal_year": 2026,
    "division": "B",
    "title": "II",
    "agency": "Environmental Protection Agency",
    "currency": "USD",
    "notes": ["..."]
  },
  "accounts": [ <account>, ... ]
}
```

## Account / Line Item (recursive)

```json
{
  "name": "string (human-readable label)",
  "amount": 744195000,
  "sub_items": [ <account>, ... ],
  "funding_source": "general_fund | trust_fund | offsetting_fees | oil_spill_liability_tf",
  "available_until": "2027-09-30",
  "statutory_reference": "optional citation to authorizing law",
  "transfers_in": [ { "from_account": "...", "amount": ... } ],
  "transfers_out": [ { "to_account": "...", "amount": ... } ],
  "notes": ["..."]
}
```

All fields except `name` and `amount` are optional.

## Water quality classification fields

Each line item (leaf or parent) carries the following optional fields
for classifying its relevance to water quality programs.

### Classification

```json
{
  "water_quality_relevance": "for water quality programs | partially for water quality programs | not for water quality programs | unknown",
  "water_quality_relevance_certainty": 3
}
```

#### Water quality relevance values
The following values are used to classify water quality relevance in the `water_quality_relevance` field.

| Value                                    | Meaning |
|------------------------------------------|---------|
| `"for water quality programs"`           | Funding is primarily or entirely directed at water quality activities |
| `"partially for water quality programs"` | A meaningful share of funding supports water quality, but the item also covers non-water activities |
| `"not for water quality programs"`       | Funding is not directed at water quality (e.g. air quality, chemical safety, general overhead) |
| `"unknown"`                              | Insufficient information to classify (e.g. unspecified earmarks, zeroed items) |

#### Water quality relevance certainty values

The following values are used to classify certainty regarding the classification in the `water_quality_relevance` field. This is the certainty that the water quality relevance classification is correct. It is stored in the `water_quality_relevance_certainty` field.

| Value | Meaning                 |
|-------|-------------------------|
| `5`   | Certainty > 99 %        |
| `4`   | 90 % < certainty ≤ 99 % |
| `3`   | 50 % < certainty ≤ 90 % |
| `2`   | 25 % < certainty ≤ 50 % |
| `1`   | Certainty ≤ 25 %        |

### Evidence ratings

Each line item also carries seven 1–5 evidence ratings that document
**why** it received its classification. Higher values indicate stronger
evidence for the dimension described.

```json
{
  "wq_evidence_name_reference": 3,
  "wq_evidence_authorizing_statute": 4,
  "wq_evidence_infrastructure": 2,
  "wq_evidence_monitoring": 1,
  "wq_evidence_contamination": 1,
  "wq_evidence_general_purpose": 2,
  "wq_evidence_non_water": 1
}
```

| Field | 1 (low) | 5 (high) |
|-------|---------|----------|
| `wq_evidence_name_reference` | Name does not mention water | Name explicitly says "water quality", "clean water", "drinking water", etc. |
| `wq_evidence_authorizing_statute` | No statute cited, or statute is not water-specific | Core water quality statute (CWA/FWPCA, SDWA, WIFIA) |
| `wq_evidence_infrastructure` | Does not fund water infrastructure | Primarily funds water/wastewater/stormwater infrastructure |
| `wq_evidence_monitoring` | Does not fund water quality monitoring | Primarily funds water quality monitoring, testing, or assessment |
| `wq_evidence_contamination` | Does not address water contamination | Primarily addresses contamination of water resources (groundwater, surface water) |
| `wq_evidence_general_purpose` | Narrowly water-specific program | Completely general-purpose or multi-media (covers many program areas) |
| `wq_evidence_non_water` | No non-water indicators | Entirely non-water program (e.g. air quality, chemical safety) |

The first five evidence fields are "pro-water-quality" indicators (higher
values suggest the item IS for water quality). The last two are
"anti-water-quality" indicators (higher values suggest the item is NOT
for water quality or is too general to classify as water-specific).

## Double-counting rules

1. If an item has `sub_items`, its `amount` is the **envelope total**
   (the headline figure stated in the bill). Do NOT add it to the
   sub_items when summing — it equals the sum of its sub_items.

2. Sub_items always exhaustively partition the parent amount.
   When the bill only earmarks part of an account, an explicit
   `"Unallocated/general"` remainder item is included so that:

       sum(sub_items[*].amount) == parent.amount

3. To get total EPA appropriated dollars with no double-counting,
   sum all **leaf nodes** (items that have no `sub_items` array).

4. `transfers_out` entries indicate money that leaves this account
   and arrives at another account. The receiving account's headline
   `amount` is as stated in the bill (i.e., the direct appropriation
   only). The `transfers_in` on the receiving account documents
   additional resources available beyond the direct appropriation.
   Transfers are informational — they do NOT change any `amount` values.

## Downstream usage

- To label items as "water quality" or not, annotate leaf nodes.
- To compare FY2025 vs FY2026, match on `name` fields (which should
  be kept consistent across files).
- `notes` fields capture provisos, conditions, and interpretive context
  that may matter for classification.
```
