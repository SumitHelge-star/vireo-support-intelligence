"""
Repeat-contact and First-Contact Resolution (FCR) analysis module.
Applies Operating Policy v3.2 definitions (30-day post-resolution return contact window).
"""

from typing import Any, Dict, Optional
import pandas as pd
import numpy as np

from src.config import CONTACT_COSTS_INR


def calculate_repeat_contacts(
    df_tickets: pd.DataFrame, window_days: int = 30
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Identifies repeat contacts per customer within the policy's 30-day resolution window.
    Computes financial channel re-handling cost per repeat ticket.
    """
    df = df_tickets.copy()
    
    # Ensure timestamps are parsed
    if "created_dt" not in df.columns:
        df["created_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
    if "resolved_dt" not in df.columns:
        df["resolved_dt"] = pd.to_datetime(df["resolved_at"], errors="coerce")

    # Sort chronological by customer
    df = df.sort_values(by=["customer_id", "created_dt"]).reset_index(drop=True)

    # Shift previous ticket fields within the same customer
    df["prev_ticket_id"] = df.groupby("customer_id")["ticket_id"].shift(1)
    df["prev_resolved_dt"] = df.groupby("customer_id")["resolved_dt"].shift(1)
    df["prev_sku"] = df.groupby("customer_id")["product_sku"].shift(1)
    df["prev_category"] = df.groupby("customer_id")["category"].shift(1)

    # Elapsed days between previous resolution and current ticket creation
    df["days_since_prior_resolution"] = (
        (df["created_dt"] - df["prev_resolved_dt"]).dt.total_seconds() / 86400.0
    )

    # Policy Rule: 0 <= days <= window_days (30 days)
    is_repeat_window = (
        df["days_since_prior_resolution"].notnull()
        & (df["days_since_prior_resolution"] >= 0)
        & (df["days_since_prior_resolution"] <= window_days)
    )

    # Classification of match strength
    # 1. Strongest: Same customer + Same SKU + Same Category
    same_sku = df["product_sku"] == df["prev_sku"]
    same_cat = df["category"] == df["prev_category"]

    df["is_repeat_contact"] = False
    df["repeat_match_type"] = "none"

    # We tag same-SKU return contacts within 30d as primary repeat contacts
    df.loc[is_repeat_window & same_sku & same_cat, "is_repeat_contact"] = True
    df.loc[is_repeat_window & same_sku & same_cat, "repeat_match_type"] = "same_sku_and_category"

    df.loc[is_repeat_window & same_sku & (~same_cat), "is_repeat_contact"] = True
    df.loc[is_repeat_window & same_sku & (~same_cat), "repeat_match_type"] = "same_sku_different_category"

    df.loc[is_repeat_window & (~same_sku), "is_repeat_contact"] = True
    df.loc[is_repeat_window & (~same_sku), "repeat_match_type"] = "same_customer_different_sku"

    # Repeat contact financial cost (costed at channel used per policy)
    df["repeat_contact_cost_inr"] = 0
    repeat_mask = df["is_repeat_contact"]
    df.loc[repeat_mask, "repeat_contact_cost_inr"] = df.loc[repeat_mask, "channel"].map(
        lambda ch: CONTACT_COSTS_INR.get(ch, CONTACT_COSTS_INR["blended"])
    )

    # Summary Statistics
    total_tickets = len(df)
    total_repeat = int(df["is_repeat_contact"].sum())
    repeat_rate = round((total_repeat / total_tickets) * 100, 2) if total_tickets > 0 else 0.0
    total_repeat_cost = int(df["repeat_contact_cost_inr"].sum())

    match_breakdown = df[df["is_repeat_contact"]]["repeat_match_type"].value_counts().to_dict()
    channel_breakdown = df[df["is_repeat_contact"]]["channel"].value_counts().to_dict()
    category_breakdown = df[df["is_repeat_contact"]]["category"].value_counts().head(5).to_dict()
    sku_breakdown = df[df["is_repeat_contact"]]["product_sku"].value_counts().head(5).to_dict()

    summary = {
        "total_tickets": total_tickets,
        "total_repeat_contacts": total_repeat,
        "repeat_contact_rate_pct": repeat_rate,
        "total_repeat_cost_inr": total_repeat_cost,
        "match_type_distribution": match_breakdown,
        "channel_distribution": channel_breakdown,
        "top_repeat_categories": category_breakdown,
        "top_repeat_skus": sku_breakdown,
    }

    return df, summary
