from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from .labeler import OTHER_CATEGORY
    from .preprocess import (
        CHART_OUTPUT_RELATIVE_PATHS,
        PROCESSED_OUTPUT_RELATIVE_PATHS,
        ensure_project_directories,
        get_processed_output_paths,
        get_report_output_path,
    )
except ImportError:  # pragma: no cover
    from labeler import OTHER_CATEGORY
    from preprocess import (
        CHART_OUTPUT_RELATIVE_PATHS,
        PROCESSED_OUTPUT_RELATIVE_PATHS,
        ensure_project_directories,
        get_processed_output_paths,
        get_report_output_path,
    )


def build_signal_features(review_df: pd.DataFrame) -> pd.DataFrame:
    feature_df = review_df.copy()
    feature_df["review_length"] = (
        feature_df["review_text"].fillna("").str.split().str.len()
    )
    feature_df["is_positive"] = (
        feature_df["sentiment_label"].eq("positive").astype(int)
    )
    feature_df["is_negative"] = (
        feature_df["sentiment_label"].eq("negative").astype(int)
    )
    feature_df["review_month"] = feature_df["date"].dt.to_period("M").astype("string")
    feature_df["review_month"] = feature_df["review_month"].fillna("unknown")
    return feature_df


def build_summary_tables(feature_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    category_summary = (
        feature_df.groupby("category", dropna=False)
        .agg(
            review_count=("review_text", "size"),
            avg_rating=("rating", "mean"),
            avg_sentiment_score=("sentiment_score", "mean"),
            positive_share=("is_positive", "mean"),
            negative_share=("is_negative", "mean"),
        )
        .reset_index()
        .sort_values(["review_count", "avg_sentiment_score"], ascending=[False, False])
        .reset_index(drop=True)
    )

    sentiment_summary = (
        feature_df.groupby("sentiment_label", dropna=False)
        .agg(
            review_count=("review_text", "size"),
            avg_rating=("rating", "mean"),
            avg_sentiment_score=("sentiment_score", "mean"),
        )
        .reset_index()
        .sort_values("review_count", ascending=False)
        .reset_index(drop=True)
    )

    if feature_df.empty:
        monthly_summary = pd.DataFrame(
            columns=["review_month", "review_count", "avg_sentiment_score"]
        )
    else:
        monthly_summary = (
            feature_df.groupby("review_month", dropna=False)
            .agg(
                review_count=("review_text", "size"),
                avg_sentiment_score=("sentiment_score", "mean"),
            )
            .reset_index()
            .sort_values("review_month")
            .reset_index(drop=True)
        )

    for summary_df in (category_summary, sentiment_summary, monthly_summary):
        numeric_columns = summary_df.select_dtypes(include="number").columns
        summary_df[numeric_columns] = summary_df[numeric_columns].round(2)

    return {
        "category_summary": category_summary,
        "sentiment_summary": sentiment_summary,
        "monthly_summary": monthly_summary,
    }


def format_markdown_value(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def format_display_path(path_value: str | Path) -> str:
    return Path(path_value).as_posix()


def dataframe_to_markdown_table(summary_df: pd.DataFrame) -> str:
    if summary_df.empty:
        return "| no_data |\n| --- |\n| no rows available |"

    header = "| " + " | ".join(summary_df.columns) + " |"
    divider = "| " + " | ".join(["---"] * len(summary_df.columns)) + " |"
    rows = []

    for _, row in summary_df.iterrows():
        row_values = [format_markdown_value(row[column]) for column in summary_df.columns]
        rows.append("| " + " | ".join(row_values) + " |")

    return "\n".join([header, divider, *rows])


def build_insight_report_markdown(
    feature_df: pd.DataFrame,
    summary_tables: dict[str, pd.DataFrame],
    dataset_label: str,
    column_mapping: dict[str, str] | None = None,
) -> str:
    category_summary = summary_tables["category_summary"]
    sentiment_summary = summary_tables["sentiment_summary"]

    top_category = category_summary.iloc[0] if not category_summary.empty else None

    eligible_categories = category_summary[
        category_summary["category"] != OTHER_CATEGORY
    ].copy()
    if eligible_categories.empty:
        eligible_categories = category_summary.copy()

    if "review_count" in eligible_categories.columns:
        filtered_categories = eligible_categories[eligible_categories["review_count"] >= 25]
        if not filtered_categories.empty:
            eligible_categories = filtered_categories

    most_positive_category = (
        eligible_categories.sort_values(
            ["avg_sentiment_score", "review_count"],
            ascending=[False, False],
        ).iloc[0]
        if not eligible_categories.empty
        else None
    )
    most_negative_category = (
        eligible_categories.sort_values(
            ["avg_sentiment_score", "review_count"],
            ascending=[True, False],
        ).iloc[0]
        if not eligible_categories.empty
        else None
    )

    min_date = feature_df["date"].min()
    max_date = feature_df["date"].max()
    date_range = "unknown"
    if pd.notna(min_date) and pd.notna(max_date):
        date_range = f"{min_date.date()} to {max_date.date()}"

    sentiment_mix_parts = []
    for _, row in sentiment_summary.iterrows():
        sentiment_mix_parts.append(
            f"{row['sentiment_label']}: {int(row['review_count'])}"
        )
    sentiment_mix = ", ".join(sentiment_mix_parts) if sentiment_mix_parts else "no data"

    mapping_lines = []
    for logical_name, source_name in (column_mapping or {}).items():
        mapping_lines.append(f"- `{logical_name}` <- `{source_name}`")
    if not mapping_lines:
        mapping_lines.append("- mapping unavailable")

    highlight_lines = [
        f"- top customer reaction category: `{top_category['category']}` ({int(top_category['review_count'])} reviews)"
        if top_category is not None
        else "- top customer reaction category: unavailable",
        f"- most positive category: `{most_positive_category['category']}` ({most_positive_category['avg_sentiment_score']:.2f} avg sentiment)"
        if most_positive_category is not None
        else "- most positive category: unavailable",
        f"- most negative category: `{most_negative_category['category']}` ({most_negative_category['avg_sentiment_score']:.2f} avg sentiment)"
        if most_negative_category is not None
        else "- most negative category: unavailable",
        f"- sentiment mix: {sentiment_mix}",
    ]

    top_category_table = dataframe_to_markdown_table(category_summary.head(8))

    report_lines = [
        "# Shopping Signal Analyzer Insight Report",
        "",
        "## Objective",
        "",
        "Summarize the strongest customer reaction signals from Amazon review text.",
        "",
        "## Dataset",
        "",
        f"- source file: `{format_display_path(dataset_label)}`",
        f"- review count: {len(feature_df)}",
        f"- date range: {date_range}",
        "- inferred column mapping:",
        *mapping_lines,
        "",
        "## Signal highlights",
        "",
        *highlight_lines,
        "",
        "## Files generated",
        "",
        f"- processed reviews: `{format_display_path(PROCESSED_OUTPUT_RELATIVE_PATHS['signals'])}`",
        f"- category summary: `{format_display_path(PROCESSED_OUTPUT_RELATIVE_PATHS['category_summary'])}`",
        f"- sentiment summary: `{format_display_path(PROCESSED_OUTPUT_RELATIVE_PATHS['sentiment_summary'])}`",
        f"- monthly summary: `{format_display_path(PROCESSED_OUTPUT_RELATIVE_PATHS['monthly_summary'])}`",
        f"- chart 1: `{format_display_path(CHART_OUTPUT_RELATIVE_PATHS['category_review_count'])}`",
        f"- chart 2: `{format_display_path(CHART_OUTPUT_RELATIVE_PATHS['category_avg_sentiment'])}`",
        "",
        "## Category summary snapshot",
        "",
        top_category_table,
        "",
        "## Recommended next steps",
        "",
        "- review the largest negative categories first",
        "- refine category keywords for mixed-service reviews that mention multiple issues",
        "- compare recent monthly trend changes after updating the dataset",
    ]
    return "\n".join(report_lines) + "\n"


def save_pipeline_outputs(
    feature_df: pd.DataFrame,
    summary_tables: dict[str, pd.DataFrame],
    base_dir: str | Path = ".",
) -> dict[str, Path]:
    ensure_project_directories(base_dir)
    output_paths = get_processed_output_paths(base_dir)

    feature_df.to_csv(output_paths["signals"], index=False)
    summary_tables["category_summary"].to_csv(output_paths["category_summary"], index=False)
    summary_tables["sentiment_summary"].to_csv(
        output_paths["sentiment_summary"], index=False
    )
    summary_tables["monthly_summary"].to_csv(output_paths["monthly_summary"], index=False)

    return output_paths


def save_insight_report(
    feature_df: pd.DataFrame,
    summary_tables: dict[str, pd.DataFrame],
    dataset_path: str | Path,
    column_mapping: dict[str, str] | None = None,
    base_dir: str | Path = ".",
) -> Path:
    ensure_project_directories(base_dir)
    report_path = get_report_output_path(base_dir)
    dataset_path_obj = Path(dataset_path)
    base_path = Path(base_dir).resolve()

    try:
        dataset_label = str(dataset_path_obj.resolve().relative_to(base_path))
    except ValueError:
        dataset_label = str(dataset_path_obj)

    report_content = build_insight_report_markdown(
        feature_df=feature_df,
        summary_tables=summary_tables,
        dataset_label=dataset_label,
        column_mapping=column_mapping,
    )
    report_path.write_text(report_content, encoding="utf-8")
    return report_path
