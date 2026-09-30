"""
Week-over-Week Trend Analysis Module for Support Performance.
Calculates deterministic WoW deltas for throughput, SLA compliance, CSAT, and resolution turnaround.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

from src.performance.tier1_metrics import calculate_tier1_leaderboard
from src.performance.tier2_metrics import calculate_tier2_operational_summary


def calculate_weekly_performance_trends(
    df_tickets: pd.DataFrame,
    current_week: str,
    previous_week: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Computes deterministic week-over-week trend comparisons for both Tier 1 and Tier 2.
    """
    df = df_tickets.copy()
    if "resolved_week" not in df.columns:
        if "resolved_dt" not in df.columns:
            df["resolved_dt"] = pd.to_datetime(df["resolved_at"], errors="coerce")
        df["resolved_week"] = df["resolved_dt"].dt.strftime("%G-W%V")

    all_weeks = sorted(df["resolved_week"].dropna().unique())
    if not previous_week and current_week in all_weeks:
        curr_idx = all_weeks.index(current_week)
        previous_week = all_weeks[curr_idx - 1] if curr_idx > 0 else None

    # Current week payloads
    t1_curr = calculate_tier1_leaderboard(df, current_week)
    t2_curr = calculate_tier2_operational_summary(df, current_week)

    # Aggregates for current week Tier 1
    t1_curr_closed = sum(r["tickets_closed"] for r in t1_curr)
    t1_curr_assigned = sum(r["tickets_assigned"] for r in t1_curr)
    t1_curr_breaches = sum(r["sla_breaches"] for r in t1_curr)
    t1_curr_breach_rate = round((t1_curr_breaches / t1_curr_assigned * 100), 1) if t1_curr_assigned > 0 else 0.0
    valid_csats = [r["average_csat"] for r in t1_curr if r["average_csat"] is not None]
    t1_curr_avg_csat = round(float(np.mean(valid_csats)), 2) if valid_csats else None

    trends: Dict[str, Any] = {
        "current_week": current_week,
        "previous_week": previous_week,
        "tier1_summary": {
            "tickets_closed": t1_curr_closed,
            "tickets_assigned": t1_curr_assigned,
            "sla_breach_rate_pct": t1_curr_breach_rate,
            "average_csat": t1_curr_avg_csat,
            "active_agents": len(t1_curr),
        },
        "tier2_summary": {
            "cases_handled": t2_curr["cases_handled"],
            "cases_resolved": t2_curr["cases_resolved"],
            "average_resolution_days": t2_curr["average_resolution_days"],
            "median_resolution_days": t2_curr["median_resolution_days"],
        },
        "tier1_wow_deltas": None,
        "tier2_wow_deltas": None,
    }

    if previous_week and previous_week in all_weeks:
        t1_prev = calculate_tier1_leaderboard(df, previous_week)
        t2_prev = calculate_tier2_operational_summary(df, previous_week)

        t1_prev_closed = sum(r["tickets_closed"] for r in t1_prev)
        t1_prev_assigned = sum(r["tickets_assigned"] for r in t1_prev)
        t1_prev_breaches = sum(r["sla_breaches"] for r in t1_prev)
        t1_prev_breach_rate = round((t1_prev_breaches / t1_prev_assigned * 100), 1) if t1_prev_assigned > 0 else 0.0
        prev_valid_csats = [r["average_csat"] for r in t1_prev if r["average_csat"] is not None]
        t1_prev_avg_csat = round(float(np.mean(prev_valid_csats)), 2) if prev_valid_csats else None

        trends["tier1_wow_deltas"] = {
            "closed_delta": t1_curr_closed - t1_prev_closed,
            "closed_growth_pct": round(((t1_curr_closed - t1_prev_closed) / t1_prev_closed * 100), 1) if t1_prev_closed > 0 else 0.0,
            "assigned_delta": t1_curr_assigned - t1_prev_assigned,
            "sla_breach_rate_delta_pct": round(t1_curr_breach_rate - t1_prev_breach_rate, 1),
            "csat_delta": round(t1_curr_avg_csat - t1_prev_avg_csat, 2) if (t1_curr_avg_csat and t1_prev_avg_csat) else None,
        }

        t2_prev_resolved = t2_prev["cases_resolved"]
        t2_prev_handled = t2_prev["cases_handled"]
        trends["tier2_wow_deltas"] = {
            "resolved_delta": t2_curr["cases_resolved"] - t2_prev_resolved,
            "handled_delta": t2_curr["cases_handled"] - t2_prev_handled,
            "avg_days_delta": round(t2_curr["average_resolution_days"] - t2_prev["average_resolution_days"], 2) if (t2_curr["average_resolution_days"] and t2_prev["average_resolution_days"]) else None,
        }

    return trends
