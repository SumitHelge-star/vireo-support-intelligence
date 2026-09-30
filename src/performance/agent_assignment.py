"""
Agent Assignment and Team Resolution Module.
Resolves temporal agent assignments against the multi-row roster in agents.csv.
"""

from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
import numpy as np

# Eligible frontline teams for Tier 1 leaderboard
TIER1_FRONTLINE_TEAMS: Set[str] = {
    "Chat Frontline",
    "Email Frontline",
    "Voice Frontline",
}

TIER2_TEAMS: Set[str] = {
    "Escalations & Warranty",
}

OTHER_OPERATIONAL_TEAMS: Set[str] = {
    "Logistics",
    "Billing",
    "Returns Desk",
}


def resolve_agent_assignment(
    df_tickets: pd.DataFrame, df_agents: pd.DataFrame
) -> pd.DataFrame:
    """
    Resolves agent metadata (name, site, team, tier, shift) for each ticket.
    Supports temporal assignment intervals (from_date <= ticket_date <= to_date)
    when multiple roster records exist for a single agent_id.
    """
    df = df_tickets.copy()
    agents = df_agents.copy()

    # Parse dates if needed
    if "created_dt" not in df.columns:
        df["created_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
    
    agents["from_dt"] = pd.to_datetime(agents["from_date"], errors="coerce")
    agents["to_dt"] = pd.to_datetime(agents["to_date"], errors="coerce").fillna(pd.Timestamp.max)

    # Check if agents table has 1 row per agent or multiple
    agent_counts = agents["agent_id"].value_counts()
    multi_roster_agents = set(agent_counts[agent_counts > 1].index)

    if not multi_roster_agents:
        # Fast path: 1-to-1 agent mapping
        agent_map = agents.set_index("agent_id")[["name", "site", "team", "shift", "tier"]].to_dict(orient="index")
        df["agent_name"] = df["agent_id"].map(lambda a: agent_map.get(a, {}).get("name", "Unknown Agent"))
        df["agent_site"] = df["agent_id"].map(lambda a: agent_map.get(a, {}).get("site", "Unknown Site"))
        df["agent_team"] = df["agent_id"].map(lambda a: agent_map.get(a, {}).get("team", df.get("assigned_team", "Unknown Team")))
        df["agent_shift"] = df["agent_id"].map(lambda a: agent_map.get(a, {}).get("shift", "Day"))
        df["agent_tier"] = df["agent_id"].map(lambda a: agent_map.get(a, {}).get("tier", 1))
    else:
        # Temporal join path for historical roster transitions
        records = []
        for _, row in df.iterrows():
            aid = row["agent_id"]
            tdt = row["created_dt"]
            sub = agents[agents["agent_id"] == aid]
            if sub.empty:
                records.append({
                    "agent_name": "Unknown Agent",
                    "agent_site": "Unknown Site",
                    "agent_team": row.get("assigned_team", "Unknown Team"),
                    "agent_shift": "Day",
                    "agent_tier": 1,
                })
            else:
                matched = sub[(sub["from_dt"] <= tdt) & (tdt <= sub["to_dt"])]
                if not matched.empty:
                    m = matched.iloc[0]
                else:
                    m = sub.iloc[-1]
                records.append({
                    "agent_name": m["name"],
                    "agent_site": m["site"],
                    "agent_team": m["team"],
                    "agent_shift": m["shift"],
                    "agent_tier": m["tier"],
                })
        meta_df = pd.DataFrame(records, index=df.index)
        for col in ["agent_name", "agent_site", "agent_team", "agent_shift", "agent_tier"]:
            df[col] = meta_df[col]

    # Classification flags
    df["is_tier1_frontline"] = df["agent_team"].isin(TIER1_FRONTLINE_TEAMS)
    df["is_tier2_warranty"] = df["agent_team"].isin(TIER2_TEAMS)
    df["is_other_ops"] = df["agent_team"].isin(OTHER_OPERATIONAL_TEAMS)

    return df
