"""
Tier 1 Frontline Performance & Leaderboard Calculation Module.
Computes weekly throughput, SLA compliance, CSAT, repeat-contact friction,
and handle-time metrics strictly for eligible frontline agents.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

from src.performance.agent_assignment import TIER1_FRONTLINE_TEAMS


def calculate_tier1_leaderboard(
    df_tickets: pd.DataFrame,
    target_week: str,
    min_closed_sample: int = 5,
) -> List[Dict[str, Any]]:
    """
    Computes the weekly Tier 1 Frontline Leaderboard for the specified ISO week.
    Only includes agents assigned to Chat Frontline, Email Frontline, and Voice Frontline.
    Strictly excludes Tier 2 / Warranty and other operational back-office teams.
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

    # De-duplicate cross-system duplicate pairs if both exist (prefer helpdesk)
    if "source_system" in df.columns and "ticket_id" in df.columns:
        # Sort so helpdesk comes before legacy_fd, then drop duplicate ticket_ids
        df = df.sort_values(by=["ticket_id", "source_system"]).drop_duplicates(subset=["ticket_id"], keep="first")

    # Filter to eligible Tier 1 Frontline tickets
    if "agent_team" in df.columns:
        t1_df = df[df["agent_team"].isin(TIER1_FRONTLINE_TEAMS)].copy()
    else:
        t1_df = df[df["assigned_team"].isin(TIER1_FRONTLINE_TEAMS)].copy()

    # Slice A: Tickets closed in the target week
    closed_mask = (
        t1_df["status"].isin(["resolved", "closed"])
        & (t1_df["resolved_week"] == target_week)
        & t1_df["resolved_dt"].notnull()
    )
    week_closed_df = t1_df[closed_mask].copy()

    # Slice B: Tickets assigned/created in the target week
    assigned_mask = t1_df["created_week"] == target_week
    week_assigned_df = t1_df[assigned_mask].copy()

    # Collect all unique Tier 1 agents active in this week (either closed or assigned)
    active_agent_ids = sorted(list(set(week_closed_df["agent_id"].unique()) | set(week_assigned_df["agent_id"].unique())))

    leaderboard_rows = []

    for aid in active_agent_ids:
        agent_closed = week_closed_df[week_closed_df["agent_id"] == aid]
        agent_assigned = week_assigned_df[week_assigned_df["agent_id"] == aid]

        # Metadata lookup
        combined = pd.concat([agent_closed, agent_assigned])
        name = combined["agent_name"].iloc[0] if "agent_name" in combined.columns else aid
        team = combined["agent_team"].iloc[0] if "agent_team" in combined.columns else combined["assigned_team"].iloc[0]
        site = combined["agent_site"].iloc[0] if "agent_site" in combined.columns else "Unknown"

        tickets_closed = len(agent_closed)
        tickets_assigned = len(agent_assigned)

        # SLA breaches on assigned/handled tickets
        if "is_sla_breached" in agent_assigned.columns:
            sla_breaches = int(agent_assigned["is_sla_breached"].sum())
            sla_breach_rate = round((sla_breaches / tickets_assigned * 100), 1) if tickets_assigned > 0 else 0.0
        else:
            sla_breaches = 0
            sla_breach_rate = 0.0

        # CSAT ratings on closed tickets (1-5 scale, 0 excluded)
        if "csat_score_clean" in agent_closed.columns:
            csat_series = agent_closed["csat_score_clean"].dropna()
        else:
            csat_series = agent_closed["csat_score"].replace(0, np.nan).dropna()
        
        valid_csat_count = len(csat_series)
        avg_csat = round(float(csat_series.mean()), 2) if valid_csat_count > 0 else None

        # Repeat contacts (30-day return rate)
        if "is_repeat_contact" in agent_closed.columns:
            repeat_count = int(agent_closed["is_repeat_contact"].sum())
            repeat_rate = round((repeat_count / tickets_closed * 100), 1) if tickets_closed > 0 else 0.0
        else:
            repeat_count = 0
            repeat_rate = 0.0

        # Valid handle time (first_response to resolution; excluding inverted legacy)
        if "handle_time_minutes" in agent_closed.columns:
            ht_series = agent_closed["handle_time_minutes"].dropna()
            valid_ht_count = len(ht_series)
            avg_ht = round(float(ht_series.mean()), 1) if valid_ht_count > 0 else None
        else:
            valid_ht_count = 0
            avg_ht = None

        # Small sample flag
        is_small_sample = tickets_closed < min_closed_sample

        leaderboard_rows.append({
            "agent_id": aid,
            "agent_name": name,
            "team": team,
            "site": site,
            "week": target_week,
            "tickets_closed": tickets_closed,
            "tickets_assigned": tickets_assigned,
            "sla_breaches": sla_breaches,
            "sla_breach_rate_pct": sla_breach_rate,
            "valid_csat_count": valid_csat_count,
            "average_csat": avg_csat,
            "repeat_contacts_30d": repeat_count,
            "repeat_contact_rate_pct": repeat_rate,
            "valid_handle_time_count": valid_ht_count,
            "average_handle_time_minutes": avg_ht,
            "is_small_sample": is_small_sample,
        })

    # Sort descending by tickets_closed, then ascending by SLA breach rate
    leaderboard_rows.sort(
        key=lambda r: (r["tickets_closed"], -(r["sla_breach_rate_pct"] if r["sla_breach_rate_pct"] is not None else 999.0)),
        reverse=True,
    )

    # Assign rank (1-indexed)
    for idx, row in enumerate(leaderboard_rows, start=1):
        row["rank_by_tickets_closed"] = idx

    return leaderboard_rows
