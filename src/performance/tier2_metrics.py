"""
Tier 2 / Warranty Operational Performance Module.
Computes multi-touch resolution turnaround, RMA volumes, and case duration metrics.
STRICT GOVERNANCE RULE: Tier 2 agents are NEVER ranked on raw ticket counts.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

from src.performance.agent_assignment import TIER2_TEAMS


def calculate_tier2_operational_summary(
    df_tickets: pd.DataFrame,
    target_week: str,
) -> Dict[str, Any]:
    """
    Computes operational turnaround and workload metrics for Escalations & Warranty.
    Focuses on resolution cycle time (days) and case depth rather than closed-ticket throughput.
    """
    df = df_tickets.copy()

    # Ensure ISO week formatting
    if "resolved_dt" not in df.columns:
        df["resolved_dt"] = pd.to_datetime(df["resolved_at"], errors="coerce")
    if "resolved_week" not in df.columns:
        df["resolved_week"] = df["resolved_dt"].dt.strftime("%G-W%V")
    if "created_week" not in df.columns:
        if "created_dt" not in df.columns:
            df["created_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
        df["created_week"] = df["created_dt"].dt.strftime("%G-W%V")

    # De-duplicate cross-system duplicate pairs if both exist
    if "source_system" in df.columns and "ticket_id" in df.columns:
        df = df.sort_values(by=["ticket_id", "source_system"]).drop_duplicates(subset=["ticket_id"], keep="first")

    # Filter to Tier 2 / Warranty tickets
    if "agent_team" in df.columns:
        t2_df = df[df["agent_team"].isin(TIER2_TEAMS)].copy()
    else:
        t2_df = df[df["assigned_team"].isin(TIER2_TEAMS)].copy()

    if t2_df.empty:
        return {
            "week": target_week,
            "team_name": "Escalations & Warranty",
            "cases_handled": 0,
            "cases_resolved": 0,
            "average_resolution_days": None,
            "median_resolution_days": None,
            "longest_resolution_days": None,
            "warranty_rma_count": 0,
            "repeat_contacts_30d": 0,
            "repeat_contact_rate_pct": 0.0,
            "valid_csat_count": 0,
            "average_csat": None,
            "agent_operational_summary": [],
            "governance_notice": "Tier 2 / Warranty is excluded from volume ranking because policy specifies resolution-day measurement.",
        }

    # Slice A: Cases resolved in target week
    resolved_mask = (
        t2_df["status"].isin(["resolved", "closed"])
        & (t2_df["resolved_week"] == target_week)
        & t2_df["resolved_dt"].notnull()
    )
    week_resolved = t2_df[resolved_mask].copy()

    # Slice B: Cases assigned in target week
    assigned_mask = t2_df["created_week"] == target_week
    week_assigned = t2_df[assigned_mask].copy()

    cases_resolved = len(week_resolved)
    cases_handled = len(week_assigned)

    # Resolution duration in days: (resolved_dt - created_dt)
    # Valid only when resolved_dt >= created_dt
    if not week_resolved.empty:
        valid_duration_mask = week_resolved["resolved_dt"] >= week_resolved["created_dt"]
        valid_durations = (
            (week_resolved.loc[valid_duration_mask, "resolved_dt"] - week_resolved.loc[valid_duration_mask, "created_dt"]).dt.total_seconds() / 86400.0
        )
        avg_res_days = round(float(valid_durations.mean()), 2) if not valid_durations.empty else None
        med_res_days = round(float(valid_durations.median()), 2) if not valid_durations.empty else None
        max_res_days = round(float(valid_durations.max()), 2) if not valid_durations.empty else None

        # Duration distribution buckets
        duration_buckets = {
            "under_2_days": int((valid_durations < 2.0).sum()),
            "2_to_5_days": int(((valid_durations >= 2.0) & (valid_durations <= 5.0)).sum()),
            "5_to_10_days": int(((valid_durations > 5.0) & (valid_durations <= 10.0)).sum()),
            "over_10_days": int((valid_durations > 10.0).sum()),
        }
    else:
        avg_res_days = None
        med_res_days = None
        max_res_days = None
        duration_buckets = {"under_2_days": 0, "2_to_5_days": 0, "5_to_10_days": 0, "over_10_days": 0}

    # Hardware RMA Replacements (count each actual replacement issued exactly once)
    if "replacement_issued" in week_resolved.columns:
        rma_count = int(
            (week_resolved["replacement_issued"].astype(str).str.strip().str.upper() == "Y").sum()
        )
    else:
        rma_count = 0

    # Repeat contacts
    if "is_repeat_contact" in week_resolved.columns:
        repeat_count = int(week_resolved["is_repeat_contact"].sum())
        repeat_rate = round((repeat_count / cases_resolved * 100), 1) if cases_resolved > 0 else 0.0
    else:
        repeat_count = 0
        repeat_rate = 0.0

    # CSAT on resolved warranty cases
    if "csat_score_clean" in week_resolved.columns:
        csat_series = week_resolved["csat_score_clean"].dropna()
    else:
        csat_series = week_resolved["csat_score"].replace(0, np.nan).dropna()
    valid_csat_count = len(csat_series)
    avg_csat = round(float(csat_series.mean()), 2) if valid_csat_count > 0 else None

    # Agent-level breakdown (strictly unranked!)
    active_agent_ids = sorted(list(set(week_resolved["agent_id"].unique()) | set(week_assigned["agent_id"].unique())))
    agent_summaries = []

    for aid in active_agent_ids:
        a_res = week_resolved[week_resolved["agent_id"] == aid]
        a_asgn = week_assigned[week_assigned["agent_id"] == aid]
        comb = pd.concat([a_res, a_asgn])
        name = comb["agent_name"].iloc[0] if "agent_name" in comb.columns else aid
        site = comb["agent_site"].iloc[0] if "agent_site" in comb.columns else "Unknown"

        a_resolved_count = len(a_res)
        a_handled_count = len(a_asgn)

        if not a_res.empty:
            a_valid_dur = (a_res["resolved_dt"] - a_res["created_dt"]).dt.total_seconds() / 86400.0
            a_valid_dur = a_valid_dur[a_valid_dur >= 0]
            a_avg_days = round(float(a_valid_dur.mean()), 2) if not a_valid_dur.empty else None
        else:
            a_avg_days = None

        agent_summaries.append({
            "agent_id": aid,
            "agent_name": name,
            "site": site,
            "cases_handled": a_handled_count,
            "cases_resolved": a_resolved_count,
            "average_resolution_days": a_avg_days,
            "repeat_contacts_30d": int(a_res["is_repeat_contact"].sum()) if "is_repeat_contact" in a_res.columns else 0,
        })

    # Sort agent summary alphabetically by name to avoid implicit ranking
    agent_summaries.sort(key=lambda x: x["agent_name"])

    return {
        "week": target_week,
        "team_name": "Escalations & Warranty",
        "cases_handled": cases_handled,
        "cases_resolved": cases_resolved,
        "average_resolution_days": avg_res_days,
        "median_resolution_days": med_res_days,
        "longest_resolution_days": max_res_days,
        "duration_distribution": duration_buckets,
        "warranty_rma_count": rma_count,
        "repeat_contacts_30d": repeat_count,
        "repeat_contact_rate_pct": repeat_rate,
        "valid_csat_count": valid_csat_count,
        "average_csat": avg_csat,
        "agent_operational_summary": agent_summaries,
        "governance_notice": "Tier 2 / Warranty is excluded from volume ranking because policy specifies resolution-day measurement.",
    }
