from __future__ import annotations

import re

import pandas as pd


OTHER_CATEGORY = "other"

CATEGORY_RULES = {
    "customer_service": [
        "customer service",
        "customer support",
        "customer-care",
        "support team",
        "support",
        "customer care",
        "representative",
        "agent",
        "chat support",
        "chat",
        "call center",
        "help desk",
        "service team",
    ],
    "delivery_shipping": [
        "delivery",
        "delivered",
        "shipping",
        "shipped",
        "shipment",
        "arrived",
        "arrival",
        "package",
        "packaging",
        "parcel",
        "courier",
        "driver",
        "tracking",
        "late delivery",
        "lost package",
        "missing package",
        "not delivered",
    ],
    "refunds_returns": [
        "refund",
        "refunded",
        "return",
        "returned",
        "replacement",
        "replace",
        "replaced",
        "money back",
        "reimburse",
        "reimbursement",
    ],
    "account_access": [
        "account",
        "login",
        "log in",
        "sign in",
        "password",
        "verification",
        "verification code",
        "otp",
        "security code",
        "locked",
        "suspended",
        "blocked",
        "closed my account",
        "freeze my account",
        "document review",
    ],
    "pricing_billing": [
        "price",
        "prices",
        "pricing",
        "overpriced",
        "expensive",
        "charged",
        "charging me",
        "billing",
        "payment",
        "credit card",
        "debit card",
        "fee",
        "fees",
        "subscription",
        "charged twice",
        "renewal",
    ],
    "prime_membership": [
        "amazon prime",
        "prime membership",
        "prime video",
        "prime day",
        "membership",
        "prime",
    ],
    "product_quality": [
        "quality",
        "broken",
        "damaged",
        "defective",
        "used item",
        "used product",
        "fake",
        "counterfeit",
        "poor quality",
        "wrong item",
        "item was used",
        "condition",
    ],
    "order_management": [
        "order",
        "ordered",
        "place order",
        "placing an order",
        "order cancelled",
        "order canceled",
        "cancelled my order",
        "cancel order",
        "checkout",
        "basket",
        "cart",
        "purchase",
        "buy online",
        "couldn't order",
    ],
}

CATEGORY_PRIORITY = [
    "account_access",
    "refunds_returns",
    "delivery_shipping",
    "pricing_billing",
    "product_quality",
    "prime_membership",
    "customer_service",
    "order_management",
]

CATEGORY_PATTERNS = {
    category_name: [
        re.compile(rf"(?<!\w){re.escape(keyword.lower())}(?!\w)")
        for keyword in keywords
    ]
    for category_name, keywords in CATEGORY_RULES.items()
}


def count_keyword_hits(review_text: str, patterns: list[re.Pattern[str]]) -> int:
    lowered_text = review_text.lower()
    return sum(len(pattern.findall(lowered_text)) for pattern in patterns)


def get_category_scores(review_text: str) -> dict[str, int]:
    return {
        category_name: count_keyword_hits(review_text, CATEGORY_PATTERNS[category_name])
        for category_name in CATEGORY_RULES
    }


def label_review_category(review_text: str) -> str:
    scores = get_category_scores(review_text)
    positive_scores = {
        category_name: score
        for category_name, score in scores.items()
        if score > 0
    }

    if not positive_scores:
        return OTHER_CATEGORY

    best_category = max(
        positive_scores.items(),
        key=lambda item: (
            item[1],
            -CATEGORY_PRIORITY.index(item[0]),
        ),
    )[0]
    return best_category


def apply_rule_based_categories(review_df: pd.DataFrame) -> pd.DataFrame:
    labeled_df = review_df.copy()
    labeled_df["category"] = labeled_df["review_text"].fillna("").map(
        label_review_category
    )
    return labeled_df
