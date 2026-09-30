"""
Comprehensive Weekly Support Performance & Throughput Orchestrator.
Builds the complete role-governed weekly payload containing Tier 1 Leaderboard,
Tier 2 Operational Diagnostics, Other Teams Overview, and Data Quality Warnings.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

from src.performance.agent_assignment import (
    resolve_agent_assignment,
    OTHER_OPERATIONAL_TEAMS,
    TIER1_FRONTLINE_TEAMS,
    TIER2_TEAMS,
)
from src.performance.tier1_metrics import calculate_tier1_leaderboard
from src.performance.tier2_metrics import calculate_tier2_operational_summary
from src.performance.trend_analysis import calculate_weekly_performance_trends


def calculate_other_ops_summary(df_tickets: pd.DataFrame, target_week: str) -> List[Dict[str, Any]]:
    """Computes operational throughput for back-office teams (Logistics, Billing, Returns Desk)."""
    df = df_tickets.copy()
    if "resolved_dt" not in df.columns:
        df["resolved_dt"] = pd.to_datetime(df["resolved_at"], errors="coerce")
    if "resolved_week" not in df.columns:
        df["resolved_week"] = df["resolved_dt"].dt.strftime("%G-W%V")

    other_df = df[df["assigned_team"].isin(OTHER_OPERATIONAL_TEAMS)].copy()
    week_closed = other_df[
        other_df["status"].isin(["resolved", "closed"]) & (other_df["resolved_week"] == target_week)
    ]

    summaries = []
    for team in sorted(list(OTHER_OPERATIONAL_TEAMS)):
        team_closed = week_closed[week_closed["assigned_team"] == team]
        csat_s = team_closed["csat_score"].replace(0, np.nan).dropna() if "csat_score" in team_closed.columns else pd.Series()
        summaries.append({
            "team_name": team,
            "tickets_closed": len(team_closed),
            "valid_csat_count": len(csat_s),
            "average_csat": round(float(csat_s.mean()), 2) if not csat_s.empty else None,
            "active_agents": team_closed["agent_id"].nunique() if not team_closed.empty else 0,
        })
    return summaries


def build_weekly_performance_payload(
    df_tickets: pd.DataFrame,
    df_agents: pd.DataFrame,
    target_week: str,
    previous_week: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Builds the unified, role-governed weekly performance payload.
    Ensures complete separation of frontline volume rankings from warranty cycle-time analysis.
    """
    # 1. Resolve agent assignment metadata
    resolved_tickets = resolve_agent_assignment(df_tickets, df_agents)

    # 2. Tier 1 Frontline Leaderboard
    t1_leaderboard = calculate_tier1_leaderboard(resolved_tickets, target_week=target_week)

    # 3. Tier 2 / Warranty Operational Performance
    t2_summary = calculate_tier2_operational_summary(resolved_tickets, target_week=target_week)

    # 4. Other Operational Teams
    other_ops = calculate_other_ops_summary(resolved_tickets, target_week=target_week)

    # 5. Trend Analysis
    trends = calculate_weekly_performance_trends(resolved_tickets, current_week=target_week, previous_week=previous_week)

    # 6. Data Quality & Fairness Warnings
    warnings = []
    small_samples = [r["agent_name"] for r in t1_leaderboard if r["is_small_sample"]]
    if small_samples:
        warnings.append(
            f"Small sample size warning (<5 closed tickets): {', '.join(small_samples[:4])}"
            + (f" and {len(small_samples)-4} others." if len(small_samples) > 4 else ".")
        )

    low_csat_agents = [r["agent_name"] for r in t1_leaderboard if r["valid_csat_count"] < 3 and r["tickets_closed"] >= 5]
    if low_csat_agents:
        warnings.append(f"Low CSAT response count (<3 responses): {', '.join(low_csat_agents)}.")

    legacy_inversions = resolved_tickets[
        (resolved_tickets["resolved_week"] == target_week)
        & (resolved_tickets["resolved_dt"] < resolved_tickets["first_response_dt"])
    ]
    if not legacy_inversions.empty:
        warnings.append(
            f"Legacy timestamp anomalies detected in {len(legacy_inversions)} tickets (excluded from handle time averages)."
        )

    return {
        "week": target_week,
        "governance_rule": "Tier 1 volume ranking only. Tier 2 / Warranty is excluded from volume ranking because policy specifies resolution-day measurement.",
        "tier1_frontline_leaderboard": t1_leaderboard,
        "tier2_warranty_operational_summary": t2_summary,
        "other_operational_teams": other_ops,
        "week_over_week_trends": trends,
        "data_quality_warnings": warnings,
    }
