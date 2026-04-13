# Shopping Signal Analyzer

A simple MVP that turns Amazon review text into structured customer reaction signals with a pandas-first pipeline.

## What it does

- safely loads raw review CSV files, including the current `Amazon_Reviews.csv`
- infers input columns and standardizes them to:
  `review_text`, `rating`, `date`, `category`, `sentiment_score`, `sentiment_label`
- cleans text, parses rating strings, and combines review title + body when available
- assigns rule-based issue categories
- assigns rule-based sentiment scores and labels
- saves processed CSV outputs, charts, and a markdown insight report
- includes a notebook that runs the full end-to-end flow

## Project structure

```text
Shopping-Signal-Analyzer/
|- Amazon_Reviews.csv
|- data/
|  |- processed/
|  `- raw/
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

## Input handling

The pipeline is designed for real-world review CSVs where column names and formats are not perfectly clean.

It currently handles:

- column name variants such as `Review Text`, `Review Date`, `Date of Experience`, `Rating`, and `Review Title`
- rating strings such as `Rated 1 out of 5 stars`
- CSV parsing fallback for files that fail under pandas' default CSV engine
- notebook execution with either the real `Amazon_Reviews.csv` file or a small demo fallback

The notebook first looks for these files:

- `Amazon_Reviews.csv`
- `data/raw/Amazon_Reviews.csv`
- `amazon_reviews.csv`
- `data/raw/amazon_reviews.csv`

## Current rule-based categories

- `customer_service`
- `delivery_shipping`
- `refunds_returns`
- `account_access`
- `pricing_billing`
- `prime_membership`
- `product_quality`
- `order_management`
- `general`

## Run the notebook

```bash
jupyter notebook notebooks/shopping_signal_mvp.ipynb
```

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
- sentiment analysis is rule-based and blends rating with text cues
- the report is generated from the same summary tables used for the charts
- the code stays intentionally simple and modular
