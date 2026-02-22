Please update the schema to include an optional field for
line items labeling them as whether they are for water
quality programs. It should have the values "for water
quality programs", "partially for water quality programs",
"not for water quality programs", "unknown". There should
be a certainty field accompanying this field with the
values "5" meaning "certainty >99%", "4" meaning "90% <
certainty <= 99%", "3" meaning "50% < certainty <= 90%",
"2" meaning "25% < certainty <= 50%" and "1" meaning
"certainty <= 25%". Please also review the existing JSON
documents and add fields for rating the evidence that a
line item is for water quality. For example (not
prescriptive), "mentions-water-quality" with a rating 1-5
rating whether the line item text directly mentions water
quality related activities. For each line item, consider
the evidence that it is or is not for water-quality and
try to fit that into a rating system. Then add fields for
each of the rating system items you develop. Try to use less than 20 fields.
