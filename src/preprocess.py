from __future__ import annotations

from pathlib import Path
import re

import pandas as pd


STANDARD_COLUMNS = [
    "review_text",
    "rating",
    "date",
    "category",
    "sentiment_score",
    "sentiment_label",
]

COLUMN_ALIASES = {
    "review_text": [
        "review_text",
        "review text",
        "review",
        "review_body",
        "review_content",
        "text",
        "content",
        "body",
        "comment",
        "review body",
        "reviews.text",
        "reviews_text",
    ],
    "rating": [
        "rating",
        "review rating",
        "review_rating",
        "star_rating",
        "star rating",
        "stars",
        "score",
        "overall",
        "reviews.rating",
        "reviews_rating",
    ],
    "date": [
        "date",
        "review_date",
        "review date",
        "date of experience",
        "timestamp",
        "time",
        "created_at",
        "posted_at",
        "reviews.date",
        "reviews_date",
    ],
    "review_title": [
        "review_title",
        "review title",
        "title",
        "headline",
        "summary",
    ],
}

TOKEN_HINTS = {
    "review_text": ("review", "text", "body", "comment", "content"),
    "rating": ("rating", "star", "score"),
    "date": ("date", "time", "created", "posted"),
    "review_title": ("title", "headline", "summary"),
}

REVIEW_FILE_CANDIDATES = [
    "Amazon_Reviews.csv",
    "data/raw/Amazon_Reviews.csv",
    "amazon_reviews.csv",
    "data/raw/amazon_reviews.csv",
]

TRAILING_DATE_PATTERN = re.compile(
    r"\s*(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\s*$",
    re.IGNORECASE,
)

PUNCTUATION_TRANSLATION = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00a0": " ",
    }
)


def ensure_project_directories(base_dir: str | Path = ".") -> dict[str, Path]:
    base_path = Path(base_dir)
    paths = {
        "raw": base_path / "data" / "raw",
        "processed": base_path / "data" / "processed",
        "figures": base_path / "reports" / "figures",
        "reports": base_path / "reports",
        "notebooks": base_path / "notebooks",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def normalize_column_name(column_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(column_name).lower())


def resolve_review_csv_path(base_dir: str | Path = ".") -> Path | None:
    base_path = Path(base_dir)

    for candidate_name in REVIEW_FILE_CANDIDATES:
        candidate_path = base_path / candidate_name
        if candidate_path.exists():
            return candidate_path

    for candidate_path in sorted(base_path.rglob("*.csv")):
        lower_name = candidate_path.name.lower()
        if "review" not in lower_name:
            continue
        if "processed" in {part.lower() for part in candidate_path.parts}:
            continue
        return candidate_path

    return None


def infer_column_mapping(
    columns: list[str] | pd.Index,
    logical_fields: tuple[str, ...] | None = None,
) -> dict[str, str]:
    available_columns = [str(column) for column in columns]
    used_columns: set[str] = set()
    mapping: dict[str, str] = {}

    fields_to_map = logical_fields or ("review_text", "rating", "date", "review_title")

    for logical_name in fields_to_map:
        best_match = ""
        best_score = 0
        normalized_aliases = {
            normalize_column_name(alias) for alias in COLUMN_ALIASES[logical_name]
        }

        for column_name in available_columns:
            if column_name in used_columns:
                continue

            normalized_name = normalize_column_name(column_name)
            score = 0

            if normalized_name in normalized_aliases:
                score = 100
            elif any(alias in normalized_name for alias in normalized_aliases):
                score = 80
            else:
                score = sum(
                    1 for token in TOKEN_HINTS[logical_name] if token in normalized_name
                )

            if score > best_score:
                best_match = column_name
                best_score = score

        if best_match and best_score > 0:
            mapping[logical_name] = best_match
            used_columns.add(best_match)

    return mapping


def read_review_csv(csv_path: str | Path, **read_csv_kwargs: object) -> pd.DataFrame:
    attempt_kwargs_list = [dict(read_csv_kwargs)]

    if "engine" not in read_csv_kwargs:
        attempt_kwargs_list.extend(
            [
                {**read_csv_kwargs, "engine": "python"},
                {**read_csv_kwargs, "engine": "python", "encoding": "utf-8-sig"},
                {
                    **read_csv_kwargs,
                    "engine": "python",
                    "encoding_errors": "replace",
                },
            ]
        )

    last_error: Exception | None = None
    for attempt_kwargs in attempt_kwargs_list:
        try:
            return pd.read_csv(csv_path, **attempt_kwargs)
        except Exception as exc:  # pragma: no cover
            last_error = exc

    raise ValueError(f"Could not read {csv_path}: {last_error}") from last_error


def parse_rating_value(rating_value: object) -> float | pd.NA:
    if pd.isna(rating_value):
        return pd.NA

    matched_value = re.search(r"(\d+(?:\.\d+)?)", str(rating_value))
    if matched_value is None:
        return pd.NA

    return float(matched_value.group(1))


def clean_review_text(review_text: object) -> str:
    cleaned_text = str(review_text or "").translate(PUNCTUATION_TRANSLATION)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    cleaned_text = TRAILING_DATE_PATTERN.sub("", cleaned_text).strip(" ,;-")
    return cleaned_text


def combine_review_title_and_text(review_title: object, review_text: object) -> str:
    cleaned_title = clean_review_text(review_title)
    cleaned_text = clean_review_text(review_text)

    if not cleaned_title:
        return cleaned_text
    if not cleaned_text:
        return cleaned_title
    if cleaned_title.lower() in cleaned_text.lower():
        return cleaned_text

    return f"{cleaned_title}. {cleaned_text}"


def standardize_review_columns(
    review_df: pd.DataFrame,
    column_mapping: dict[str, str] | None = None,
) -> pd.DataFrame:
    resolved_mapping = column_mapping or infer_column_mapping(review_df.columns)
    if "review_text" not in resolved_mapping:
        raise ValueError(
            "Could not infer a review text column. Pass a mapping for review_text."
        )

    rename_map = {
        source_name: logical_name
        for logical_name, source_name in resolved_mapping.items()
    }
    standardized_df = review_df.rename(columns=rename_map).copy()

    for required_column in ("review_text", "rating", "date"):
        if required_column not in standardized_df.columns:
            standardized_df[required_column] = pd.NA

    if "review_title" in standardized_df.columns:
        standardized_df["review_text"] = standardized_df.apply(
            lambda row: combine_review_title_and_text(
                row.get("review_title"),
                row.get("review_text"),
            ),
            axis=1,
        )

    standardized_df = standardized_df[["review_text", "rating", "date"]].copy()
    standardized_df["review_text"] = (
        standardized_df["review_text"].fillna("").map(clean_review_text)
    )
    standardized_df = standardized_df[
        standardized_df["review_text"].str.len() > 0
    ].reset_index(drop=True)
    standardized_df["rating"] = standardized_df["rating"].map(parse_rating_value)
    standardized_df["date"] = pd.to_datetime(
        standardized_df["date"], errors="coerce", utc=True
    ).dt.tz_localize(None)
    standardized_df["category"] = "unlabeled"
    standardized_df["sentiment_score"] = 0.0
    standardized_df["sentiment_label"] = "neutral"

    return standardized_df[STANDARD_COLUMNS]


def load_and_standardize_reviews(
    csv_path: str | Path,
    column_mapping: dict[str, str] | None = None,
    **read_csv_kwargs: object,
) -> pd.DataFrame:
    review_df = read_review_csv(csv_path, **read_csv_kwargs)
    return standardize_review_columns(review_df, column_mapping=column_mapping)
