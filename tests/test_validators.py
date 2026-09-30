"""
Unit tests for validators module.
Tests detection of duplicates, foreign keys, timestamp anomalies, and business policy violations.
"""

import pytest
import pandas as pd
import numpy as np

from src.validators import (
    audit_tickets,
    audit_timestamps,
    audit_agents,
    audit_customers,
    audit_products,
    audit_orders,
    audit_business_rules,
)


@pytest.fixture
def sample_tickets_df():
    return pd.DataFrame({
        "ticket_id": ["TK-101", "TK-101", "TK-102", "TK-103", None],
        "created_at": [
            "2025-01-01 10:00",
            "2025-01-01 10:00",
            "2025-01-02 11:00",
            "2025-01-03 12:00",
            "2025-01-04 13:00",
        ],
        "first_response_at": [
            "2025-01-01 10:10",
            "2025-01-01 10:10",
            "2025-01-02 11:20",
            "2025-01-03 12:30",
            "2025-01-04 13:40",
        ],
        "resolved_at": [
            "2025-01-01 11:00",
            "2025-01-01 08:00",  # Anomaly: resolved before created
            "2025-01-02 12:00",
            None,  # Open ticket
            "2025-01-04 15:00",
        ],
        "status": ["resolved", "resolved", "resolved", "open", "resolved"],
        "channel": ["chat", "chat", "email", "voice", "social"],
        "customer_id": ["C1", "C1", "C2", "C3", "C4"],
        "order_id": ["O1", "O1", None, "O3", "O4"],
        "product_sku": ["P1", "P1", "P2", "P3", "P4"],
        "category": ["Product", "Product", "Delivery", "Battery", "Account"],
        "priority": ["Normal", "Normal", "High", "Low", "Normal"],
        "assigned_team": ["Chat Frontline", "Chat Frontline", "Logistics", "Voice Frontline", "Chat Frontline"],
        "agent_id": ["A1", "A1", "A2", "A3", "A4"],
        "transfers": [0, 0, 1, 0, 0],
        "csat_score": [5.0, 0.0, np.nan, 4.0, 3.0],
        "refund_amount_inr": [np.nan, 2499.0, np.nan, np.nan, 600.0],
        "refund_reason_code": [np.nan, "DOA-REPL", np.nan, np.nan, "GW-OTHER"],
        "replacement_issued": ["N", "Y", "N", "N", "N"],
        "customer_message": ["Help", "Help", "Where is order", "Noise", "Login"],
        "agent_notes": ["Done", "Done", "Tracked", "Advised", "Reset"],
        "source_system": ["helpdesk", "legacy_fd", "helpdesk", "helpdesk", "helpdesk"],
    })


def test_audit_tickets_duplicates_and_nulls(sample_tickets_df):
    """Test that audit_tickets accurately flags duplicate IDs and missing values."""
    res = audit_tickets(sample_tickets_df)
    assert res["total_rows"] == 5
    assert res["unique_ticket_ids"] == 3
    assert res["missing_ticket_ids"] == 1
    assert res["duplicated_rows_count"] == 2
    assert res["duplicated_unique_ids"] == 1
    assert res["csat_zero_count"] == 1
    assert res["csat_null_count"] == 1


def test_audit_timestamps_anomalies(sample_tickets_df):
    """Test that timestamp validation detects resolved_at < created_at and SLA breaches."""
    res = audit_timestamps(sample_tickets_df)
    assert res["resolved_before_created_total"] == 1
    assert res["resolved_before_created_legacy"] == 1
    assert res["resolved_before_created_helpdesk"] == 0
    assert res["open_with_resolved_timestamp"] == 0
    assert res["resolved_missing_resolved_timestamp"] == 0


def test_audit_business_rules_violations(sample_tickets_df):
    """Test detection of dual refund+replacement and goodwill cap breaches."""
    agents_df = pd.DataFrame({
        "agent_id": ["A1", "A2", "A3", "A4"],
        "tier": [1, 2, 1, 1],
        "team": ["Chat Frontline", "Logistics", "Voice Frontline", "Chat Frontline"],
    })
    res = audit_business_rules(sample_tickets_df, agents_df)
    # Row 1 has refund 2499.0 and replacement 'Y'
    assert res["tickets_with_both_refund_and_replacement"] == 1
    # Row 4 has GW-OTHER refund of 600.0 > 500
    assert res["goodwill_refunds_exceeding_cap"] == 1
    assert res["replacements_by_tier1_agents"] == 1


def test_audit_orders_referential_integrity_and_fallback():
    """Test detection of unmatched foreign keys and ambiguous fallback order matches."""
    tickets_df = pd.DataFrame({
        "ticket_id": ["T1", "T2", "T3"],
        "customer_id": ["C1", "C2", "C3"],
        "product_sku": ["SKU1", "SKU2", "SKU3"],
        "order_id": ["O1", None, None],
    })
    customers_df = pd.DataFrame({"customer_id": ["C1", "C2", "C3"]})
    products_df = pd.DataFrame({"sku": ["SKU1", "SKU2", "SKU3"]})
    orders_df = pd.DataFrame({
        "order_id": ["O1", "O2_A", "O2_B"],
        "customer_id": ["C1", "C2", "C2"],  # C2 ordered SKU2 twice (ambiguous)
        "sku": ["SKU1", "SKU2", "SKU2"],
    })

    res = audit_orders(orders_df, customers_df, products_df, tickets_df)
    assert res["total_orders"] == 3
    assert res["tickets_with_order_id_count"] == 1
    assert res["tickets_without_order_id_count"] == 2
    assert res["fallback_unique_matches"] == 0
    assert res["fallback_ambiguous_matches"] == 1  # T2 matches O2_A and O2_B
    assert res["fallback_unmatched"] == 1           # T3 matches 0 orders

