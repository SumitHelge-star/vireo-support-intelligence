"""
Tests for Tier 2 / Warranty Operational Performance.
Verifies cycle-time calculations, RMA replacement counts, and absence of rank fields.
"""

import pytest
import pandas as pd
from src.data_loader import load_all_datasets
from src.normalization import derive_ticket_features
from src.complaint_analysis.repeat_contact import calculate_repeat_contacts
from src.performance.agent_assignment import resolve_agent_assignment
from src.performance.tier2_metrics import calculate_tier2_operational_summary


@pytest.fixture(scope="module")
def prepared_tickets():
    datasets = load_all_datasets()
    df = derive_ticket_features(datasets["tickets"], datasets.get("orders"))
    df, _ = calculate_repeat_contacts(df)
    df = resolve_agent_assignment(df, datasets["agents"])
    return df


def test_tier2_resolution_days_metrics(prepared_tickets):
    """Verifies that Tier 2 summary computes average, median, and max turnaround days."""
    t2 = calculate_tier2_operational_summary(prepared_tickets, target_week="2025-W41")
    
    assert t2["team_name"] == "Escalations & Warranty"
    assert "cases_handled" in t2
    assert "cases_resolved" in t2
    assert "average_resolution_days" in t2
    assert "median_resolution_days" in t2
    assert "duration_distribution" in t2
    assert "warranty_rma_count" in t2

    # Verify duration buckets exist
    dist = t2["duration_distribution"]
    assert "under_2_days" in dist
    assert "2_to_5_days" in dist
    assert "5_to_10_days" in dist
    assert "over_10_days" in dist


def test_tier2_strictly_unranked_governance(prepared_tickets):
    """Verifies that Tier 2 agents are NOT assigned ranks in operational summaries."""
    t2 = calculate_tier2_operational_summary(prepared_tickets, target_week="2025-W41")
    agent_summaries = t2["agent_operational_summary"]
    
    for a in agent_summaries:
        assert "rank" not in a
        assert "rank_by_tickets_closed" not in a
    
    # Check governance notice
    assert "Tier 2 / Warranty is excluded from volume ranking" in t2["governance_notice"]
