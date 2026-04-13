# Shopping Signal Analyzer Insight Report

## Objective

Summarize the strongest customer reaction signals from Amazon review text.

## Dataset

- source file: `data/raw/Amazon_Reviews.csv`
- review count: 21212
- date range: 2007-08-27 to 2024-09-17
- inferred column mapping:
- `review_text` <- `Review Text`
- `rating` <- `Rating`
- `date` <- `Review Date`
- `review_title` <- `Review Title`

## Signal highlights

- top customer reaction category: `delivery_shipping` (6031 reviews)
- most positive category: `pricing_billing` (0.45 avg sentiment)
- most negative category: `account_access` (-1.33 avg sentiment)
- sentiment mix: negative: 12581, positive: 6592, neutral: 2039

## Actionable insights

- `delivery shipping` drives 28.4% of review volume and 63% of those reviews are negative (avg sentiment -0.42). Prioritize tightening carrier SLA monitoring, failed-delivery handling, and shipment status messaging.
- `account access` represents 7.3% of reviews but has the weakest sentiment at -1.33 with 82% negative share. Tackle simplifying verification recovery and adding a manual unlock escalation path first to remove the sharpest customer friction.
- `pricing billing` covers 6.1% of reviews and has the strongest named sentiment at 0.45 with 43% positive share. Protect that advantage by clarifying charges, renewals, and pricing changes before payment is submitted.
- `other` still accounts for 16.9% of reviews with avg sentiment 0.76. Review those cases first and promote repeated themes into new category rules.

## Files generated

- processed reviews: `data/processed/reviews_with_signals.csv`
- category summary: `data/processed/category_summary.csv`
- sentiment summary: `data/processed/sentiment_summary.csv`
- monthly summary: `data/processed/monthly_sentiment_summary.csv`
- chart 1: `reports/figures/category_review_count.png`
- chart 2: `reports/figures/category_avg_sentiment.png`

## Category summary snapshot

| category | review_count | avg_rating | avg_sentiment_score | positive_share | negative_share |
| --- | --- | --- | --- | --- | --- |
| delivery_shipping | 6031 | 2.07 | -0.42 | 0.28 | 0.63 |
| other | 3583 | 3.25 | 0.76 | 0.57 | 0.34 |
| refunds_returns | 2598 | 1.69 | -0.92 | 0.19 | 0.72 |
| customer_service | 2274 | 1.99 | -0.68 | 0.27 | 0.65 |
| prime_membership | 1682 | 2.20 | -0.12 | 0.32 | 0.56 |
| order_management | 1651 | 2.00 | -0.61 | 0.25 | 0.65 |
| account_access | 1538 | 1.20 | -1.33 | 0.07 | 0.82 |
| pricing_billing | 1293 | 2.61 | 0.45 | 0.43 | 0.46 |

## Recommended next steps

- review the largest negative categories first
- refine category keywords for mixed-service reviews that mention multiple issues
- compare recent monthly trend changes after updating the dataset
