"""
Comprehensive Automated Tests for Phase 5 Streamlit Dashboard and Integration.
"""

import pytest
import pandas as pd
from src.data_loader import load_all_datasets
from src.normalization import derive_ticket_features
from src.complaint_analysis.repeat_contact import calculate_repeat_contacts
from src.complaint_analysis.weekly_digest import generate_weekly_digest
from src.business_impact.roi_model import calculate_business_impact
from src.performance import (
    resolve_agent_assignment,
    build_weekly_performance_payload,
)


@pytest.fixture(scope="module")
def prepared_dashboard_data():
    datasets = load_all_datasets()
    df_tickets = derive_ticket_features(datasets["tickets"], datasets.get("orders"))
    df_tickets, repeat_summary = calculate_repeat_contacts(df_tickets)
    df_tickets = resolve_agent_assignment(df_tickets, datasets["agents"])
    financial_summary = calculate_business_impact(df_tickets, tool_annual_cost_inr=0.0)
    return df_tickets, datasets["agents"], datasets["products"], repeat_summary, financial_summary


def test_dashboard_components_import():
    """Test that all Streamlit UI components import cleanly."""
    from app.components import (
        render_kpi_cards,
        render_complaint_view,
        render_performance_view,
        render_tier2_view,
        render_finance_view,
    )
    assert render_kpi_cards is not None
    assert render_complaint_view is not None
    assert render_performance_view is not None
    assert render_tier2_view is not None
    assert render_finance_view is not None


def test_dashboard_kpi_calculations_match_pipeline(prepared_dashboard_data):
    """Test that dashboard KPI values match the underlying deterministic pipelines."""
    df_tickets, df_agents, _, _, financial_summary = prepared_dashboard_data
    test_week = "2025-W41"

    digest = generate_weekly_digest(df_tickets, target_week=test_week, n_clusters=5)
    perf = build_weekly_performance_payload(df_tickets, df_agents, target_week=test_week)

    assert digest["total_tickets"] == 203
    assert digest["repeat_contacts"]["count"] == 57
    assert len(perf["tier1_frontline_leaderboard"]) > 0

    # Verify financial base scenario matches Phase 3
    base_sc = financial_summary.scenarios["Base"]
    assert 94000 <= base_sc["total_annualized_gross_savings_inr"] <= 95000


def test_dashboard_tier2_never_ranked(prepared_dashboard_data):
    """Test that Tier 2 agents are strictly unranked in performance payload."""
    df_tickets, df_agents, _, _, _ = prepared_dashboard_data
    perf = build_weekly_performance_payload(df_tickets, df_agents, target_week="2025-W41")

    t2 = perf["tier2_warranty_operational_summary"]
    for agent in t2.get("agent_operational_summary", []):
        assert "rank" not in agent
        assert "rank_by_tickets_closed" not in agent


def test_dashboard_week_selection_consistency(prepared_dashboard_data):
    """Test that selecting different ISO weeks produces consistent, valid outputs."""
    df_tickets, df_agents, _, _, _ = prepared_dashboard_data

    w41_digest = generate_weekly_digest(df_tickets, target_week="2025-W41", n_clusters=5)
    w40_digest = generate_weekly_digest(df_tickets, target_week="2025-W40", n_clusters=5)

    assert w41_digest["target_week"] == "2025-W41"
    assert w40_digest["target_week"] == "2025-W40"
    assert w41_digest["total_tickets"] != w40_digest["total_tickets"]


def test_dashboard_first_week_wow_handled_gracefully(prepared_dashboard_data):
    """Test that the earliest week (no prior week) handles WoW comparison gracefully."""
    df_tickets, df_agents, _, _, _ = prepared_dashboard_data
    w01_digest = generate_weekly_digest(df_tickets, target_week="2025-W01", n_clusters=5)

    assert w01_digest["target_week"] == "2025-W01"
    assert w01_digest["wow_comparison"] is None or isinstance(w01_digest["wow_comparison"], dict)


def test_dashboard_small_sample_flagging(prepared_dashboard_data):
    """Test that frontline agents with <5 closed tickets receive small-sample warnings."""
    df_tickets, df_agents, _, _, _ = prepared_dashboard_data
    perf = build_weekly_performance_payload(df_tickets, df_agents, target_week="2025-W41")

    leaderboard = perf["tier1_frontline_leaderboard"]
    small_sample_agents = [a for a in leaderboard if a["tickets_closed"] < 5]
    for agent in small_sample_agents:
        assert agent["is_small_sample"] is True

    standard_agents = [a for a in leaderboard if a["tickets_closed"] >= 5]
    for agent in standard_agents:
        assert agent["is_small_sample"] is False


def test_dashboard_financial_scenarios_reconciliation(prepared_dashboard_data):
    """Verify that all financial scenario outputs match Phase 3 exact formulas."""
    _, _, _, _, financial_summary = prepared_dashboard_data
    
    # 5% Conservative
    sc_5 = financial_summary.scenarios["Conservative"]
    assert 47000 <= sc_5["total_annualized_gross_savings_inr"] <= 48000
    
    # 10% Base
    sc_10 = financial_summary.scenarios["Base"]
    assert 94000 <= sc_10["total_annualized_gross_savings_inr"] <= 95000
    
    # 20% Stretch
    sc_20 = financial_summary.scenarios["Stretch"]
    assert 188000 <= sc_20["total_annualized_gross_savings_inr"] <= 190000
    
    # Software cost is 0
    assert sc_10["tool_annual_cost_inr"] == 0.0
    assert sc_10["net_annual_benefit_inr"] == sc_10["total_annualized_gross_savings_inr"]


def test_complaint_view_renders_complaintcluster_objects_without_attribute_error(prepared_dashboard_data):
    """Regression test: render_complaint_view must accept ComplaintCluster dataclass objects without AttributeError."""
    from app.components.complaint_view import _get_cluster_field, render_complaint_view
    from src.complaint_analysis.clustering import ComplaintCluster

    df_tickets, _, _, _, _ = prepared_dashboard_data
    sample_cluster = ComplaintCluster(
        cluster_id=0,
        label="Bluetooth Connectivity (pairing, connect)",
        top_terms=["pairing", "connect", "bluetooth"],
        ticket_count=15,
        percentage=7.5,
        ticket_ids=["TK-1001", "TK-1002"],
        dominant_category="Technical",
        dominant_channel="chat",
        dominant_product="VA-EB-PL2",
        avg_csat=4.2,
        sla_breach_rate=5.0,
        representative_ticket_ids=["TK-1001", "TK-1002"],
    )

    # 1. Test field extractor with dataclass object
    assert _get_cluster_field(sample_cluster, "cluster_id") == 0
    assert _get_cluster_field(sample_cluster, "label") == "Bluetooth Connectivity (pairing, connect)"
    assert _get_cluster_field(sample_cluster, "representative_ticket_ids") == ["TK-1001", "TK-1002"]

    # 2. Test field extractor with dictionary
    sample_dict = {
        "cluster_id": 1,
        "label": "Battery Issue",
        "representative_ticket_ids": ["TK-2001"],
    }
    assert _get_cluster_field(sample_dict, "cluster_id") == 1
    assert _get_cluster_field(sample_dict, "label") == "Battery Issue"
    assert _get_cluster_field(sample_dict, "representative_ticket_ids") == ["TK-2001"]

    # 3. Test empty representative ticket list safe fallback
    empty_cluster = ComplaintCluster(
        cluster_id=2,
        label="Empty Evidence Topic",
        top_terms=["general"],
        ticket_count=1,
        percentage=0.5,
        ticket_ids=["TK-3001"],
        dominant_category="General",
        dominant_channel="email",
        dominant_product="VA-HP-WP",
        representative_ticket_ids=[],
    )
    assert _get_cluster_field(empty_cluster, "representative_ticket_ids") == []


