from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_category_review_count_chart(
    category_summary: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    chart_path = Path(output_path)
    chart_path.parent.mkdir(parents=True, exist_ok=True)

    ordered_summary = category_summary.sort_values("review_count", ascending=False)
    plt.figure(figsize=(10, 5))
    plt.bar(
        ordered_summary["category"],
        ordered_summary["review_count"],
        color="#4c78a8",
    )
    plt.title("Amazon Review Count by Customer Reaction Category")
    plt.xlabel("Category")
    plt.ylabel("Review Count")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close()

    return chart_path


def save_category_avg_sentiment_chart(
    category_summary: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    chart_path = Path(output_path)
    chart_path.parent.mkdir(parents=True, exist_ok=True)

    ordered_summary = category_summary.sort_values("review_count", ascending=False)
    plt.figure(figsize=(10, 5))
    plt.bar(
        ordered_summary["category"],
        ordered_summary["avg_sentiment_score"],
        color="#72b7b2",
    )
    plt.axhline(0, color="#333333", linewidth=1, linestyle="--")
    plt.title("Average Amazon Sentiment Score by Category")
    plt.xlabel("Category")
    plt.ylabel("Average Sentiment Score")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close()

    return chart_path


def create_all_charts(
    summary_tables: dict[str, pd.DataFrame],
    base_dir: str | Path = ".",
) -> dict[str, Path]:
    figure_dir = Path(base_dir) / "reports" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    category_summary = summary_tables["category_summary"]
    chart_paths = {
        "category_review_count": save_category_review_count_chart(
            category_summary,
            figure_dir / "category_review_count.png",
        ),
        "category_avg_sentiment": save_category_avg_sentiment_chart(
            category_summary,
            figure_dir / "category_avg_sentiment.png",
        ),
    }
    return chart_paths
