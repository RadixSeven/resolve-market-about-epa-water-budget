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
