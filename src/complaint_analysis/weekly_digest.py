"""
Weekly Customer Support Complaint Intelligence Digest Generator.
Assembles deterministic metrics, complaint clusters, representative evidence,
repeat contacts, SLA liabilities, and cross-week trends.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.complaint_analysis.clustering import perform_complaint_clustering, ComplaintCluster
from src.complaint_analysis.representative_tickets import extract_representative_tickets
from src.complaint_analysis.repeat_contact import calculate_repeat_contacts
from src.config import SLA_BREACH_STORE_CREDIT_INR, CONTACT_COSTS_INR


def generate_weekly_digest(
    df_tickets: pd.DataFrame,
    target_week: Optional[str] = None,
    previous_week: Optional[str] = None,
    n_clusters: int = 5,
) -> Dict[str, Any]:
    """
    Generates a comprehensive weekly intelligence payload for the specified week.
    All numerical metrics are deterministic and traceable to ticket IDs.
    """
    df = df_tickets.copy()
    if "created_week" not in df.columns:
        df["created_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
        df["created_week"] = df["created_dt"].dt.strftime("%G-W%V")

    available_weeks = sorted(df["created_week"].dropna().unique())
    if not available_weeks:
        return {"error": "No valid weekly data available."}

    week = target_week or available_weeks[-1]
    week_df = df[df["created_week"] == week].copy()

    if week_df.empty:
        return {"error": f"No tickets found for week {week}."}

    # 1. Run clustering & topic grouping on the week's tickets
    clusters, clustered_df, kmeans, vectorizer = perform_complaint_clustering(
        week_df, n_clusters=n_clusters
    )

    # 2. Extract representative evidence examples
    representative_evidence = extract_representative_tickets(
        clustered_df, clusters, vectorizer, kmeans, top_n=3
    )

    # 3. Repeat contact analysis across whole dataset then filter to current week
    df_with_repeats, repeat_global_summary = calculate_repeat_contacts(df)
    week_repeats = df_with_repeats[df_with_repeats["created_week"] == week]
    
    total_week_tickets = len(week_df)
    week_repeat_count = int(week_repeats["is_repeat_contact"].sum())
    week_repeat_rate = round((week_repeat_count / total_week_tickets) * 100, 2)
    week_repeat_cost = int(week_repeats["repeat_contact_cost_inr"].sum())
    top_repeat_skus = week_repeats[week_repeats["is_repeat_contact"]]["product_sku"].value_counts().head(3).to_dict()

    # 4. SLA breaches and automated credit liabilities
    if "is_sla_breached" not in week_df.columns:
        from src.config import SLA_TARGET_MINUTES
        if "first_response_dt" not in week_df.columns:
            week_df["first_response_dt"] = pd.to_datetime(week_df["first_response_at"], errors="coerce")
        resp_mins = (week_df["first_response_dt"] - pd.to_datetime(week_df["created_at"])).dt.total_seconds() / 60.0
        targets = week_df["channel"].map(SLA_TARGET_MINUTES)
        week_df["is_sla_breached"] = resp_mins > targets

    sla_breaches = int(week_df["is_sla_breached"].sum())
    sla_breach_rate = round((sla_breaches / total_week_tickets) * 100, 2)
    sla_credit_liability = sla_breaches * SLA_BREACH_STORE_CREDIT_INR

    # 5. CSAT ratings (clean scores 1-5, excluding 0)
    csat_clean = week_df["csat_score"].replace(0, np.nan).dropna()
    valid_csat_count = len(csat_clean)
    csat_response_rate = round((valid_csat_count / total_week_tickets) * 100, 2)
    mean_csat = round(float(csat_clean.mean()), 2) if valid_csat_count > 0 else None

    # 6. Channel and Category distributions
    channel_breakdown = week_df["channel"].value_counts().to_dict()
    category_breakdown = week_df["category"].value_counts().head(5).to_dict()

    # 7. Tier 2 / Warranty separation audit
    tier2_tickets = 0
    if "assigned_team" in week_df.columns:
        tier2_tickets = int((week_df["assigned_team"] == "Escalations & Warranty").sum())

    # 8. Week-over-Week trend comparison if previous week is available
    if not previous_week:
        current_idx = available_weeks.index(week)
        previous_week = available_weeks[current_idx - 1] if current_idx > 0 else None

    wow_comparison = None
    if previous_week and previous_week in available_weeks:
        prev_df = df[df["created_week"] == previous_week]
        prev_repeats = df_with_repeats[df_with_repeats["created_week"] == previous_week]
        prev_vol = len(prev_df)
        vol_change = total_week_tickets - prev_vol
        vol_pct_change = round((vol_change / prev_vol) * 100, 2) if prev_vol > 0 else 0.0

        prev_repeat_count = int(prev_repeats["is_repeat_contact"].sum())
        repeat_change = week_repeat_count - prev_repeat_count

        wow_comparison = {
            "previous_week": previous_week,
            "previous_volume": prev_vol,
            "volume_change": vol_change,
            "volume_pct_change": vol_pct_change,
            "previous_repeat_count": prev_repeat_count,
            "repeat_change": repeat_change,
        }

    return {
        "target_week": week,
        "total_tickets": total_week_tickets,
        "channel_breakdown": channel_breakdown,
        "category_breakdown": category_breakdown,
        "complaint_clusters": clusters,
        "representative_evidence": representative_evidence,
        "repeat_contacts": {
            "count": week_repeat_count,
            "rate_pct": week_repeat_rate,
            "total_cost_inr": week_repeat_cost,
            "top_skus": top_repeat_skus,
        },
        "sla_performance": {
            "breach_count": sla_breaches,
            "breach_rate_pct": sla_breach_rate,
            "store_credit_liability_inr": sla_credit_liability,
        },
        "csat_performance": {
            "valid_survey_count": valid_csat_count,
            "response_rate_pct": csat_response_rate,
            "mean_score": mean_csat,
        },
        "tier2_warranty_ticket_count": tier2_tickets,
        "wow_comparison": wow_comparison,
    }
