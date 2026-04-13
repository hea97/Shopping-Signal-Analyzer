from __future__ import annotations

import re

import pandas as pd

POSITIVE_SENTIMENT_THRESHOLD = 1.0
NEGATIVE_SENTIMENT_THRESHOLD = -1.0

POSITIVE_WORDS = {
    "amazing",
    "best",
    "easy",
    "efficient",
    "excellent",
    "fast",
    "good",
    "great",
    "helpful",
    "happy",
    "love",
    "perfect",
    "pleased",
    "prompt",
    "recommend",
    "reliable",
    "resolved",
    "responsive",
    "smooth",
    "satisfied",
    "useful",
    "worth",
    "wonderful",
}

NEGATIVE_WORDS = {
    "awful",
    "bad",
    "broken",
    "defective",
    "disappointed",
    "damaged",
    "delayed",
    "frustrating",
    "fraud",
    "horrible",
    "lost",
    "late",
    "overcharged",
    "poor",
    "rude",
    "scam",
    "slow",
    "terrible",
    "unresolved",
    "useless",
    "worst",
}

TOKEN_PATTERN = re.compile(r"[a-z']+")


def tokenize_review_text(review_text: str) -> list[str]:
    return TOKEN_PATTERN.findall(review_text.lower())


def count_sentiment_hits(tokens: list[str], sentiment_words: set[str]) -> int:
    return sum(token in sentiment_words for token in tokens)


def score_text_sentiment(review_text: str) -> tuple[int, int, float]:
    tokens = tokenize_review_text(review_text)
    positive_hits = count_sentiment_hits(tokens, POSITIVE_WORDS)
    negative_hits = count_sentiment_hits(tokens, NEGATIVE_WORDS)
    text_score = float(positive_hits - negative_hits)
    return positive_hits, negative_hits, text_score


def score_rating_adjustment(rating: float | int | None = None) -> float:
    if pd.isna(rating):
        return 0.0

    numeric_rating = float(rating)
    if numeric_rating >= 4.0:
        return 1.0
    if numeric_rating <= 2.0:
        return -1.0
    return 0.0


def classify_sentiment_label(sentiment_score: float) -> str:
    if sentiment_score >= POSITIVE_SENTIMENT_THRESHOLD:
        return "positive"
    if sentiment_score <= NEGATIVE_SENTIMENT_THRESHOLD:
        return "negative"
    return "neutral"


def score_rule_based_sentiment(
    review_text: str,
    rating: float | int | None = None,
) -> tuple[float, str]:
    # Keep the MVP transparent: text score is word hits, rating adds a small tie-breaker.
    _, _, text_score = score_text_sentiment(review_text)
    rating_score = score_rating_adjustment(rating)
    sentiment_score = round(text_score + rating_score, 2)
    sentiment_label = classify_sentiment_label(sentiment_score)
    return sentiment_score, sentiment_label


def build_sentiment_output(review_df: pd.DataFrame) -> pd.DataFrame:
    sentiment_results = review_df.apply(
        lambda row: score_rule_based_sentiment(
            row["review_text"],
            row["rating"],
        ),
        axis=1,
        result_type="expand",
    )
    sentiment_results.columns = ["sentiment_score", "sentiment_label"]
    return sentiment_results


def apply_rule_based_sentiment(review_df: pd.DataFrame) -> pd.DataFrame:
    sentiment_df = review_df.copy()
    sentiment_output = build_sentiment_output(sentiment_df)
    sentiment_df[["sentiment_score", "sentiment_label"]] = sentiment_output
    return sentiment_df
