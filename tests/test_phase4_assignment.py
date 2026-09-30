"""
Tests for Agent Assignment Resolution and Team Classification.
"""

import pytest
import pandas as pd
from src.data_loader import load_all_datasets
from src.normalization import derive_ticket_features
from src.performance.agent_assignment import (
    resolve_agent_assignment,
    TIER1_FRONTLINE_TEAMS,
    TIER2_TEAMS,
    OTHER_OPERATIONAL_TEAMS,
)


@pytest.fixture(scope="module")
def loaded_data():
    return load_all_datasets()


def test_agent_assignment_metadata_resolution(loaded_data):
    """Verifies agent names, sites, teams, and tiers are cleanly mapped to tickets."""
    df_tickets = derive_ticket_features(loaded_data["tickets"], loaded_data.get("orders"))
    resolved = resolve_agent_assignment(df_tickets, loaded_data["agents"])

    assert "agent_name" in resolved.columns
    assert "agent_site" in resolved.columns
    assert "agent_team" in resolved.columns
    assert "agent_tier" in resolved.columns
    assert resolved["agent_name"].isnull().sum() == 0
    assert (resolved["agent_name"] == "Unknown Agent").sum() == 0


def test_team_classification_separation(loaded_data):
    """Verifies that Tier 1, Tier 2, and Other Operational teams are mutually exclusive."""
    df_tickets = derive_ticket_features(loaded_data["tickets"], loaded_data.get("orders"))
    resolved = resolve_agent_assignment(df_tickets, loaded_data["agents"])

    # Mutually exclusive flags
    t1_count = resolved["is_tier1_frontline"].sum()
    t2_count = resolved["is_tier2_warranty"].sum()
    other_count = resolved["is_other_ops"].sum()

    assert t1_count + t2_count + other_count == len(resolved)
    assert resolved[resolved["is_tier1_frontline"]]["agent_team"].isin(TIER1_FRONTLINE_TEAMS).all()
    assert resolved[resolved["is_tier2_warranty"]]["agent_team"].isin(TIER2_TEAMS).all()
    assert resolved[resolved["is_other_ops"]]["agent_team"].isin(OTHER_OPERATIONAL_TEAMS).all()
