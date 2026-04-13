from __future__ import annotations

import re

import pandas as pd


POSITIVE_PHRASES = {
    "great customer service": 2.0,
    "excellent customer service": 2.0,
    "highly recommend": 2.0,
    "very happy": 1.5,
    "great experience": 1.5,
    "fast delivery": 1.0,
    "arrived on time": 1.0,
    "quick refund": 1.5,
    "refunded quickly": 1.5,
    "resolved quickly": 1.5,
    "no hassle": 1.0,
    "worth it": 1.0,
    "love amazon": 2.0,
}

NEGATIVE_PHRASES = {
    "terrible customer service": 2.5,
    "poor customer service": 2.0,
    "never again": 2.5,
    "never use again": 2.0,
    "do not trust": 2.0,
    "waste of time": 2.0,
    "very disappointing": 1.5,
    "did not arrive": 2.0,
    "didn't arrive": 2.0,
    "not delivered": 2.0,
    "late delivery": 1.5,
    "locked my account": 2.5,
    "account suspended": 2.5,
    "charged twice": 2.0,
    "used item": 1.5,
    "wrong item": 1.5,
}

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


def count_weighted_phrase_hits(
    review_text: str,
    phrase_weights: dict[str, float],
) -> float:
    lowered_text = review_text.lower()
    return sum(
        lowered_text.count(phrase) * weight
        for phrase, weight in phrase_weights.items()
    )


def score_rule_based_sentiment(
    review_text: str,
    rating: float | int | None = None,
) -> tuple[float, str]:
    tokens = tokenize_review_text(review_text)
    positive_hits = sum(token in POSITIVE_WORDS for token in tokens)
    negative_hits = sum(token in NEGATIVE_WORDS for token in tokens)
    word_score = max(min(positive_hits - negative_hits, 4), -4) * 0.5

    phrase_score = count_weighted_phrase_hits(
        review_text,
        POSITIVE_PHRASES,
    ) - count_weighted_phrase_hits(
        review_text,
        NEGATIVE_PHRASES,
    )

    rating_score = 0.0
    if pd.notna(rating):
        rating_score = float(rating) - 3.0

    sentiment_score = round(float(rating_score + word_score + phrase_score), 2)

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
