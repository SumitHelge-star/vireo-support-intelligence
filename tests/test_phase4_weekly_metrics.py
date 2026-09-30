"""
Tests for ISO Week Labeling, Scenario Wording, Trend Calculations, and Unified Payload.
"""

import pytest
import pandas as pd
from src.data_loader import load_all_datasets
from src.normalization import derive_ticket_features
from src.complaint_analysis.repeat_contact import calculate_repeat_contacts
from src.business_impact.roi_model import calculate_business_impact
from src.performance.weekly_leaderboard import build_weekly_performance_payload


@pytest.fixture(scope="module")
def prepared_data():
    datasets = load_all_datasets()
    df = derive_ticket_features(datasets["tickets"], datasets.get("orders"))
    df, _ = calculate_repeat_contacts(df)
    return df, datasets["agents"]


def test_iso_week_labeling_proof():
    """
    Test A1: Proves that dates 2025-10-06 through 2025-10-12 map to ISO week 2025-W41.
    """
    date_range = pd.date_range("2025-10-06", "2025-10-12")
    iso_weeks = date_range.strftime("%G-W%V").tolist()
    
    assert all(w == "2025-W41" for w in iso_weeks), f"Expected all 2025-W41, got {iso_weeks}"


def test_scenario_wording_labeled_as_assumptions(prepared_data):
    """
    Test A2: Verifies that scenario reduction parameters in BusinessImpactSummary are documented as assumptions.
    """
    df_tickets, _ = prepared_data
    impact = calculate_business_impact(df_tickets, tool_annual_cost_inr=0.0)
    
    obs_map = impact.observed_vs_assumed_parameters
    assert "ASSUMED" in obs_map["scenario_reduction_percentages"]
    assert "ASSUMED" in obs_map["sla_breach_reduction_linkage"]


def test_build_weekly_performance_payload_schema_and_trends(prepared_data):
    """
    Test Phase 4 Payload: Verifies unified weekly performance payload structure and WoW trends.
    """
    df_tickets, df_agents = prepared_data
    payload = build_weekly_performance_payload(
        df_tickets=df_tickets,
        df_agents=df_agents,
        target_week="2025-W41",
        previous_week="2025-W40",
    )

    assert payload["week"] == "2025-W41"
    assert "tier1_frontline_leaderboard" in payload
    assert "tier2_warranty_operational_summary" in payload
    assert "other_operational_teams" in payload
    assert "week_over_week_trends" in payload
    assert "data_quality_warnings" in payload

    trends = payload["week_over_week_trends"]
    assert trends["tier1_wow_deltas"] is not None
    assert "closed_delta" in trends["tier1_wow_deltas"]
    assert "sla_breach_rate_delta_pct" in trends["tier1_wow_deltas"]
