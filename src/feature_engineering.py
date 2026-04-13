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


def round_numeric_columns(summary_df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = summary_df.select_dtypes(include="number").columns
    summary_df[numeric_columns] = summary_df[numeric_columns].round(2)
    return summary_df


def format_markdown_value(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def format_display_path(path_value: str | Path) -> str:
    return Path(path_value).as_posix()


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


def build_category_summary(feature_df: pd.DataFrame) -> pd.DataFrame:
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
    return round_numeric_columns(category_summary)


def build_sentiment_summary(feature_df: pd.DataFrame) -> pd.DataFrame:
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
    return round_numeric_columns(sentiment_summary)


def build_monthly_summary(feature_df: pd.DataFrame) -> pd.DataFrame:
    if feature_df.empty:
        return pd.DataFrame(
            columns=["review_month", "review_count", "avg_sentiment_score"]
        )

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
    return round_numeric_columns(monthly_summary)


def build_summary_tables(feature_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "category_summary": build_category_summary(feature_df),
        "sentiment_summary": build_sentiment_summary(feature_df),
        "monthly_summary": build_monthly_summary(feature_df),
    }


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


def format_category_name(category_name: str) -> str:
    return category_name.replace("_", " ")


def format_share(review_count: float, total_reviews: int) -> str:
    if total_reviews <= 0:
        return "0.0%"
    return f"{(float(review_count) / total_reviews) * 100:.1f}%"


def format_ratio(value: float) -> str:
    return f"{float(value) * 100:.0f}%"


def get_category_action(category_name: str) -> str:
    action_map = {
        "delivery_shipping": "tightening carrier SLA monitoring, failed-delivery handling, and shipment status messaging",
        "refunds_returns": "shortening refund turnaround and exposing return-status updates earlier",
        "customer_service": "improving first-contact resolution and routing escalations faster",
        "account_access": "simplifying verification recovery and adding a manual unlock escalation path",
        "pricing_billing": "clarifying charges, renewals, and pricing changes before payment is submitted",
        "prime_membership": "making renewal, cancellation, and membership status messaging clearer",
        "product_quality": "strengthening damaged-item checks and seller quality controls",
        "order_management": "reducing cancellation friction and surfacing order-status changes sooner",
        OTHER_CATEGORY: "review a sample of uncategorized reviews and promote recurring themes into new rules",
    }
    return action_map.get(category_name, "review the underlying cases and assign a targeted follow-up action")


def build_volume_sentiment_insight(
    category_row: pd.Series,
    total_reviews: int,
    insight_type: str,
) -> str:
    category_name = str(category_row["category"])
    category_label = format_category_name(category_name)
    volume_share = format_share(category_row["review_count"], total_reviews)
    avg_sentiment = float(category_row["avg_sentiment_score"])
    negative_share = format_ratio(category_row["negative_share"])
    positive_share = format_ratio(category_row["positive_share"])
    action_text = get_category_action(category_name)

    if insight_type == "volume_risk":
        return (
            f"- `{category_label}` drives {volume_share} of review volume and {negative_share} of those reviews are negative "
            f"(avg sentiment {avg_sentiment:.2f}). Prioritize {action_text}."
        )

    if insight_type == "severity":
        return (
            f"- `{category_label}` represents {volume_share} of reviews but has the weakest sentiment at {avg_sentiment:.2f} "
            f"with {negative_share} negative share. Tackle {action_text} first to remove the sharpest customer friction."
        )

    if insight_type == "strength":
        return (
            f"- `{category_label}` covers {volume_share} of reviews and has the strongest named sentiment at {avg_sentiment:.2f} "
            f"with {positive_share} positive share. Protect that advantage by {action_text}."
        )

    return (
        f"- `{category_label}` accounts for {volume_share} of reviews with avg sentiment {avg_sentiment:.2f}. "
        f"Use this signal to {action_text}."
    )


def build_actionable_insights(category_summary: pd.DataFrame) -> list[str]:
    if category_summary.empty:
        return ["- No category insights are available because the summary table is empty."]

    total_reviews = int(category_summary["review_count"].sum())
    named_categories = category_summary[category_summary["category"] != OTHER_CATEGORY].copy()
    if named_categories.empty:
        named_categories = category_summary.copy()

    significant_named_categories = named_categories[
        named_categories["review_count"] >= max(25, int(total_reviews * 0.01))
    ].copy()
    if significant_named_categories.empty:
        significant_named_categories = named_categories.copy()

    candidate_sets = [
        (
            "volume_risk",
            significant_named_categories.sort_values(
                ["review_count", "negative_share", "avg_sentiment_score"],
                ascending=[False, False, True],
            ),
        ),
        (
            "severity",
            significant_named_categories.sort_values(
                ["avg_sentiment_score", "review_count"],
                ascending=[True, False],
            ),
        ),
        (
            "strength",
            significant_named_categories.sort_values(
                ["avg_sentiment_score", "review_count"],
                ascending=[False, False],
            ),
        ),
    ]

    actionable_insights: list[str] = []
    used_categories: set[str] = set()

    for insight_type, candidate_df in candidate_sets:
        for _, category_row in candidate_df.iterrows():
            category_name = str(category_row["category"])
            if category_name in used_categories:
                continue
            actionable_insights.append(
                build_volume_sentiment_insight(
                    category_row=category_row,
                    total_reviews=total_reviews,
                    insight_type=insight_type,
                )
            )
            used_categories.add(category_name)
            break

    if len(actionable_insights) < 3:
        remaining_categories = category_summary.sort_values(
            ["review_count", "avg_sentiment_score"],
            ascending=[False, False],
        )
        for _, category_row in remaining_categories.iterrows():
            category_name = str(category_row["category"])
            if category_name in used_categories:
                continue
            actionable_insights.append(
                build_volume_sentiment_insight(
                    category_row=category_row,
                    total_reviews=total_reviews,
                    insight_type="fallback",
                )
            )
            used_categories.add(category_name)
            if len(actionable_insights) >= 3:
                break

    other_category_rows = category_summary[
        category_summary["category"] == OTHER_CATEGORY
    ]
    if not other_category_rows.empty and len(actionable_insights) < 4:
        other_category_row = other_category_rows.iloc[0]
        other_share = format_share(other_category_row["review_count"], total_reviews)
        if float(other_category_row["review_count"]) / max(total_reviews, 1) >= 0.1:
            actionable_insights.append(
                f"- `{format_category_name(OTHER_CATEGORY)}` still accounts for {other_share} of reviews with avg sentiment "
                f"{float(other_category_row['avg_sentiment_score']):.2f}. Review those cases first and promote repeated themes into new category rules."
            )

    return actionable_insights[:4]


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
    actionable_insights = build_actionable_insights(category_summary)

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
        "## Actionable insights",
        "",
        *actionable_insights,
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
    summary_key_to_output_key = {
        "category_summary": "category_summary",
        "sentiment_summary": "sentiment_summary",
        "monthly_summary": "monthly_summary",
    }
    for summary_key, output_key in summary_key_to_output_key.items():
        summary_tables[summary_key].to_csv(output_paths[output_key], index=False)

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
