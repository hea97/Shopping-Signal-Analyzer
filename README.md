# Shopping Signal Analyzer

A simple MVP that turns Amazon review text into structured customer reaction signals with a pandas-first pipeline.

## What it does

- safely loads raw review CSV files, with `data/raw/Amazon_Reviews.csv` as the primary source path
- infers input columns and standardizes them to:
  `review_text`, `rating`, `date`, `category`, `sentiment_score`, `sentiment_label`
- cleans text, parses rating strings, combines review title + body when available, and removes exact duplicate standardized reviews
- assigns rule-based issue categories
- assigns rule-based sentiment scores and labels from positive and negative word counts
- saves processed CSV outputs, charts, and a markdown insight report
- includes a notebook that runs the full end-to-end flow

## Project structure

```text
Shopping-Signal-Analyzer/
|- data/
|  |- processed/
|  `- raw/
|     `- Amazon_Reviews.csv
|- notebooks/
|  `- shopping_signal_mvp.ipynb
|- reports/
|  |- figures/
|  `- insight_report.md
|- src/
|  |- __init__.py
|  |- feature_engineering.py
|  |- labeler.py
|  |- preprocess.py
|  |- sentiment.py
|  `- visualize.py
|- requirements.txt
`- README.md
```

## Install

```bash
pip install -r requirements.txt
```

Run commands from the repository root so the notebook and output paths resolve cleanly.

## Input handling

The pipeline is designed for real-world review CSVs where column names and formats are not perfectly clean.

It currently handles:

- column name variants such as `Review Text`, `Review Date`, `Date of Experience`, `Rating`, and `Review Title`
- rating strings such as `Rated 1 out of 5 stars`
- missing values by backfilling from other likely source columns when possible
- CSV parsing fallback for files that fail under pandas' default CSV engine
- notebook execution with either the real `data/raw/Amazon_Reviews.csv` file or a small demo fallback

The notebook first looks for these files:

- `data/raw/Amazon_Reviews.csv`
- `amazon_reviews.csv`
- `data/raw/amazon_reviews.csv`
- `data/raw/demo_amazon_reviews.csv`
- `Amazon_Reviews.csv`

## Current rule-based categories

- `customer_service`
- `delivery_shipping`
- `refunds_returns`
- `account_access`
- `pricing_billing`
- `prime_membership`
- `product_quality`
- `order_management`
- `other`

## Run the notebook

```bash
jupyter notebook notebooks/shopping_signal_mvp.ipynb
```

Notebook flow:

1. resolve the review CSV path
2. load the CSV with safe parsing fallbacks
3. standardize columns to the internal schema
4. label categories and sentiment
5. save processed outputs, charts, and the insight report

If no review CSV is found, the notebook writes a tiny demo file to `data/raw/demo_amazon_reviews.csv`.

## Outputs

Running the notebook saves these artifacts:

- `data/processed/reviews_with_signals.csv`
- `data/processed/category_summary.csv`
- `data/processed/sentiment_summary.csv`
- `data/processed/monthly_sentiment_summary.csv`
- `reports/figures/category_review_count.png`
- `reports/figures/category_avg_sentiment.png`
- `reports/insight_report.md`

## MVP notes

- category labeling is rule-based and tuned for the current Amazon review dataset
- sentiment analysis is rule-based and uses word-count text scoring with a small rating adjustment
- the report is generated from the same summary tables used for the charts
- the code stays intentionally simple and modular
