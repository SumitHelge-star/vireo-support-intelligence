"""
Comprehensive Automated Test Suite for Phase 3: Business Impact, Financial ROI & Prior-Phase Verification.
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.data_loader import load_all_datasets
from src.normalization import derive_ticket_features
from src.complaint_analysis.repeat_contact import calculate_repeat_contacts
from src.complaint_analysis.clustering import perform_complaint_clustering
from src.business_impact.roi_model import calculate_business_impact
from src.config import (
    CONTACT_COSTS_INR,
    BLENDED_CONTACT_COST_INR,
    SLA_BREACH_STORE_CREDIT_INR,
)


@pytest.fixture(scope="module")
def loaded_data():
    return load_all_datasets()


@pytest.fixture(scope="module")
def normalized_tickets(loaded_data):
    return derive_ticket_features(loaded_data["tickets"], loaded_data.get("orders"))


def test_date_range_verification(normalized_tickets):
    """
    Test A1: Verifies the true physical date range of tickets.csv is 2025-01-01 to 2026-06-30.
    """
    df = normalized_tickets
    min_date = df["created_date"].min()
    max_date = df["created_date"].max()
    
    assert min_date == "2025-01-01", f"Expected min date 2025-01-01, got {min_date}"
    assert max_date == "2026-06-30", f"Expected max date 2026-06-30, got {max_date}"
    assert len(df) == 12528, f"Expected 12,528 total rows, got {len(df)}"
    assert df["ticket_id"].nunique() == 11875, f"Expected 11,875 unique ticket IDs, got {df['ticket_id'].nunique()}"


def test_channel_cost_calculation_vs_blended(normalized_tickets):
    """
    Test 9: Verifies channel-specific repeat contact costs and blended cross-check.
    """
    df, _ = calculate_repeat_contacts(normalized_tickets)
    repeats = df[df["is_repeat_contact"]]
    
    # Calculate exact channel cost sum
    expected_sum = (
        (repeats["channel"] == "chat").sum() * 210
        + (repeats["channel"] == "email").sum() * 260
        + (repeats["channel"] == "voice").sum() * 520
        + (repeats["channel"] == "social").sum() * 240
    )
    actual_sum = repeats["repeat_contact_cost_inr"].sum()
    
    assert actual_sum == expected_sum, f"Expected {expected_sum}, got {actual_sum}"
    assert actual_sum == 1020540, f"Expected Rs 1,020,540, got {actual_sum}"
    
    blended_sum = len(repeats) * BLENDED_CONTACT_COST_INR
    assert blended_sum == 1098520, f"Expected blended Rs 1,098,520, got {blended_sum}"
    assert blended_sum > actual_sum, "Blended cost should exceed channel sum due to Chat volume weight"


def test_sla_breach_liability_deterministic(normalized_tickets):
    """
    Test 10: Verifies deterministic SLA breach calculation and ₹350 store credit liability.
    """
    df = normalized_tickets
    breaches = df[df["is_sla_breached"]]
    
    assert len(breaches) == 1119, f"Expected 1,119 SLA breaches, got {len(breaches)}"
    total_liability = len(breaches) * SLA_BREACH_STORE_CREDIT_INR
    assert total_liability == 391650, f"Expected Rs 391,650 liability, got {total_liability}"


def test_business_impact_scenarios_and_annualization(normalized_tickets):
    """
    Test 11 & 12: Verifies Conservative (5%), Base (10%), Stretch (20%) scenario savings and annualization.
    """
    impact = calculate_business_impact(normalized_tickets, tool_annual_cost_inr=0.0)
    
    # Check baseline totals
    assert impact.total_tickets == 12528
    assert impact.total_repeat_contacts == 3788
    assert impact.repeat_contact_rate == 30.24
    assert impact.total_sla_breaches == 1119
    
    # Check Base Scenario (10%)
    base = impact.scenarios["Base"]
    assert base["reduction_percentage"] == 10.0
    assert base["avoided_repeat_contacts_18m"] == 379
    assert base["avoided_repeat_cost_18m_inr"] == 102054.0
    assert base["avoided_sla_breaches_18m"] == 112
    assert base["avoided_sla_liability_18m_inr"] == 39165.0
    assert base["total_gross_savings_18m_inr"] == 141219.0
    
    # Check annualization (approx 1.5 years)
    assert 94000 <= base["total_annualized_gross_savings_inr"] <= 95000


def test_roi_and_break_even_modeling(normalized_tickets):
    """
    Test 13 & 14: Verifies ROI formulas, zero tool cost handling, and non-zero tool cost evaluation.
    """
    # Case A: Free / zero tool cost
    free_impact = calculate_business_impact(normalized_tickets, tool_annual_cost_inr=0.0)
    base_free = free_impact.scenarios["Base"]
    assert base_free["tool_annual_cost_inr"] == 0.0
    assert base_free["roi_percentage"] is None
    assert base_free["payback_period_months"] == 0.0
    assert base_free["net_annual_benefit_inr"] == base_free["total_annualized_gross_savings_inr"]
    
    # Case B: Hypothetical paid software cost (e.g. Rs 30,000 / year)
    paid_impact = calculate_business_impact(normalized_tickets, tool_annual_cost_inr=30000.0)
    base_paid = paid_impact.scenarios["Base"]
    assert base_paid["tool_annual_cost_inr"] == 30000.0
    assert base_paid["net_annual_benefit_inr"] > 64000
    assert base_paid["roi_percentage"] > 200.0
    assert base_paid["payback_period_months"] < 4.0


def test_no_double_counting_safeguard(normalized_tickets):
    """
    Test 15: Verifies that repeat contact costs and SLA penalty credits remain separate line items.
    """
    impact = calculate_business_impact(normalized_tickets, tool_annual_cost_inr=0.0)
    base = impact.scenarios["Base"]
    
    # Sum of individual savings must equal total gross savings exactly
    component_sum = base["avoided_repeat_cost_18m_inr"] + base["avoided_sla_liability_18m_inr"]
    assert base["total_gross_savings_18m_inr"] == pytest.approx(component_sum, 0.01)
