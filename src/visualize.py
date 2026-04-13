from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

try:
    from .preprocess import get_chart_output_paths
except ImportError:  # pragma: no cover
    from preprocess import get_chart_output_paths


def save_bar_chart(
    chart_df: pd.DataFrame,
    value_column: str,
    output_path: str | Path,
    title: str,
    y_label: str,
    bar_color: str,
    add_zero_reference_line: bool = False,
) -> Path:
    chart_path = Path(output_path)
    chart_path.parent.mkdir(parents=True, exist_ok=True)

    ordered_chart_df = chart_df.sort_values("review_count", ascending=False)
    plt.figure(figsize=(10, 5))
    plt.bar(
        ordered_chart_df["category"],
        ordered_chart_df[value_column],
        color=bar_color,
    )
    if add_zero_reference_line:
        plt.axhline(0, color="#333333", linewidth=1, linestyle="--")
    plt.title(title)
    plt.xlabel("Category")
    plt.ylabel(y_label)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close()

    return chart_path


def save_category_review_count_chart(
    category_summary: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    return save_bar_chart(
        chart_df=category_summary,
        value_column="review_count",
        output_path=output_path,
        title="Amazon Review Count by Customer Reaction Category",
        y_label="Review Count",
        bar_color="#4c78a8",
    )


def save_category_avg_sentiment_chart(
    category_summary: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    return save_bar_chart(
        chart_df=category_summary,
        value_column="avg_sentiment_score",
        output_path=output_path,
        title="Average Amazon Sentiment Score by Category",
        y_label="Average Sentiment Score",
        bar_color="#72b7b2",
        add_zero_reference_line=True,
    )


def create_all_charts(
    summary_tables: dict[str, pd.DataFrame],
    base_dir: str | Path = ".",
) -> dict[str, Path]:
    chart_paths = get_chart_output_paths(base_dir)
    category_summary = summary_tables["category_summary"]
    saved_chart_paths = {
        "category_review_count": save_category_review_count_chart(
            category_summary,
            chart_paths["category_review_count"],
        ),
        "category_avg_sentiment": save_category_avg_sentiment_chart(
            category_summary,
            chart_paths["category_avg_sentiment"],
        ),
    }
    return saved_chart_paths
