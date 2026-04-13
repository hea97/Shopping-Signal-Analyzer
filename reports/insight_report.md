# Shopping Signal Analyzer Insight Report

## Objective

Summarize the strongest customer reaction signals from Amazon review text.

## Dataset

- source file: `data\raw\Amazon_Reviews.csv`
- review count: 21055
- date range: 2007-08-27 to 2024-09-17
- inferred column mapping:
- `review_text` <- `Review Text`
- `rating` <- `Rating`
- `date` <- `Review Date`
- `review_title` <- `Review Title`

## Signal highlights

- top customer reaction category: `delivery_shipping` (6194 reviews)
- most positive category: `pricing_billing` (0.12 avg sentiment)
- most negative category: `account_access` (-2.28 avg sentiment)
- sentiment mix: negative: 13889, positive: 5985, neutral: 1181

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
| delivery_shipping | 6194 | 1.97 | -1.14 | 0.22 | 0.71 |
| general | 3648 | 3.24 | 0.61 | 0.56 | 0.38 |
| refunds_returns | 3344 | 1.76 | -1.46 | 0.18 | 0.78 |
| customer_service | 1879 | 1.96 | -1.21 | 0.24 | 0.72 |
| pricing_billing | 1871 | 2.71 | 0.12 | 0.43 | 0.51 |
| account_access | 1618 | 1.19 | -2.28 | 0.04 | 0.93 |
| prime_membership | 1588 | 2.18 | -0.63 | 0.29 | 0.65 |
| product_quality | 518 | 2.09 | -1.30 | 0.24 | 0.69 |

## Recommended next steps

- review the largest negative categories first
- refine category keywords for mixed-service reviews that mention multiple issues
- compare recent monthly trend changes after updating the dataset
