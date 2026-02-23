Please improve the simplistic "flip" for incorrect relevance classifications.
Instead, we will choose a different classification for the item based on the
distribution of classifications in the data. To get a better approximation,
use the distribution of classifications combining both years.

First, count the number of items in each `water_quality_relevance` classification across both years. For example, assume we got the following result:

| Count | water_quality_relevance classification |
|-------|----------------------------------------|
| 45    | for water quality programs             |
| 13    | not for water quality programs         |
| 45    | partially for water quality programs   |
| 6     | unknown                                |

If an unknown item is classified incorrectly, then we will sample a new 
classification for it from the distribution of classifications in the data
excluding its original classification. In the example above, if an item with an
original classification of "unknown" is classified incorrectly, then we will
sample a new classification for it from the distribution of classifications in
the data excluding "unknown". You can make a cumulative table for each 
original classification to make this sampling easier. For example, for the
"unknown" classification, the cumulative distribution for sampling a new classification would be:

| Cumulative Count | water_quality_relevance classification |
|------------------|----------------------------------------|
| 45               | for water quality programs             |
| 58               | not for water quality programs         |
| 103              | partially for water quality programs   |

Then you sample a random integer uniformly in [0,102]. If it is less than a
row in the table, then that row's classification is the new classification for
the item.

This algorithm is not required, just an example of how to achieve the correct
distribution.

Now, when sampling a line item, sample the certainty as before. Then draw a
random number for correctness using a uniform distribution over [0, 1]. If the
correctness is less than the certainty, then the relevance classification is
correct. Otherwise, draw a new classification for the item excluding the
original classification as outlined above. Now draw `frac` from that final
classification's distribution and add `frac * amount` to the total for water
quality programs.
