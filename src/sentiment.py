from __future__ import annotations

import re

import pandas as pd

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

    if float(rating) >= 4.0:
        return 1.0
    if float(rating) <= 2.0:
        return -1.0
    return 0.0


def score_rule_based_sentiment(
    review_text: str,
    rating: float | int | None = None,
) -> tuple[float, str]:
    # Keep the MVP transparent: text score is word hits, rating adds a small tie-breaker.
    _, _, text_score = score_text_sentiment(review_text)
    rating_score = score_rating_adjustment(rating)
    sentiment_score = round(text_score + rating_score, 2)

    if sentiment_score >= 1.0:
        sentiment_label = "positive"
    elif sentiment_score <= -1.0:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"

    return sentiment_score, sentiment_label


def apply_rule_based_sentiment(review_df: pd.DataFrame) -> pd.DataFrame:
    sentiment_df = review_df.copy()
    scores_and_labels = sentiment_df.apply(
        lambda row: score_rule_based_sentiment(
            row["review_text"],
            row["rating"],
        ),
        axis=1,
    )
    sentiment_df["sentiment_score"] = scores_and_labels.map(lambda item: item[0])
    sentiment_df["sentiment_label"] = scores_and_labels.map(lambda item: item[1])
    return sentiment_df
