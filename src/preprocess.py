from __future__ import annotations

from pathlib import Path
import re

import pandas as pd


REQUIRED_STANDARD_FIELDS = (
    "review_text",
    "rating",
    "date",
)
OPTIONAL_STANDARD_FIELDS = ("review_title",)
DEFAULT_MAPPING_FIELDS = REQUIRED_STANDARD_FIELDS + OPTIONAL_STANDARD_FIELDS

STANDARD_COLUMNS = [
    "review_text",
    "rating",
    "date",
    "category",
    "sentiment_score",
    "sentiment_label",
]

PROCESSED_OUTPUT_RELATIVE_PATHS = {
    "signals": Path("data") / "processed" / "reviews_with_signals.csv",
    "category_summary": Path("data") / "processed" / "category_summary.csv",
    "sentiment_summary": Path("data") / "processed" / "sentiment_summary.csv",
    "monthly_summary": Path("data") / "processed" / "monthly_sentiment_summary.csv",
}

CHART_OUTPUT_RELATIVE_PATHS = {
    "category_review_count": Path("reports") / "figures" / "category_review_count.png",
    "category_avg_sentiment": Path("reports") / "figures" / "category_avg_sentiment.png",
}

REPORT_OUTPUT_RELATIVE_PATH = Path("reports") / "insight_report.md"

COLUMN_ALIASES = {
    "review_text": [
        "review_text",
        "review text",
        "review",
        "review_body",
        "reviewbody",
        "review_content",
        "review content",
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
        "starrating",
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
        "reviewdate",
        "review date",
        "date of experience",
        "experience date",
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
        "reviewtitle",
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
    "data/raw/Amazon_Reviews.csv",
    "data/raw/amazon_reviews.csv",
    "data/raw/demo_amazon_reviews.csv",
    "Amazon_Reviews.csv",
    "amazon_reviews.csv",
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


def resolve_named_paths(
    relative_paths: dict[str, Path],
    base_dir: str | Path = ".",
) -> dict[str, Path]:
    base_path = Path(base_dir)
    return {
        name: base_path / relative_path
        for name, relative_path in relative_paths.items()
    }


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


def get_processed_output_paths(base_dir: str | Path = ".") -> dict[str, Path]:
    return resolve_named_paths(PROCESSED_OUTPUT_RELATIVE_PATHS, base_dir)


def get_chart_output_paths(base_dir: str | Path = ".") -> dict[str, Path]:
    return resolve_named_paths(CHART_OUTPUT_RELATIVE_PATHS, base_dir)


def get_report_output_path(base_dir: str | Path = ".") -> Path:
    return Path(base_dir) / REPORT_OUTPUT_RELATIVE_PATH


def normalize_column_name(column_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(column_name).lower())


def score_column_match(column_name: str, logical_name: str) -> int:
    normalized_name = normalize_column_name(column_name)
    aliases = COLUMN_ALIASES[logical_name]

    for alias_index, alias in enumerate(aliases):
        normalized_alias = normalize_column_name(alias)
        if normalized_name == normalized_alias:
            return 300 - alias_index

    for alias_index, alias in enumerate(aliases):
        normalized_alias = normalize_column_name(alias)
        if normalized_alias and normalized_alias in normalized_name:
            return 200 - alias_index

    token_matches = sum(
        1 for token in TOKEN_HINTS[logical_name] if token in normalized_name
    )
    return token_matches * 25


def get_ranked_candidate_columns(
    columns: list[str] | pd.Index,
    logical_name: str,
) -> list[str]:
    scored_columns = []
    for column_name in [str(column) for column in columns]:
        score = score_column_match(column_name, logical_name)
        if score > 0:
            scored_columns.append((column_name, score))

    scored_columns.sort(key=lambda item: (-item[1], item[0]))
    return [column_name for column_name, _ in scored_columns]


def choose_best_column_match(
    available_columns: list[str],
    logical_name: str,
    used_columns: set[str],
) -> tuple[str, int]:
    best_match = ""
    best_score = 0

    for column_name in available_columns:
        if column_name in used_columns:
            continue

        score = score_column_match(column_name, logical_name)
        if score > best_score:
            best_match = column_name
            best_score = score

    return best_match, best_score


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

    fields_to_map = logical_fields or DEFAULT_MAPPING_FIELDS

    for logical_name in fields_to_map:
        best_match, best_score = choose_best_column_match(
            available_columns=available_columns,
            logical_name=logical_name,
            used_columns=used_columns,
        )

        if best_match and best_score > 0:
            mapping[logical_name] = best_match
            used_columns.add(best_match)

    return mapping


def build_read_csv_attempts(
    read_csv_kwargs: dict[str, object],
) -> list[dict[str, object]]:
    read_csv_attempts = [dict(read_csv_kwargs)]

    if "engine" in read_csv_kwargs:
        return read_csv_attempts

    read_csv_attempts.extend(
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
    return read_csv_attempts


def read_review_csv(csv_path: str | Path, **read_csv_kwargs: object) -> pd.DataFrame:
    read_csv_attempts = build_read_csv_attempts(dict(read_csv_kwargs))
    last_error: Exception | None = None
    for attempt_kwargs in read_csv_attempts:
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


def backfill_standardized_columns(
    standardized_df: pd.DataFrame,
    source_df: pd.DataFrame,
    resolved_mapping: dict[str, str],
) -> pd.DataFrame:
    for logical_name in REQUIRED_STANDARD_FIELDS:
        fallback_candidates = get_ranked_candidate_columns(source_df.columns, logical_name)
        primary_source = resolved_mapping.get(logical_name)

        for fallback_column in fallback_candidates:
            if fallback_column == primary_source:
                continue
            standardized_df[logical_name] = standardized_df[logical_name].fillna(
                source_df[fallback_column]
            )

    return standardized_df


def add_default_signal_columns(standardized_df: pd.DataFrame) -> pd.DataFrame:
    standardized_df["category"] = "unlabeled"
    standardized_df["sentiment_score"] = 0.0
    standardized_df["sentiment_label"] = "neutral"
    return standardized_df


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

    for required_column in REQUIRED_STANDARD_FIELDS:
        if required_column not in standardized_df.columns:
            standardized_df[required_column] = pd.NA

    standardized_df = backfill_standardized_columns(
        standardized_df=standardized_df,
        source_df=review_df,
        resolved_mapping=resolved_mapping,
    )

    if "review_title" in standardized_df.columns:
        standardized_df["review_text"] = standardized_df.apply(
            lambda row: combine_review_title_and_text(
                row.get("review_title"),
                row.get("review_text"),
            ),
            axis=1,
        )

    standardized_df = standardized_df[list(REQUIRED_STANDARD_FIELDS)].copy()
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

    # Deduplicate after text/rating/date normalization so equivalent rows collapse reliably.
    standardized_df = standardized_df.drop_duplicates(
        subset=list(REQUIRED_STANDARD_FIELDS)
    ).reset_index(drop=True)
    standardized_df = add_default_signal_columns(standardized_df)

    return standardized_df[STANDARD_COLUMNS]


def preprocess_dataframe(
    review_df: pd.DataFrame,
    column_mapping: dict[str, str] | None = None,
) -> pd.DataFrame:
    return standardize_review_columns(review_df, column_mapping=column_mapping)


def load_and_standardize_reviews(
    csv_path: str | Path,
    column_mapping: dict[str, str] | None = None,
    **read_csv_kwargs: object,
) -> pd.DataFrame:
    review_df = read_review_csv(csv_path, **read_csv_kwargs)
    return standardize_review_columns(review_df, column_mapping=column_mapping)
