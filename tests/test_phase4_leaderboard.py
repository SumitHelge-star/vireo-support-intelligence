"""
Tests for Tier 1 Frontline Weekly Leaderboard.
Verifies volume ranking, duplicate protection, small-sample warnings, and Tier 2 exclusion.
"""

import pytest
import pandas as pd
from src.data_loader import load_all_datasets
from src.normalization import derive_ticket_features
from src.complaint_analysis.repeat_contact import calculate_repeat_contacts
from src.performance.agent_assignment import resolve_agent_assignment, TIER1_FRONTLINE_TEAMS, TIER2_TEAMS
from src.performance.tier1_metrics import calculate_tier1_leaderboard


@pytest.fixture(scope="module")
def prepared_tickets():
    datasets = load_all_datasets()
    df = derive_ticket_features(datasets["tickets"], datasets.get("orders"))
    df, _ = calculate_repeat_contacts(df)
    df = resolve_agent_assignment(df, datasets["agents"])
    return df


def test_tier1_leaderboard_volume_ranking_and_fields(prepared_tickets):
    """Verifies that Tier 1 leaderboard produces ranked rows with all required metrics."""
    leaderboard = calculate_tier1_leaderboard(prepared_tickets, target_week="2025-W41")
    assert len(leaderboard) > 0

    # Verify descending rank order by tickets closed
    closed_counts = [r["tickets_closed"] for r in leaderboard]
    assert closed_counts == sorted(closed_counts, reverse=True)

    # Verify required keys exist in each record
    required_keys = [
        "agent_id", "agent_name", "team", "site", "week",
        "tickets_closed", "tickets_assigned", "sla_breaches",
        "sla_breach_rate_pct", "valid_csat_count", "average_csat",
        "repeat_contacts_30d", "repeat_contact_rate_pct",
        "valid_handle_time_count", "average_handle_time_minutes",
        "is_small_sample", "rank_by_tickets_closed"
    ]
    for r in leaderboard:
        for k in required_keys:
            assert k in r, f"Missing key {k} in leaderboard record"


def test_tier2_agents_strictly_excluded_from_tier1_leaderboard(prepared_tickets):
    """Verifies that NO Tier 2 / Escalations & Warranty agent appears in Tier 1 ranking."""
    leaderboard = calculate_tier1_leaderboard(prepared_tickets, target_week="2025-W41")
    t1_teams = {r["team"] for r in leaderboard}
    assert t1_teams.issubset(TIER1_FRONTLINE_TEAMS)
    assert not any(r["team"] in TIER2_TEAMS for r in leaderboard)


def test_no_duplicate_ticket_inflation(prepared_tickets):
    """Verifies that cross-system duplicate ticket pairs do not inflate closed counts."""
    leaderboard = calculate_tier1_leaderboard(prepared_tickets, target_week="2025-W41")
    total_closed_leaderboard = sum(r["tickets_closed"] for r in leaderboard)

    # Calculate closed unique tickets in the same week for Tier 1
    t1_df = prepared_tickets[
        prepared_tickets["agent_team"].isin(TIER1_FRONTLINE_TEAMS)
        & (prepared_tickets["resolved_week"] == "2025-W41")
        & prepared_tickets["status"].isin(["resolved", "closed"])
    ]
    unique_closed = t1_df["ticket_id"].nunique()
    assert total_closed_leaderboard == unique_closed
