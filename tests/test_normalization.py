"""
Unit tests for normalization and feature engineering module.
Tests derived field calculations, CSAT sanitization, fallback order recovery, and raw file safety.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.normalization import derive_ticket_features, normalize_and_save_all
from src.data_loader import load_tickets
from src.config import RAW_TICKETS_FILE


def test_derive_ticket_features_calculations():
    """Test deterministic feature engineering on tickets."""
    df_tickets = pd.DataFrame({
        "ticket_id": ["TK-1", "TK-2", "TK-3"],
        "created_at": ["2025-01-10 10:00", "2025-02-15 14:00", "2025-03-20 09:00"],
        "first_response_at": ["2025-01-10 10:20", "2025-02-15 14:10", "2025-03-20 10:00"],
        "resolved_at": ["2025-01-10 12:00", "2025-02-15 13:00", None],  # TK-2 has resolved < first_resp
        "status": ["resolved", "resolved", "open"],
        "channel": ["chat", "email", "voice"],
        "customer_id": ["C1", "C2", "C3"],
        "order_id": ["O1", None, None],
        "product_sku": ["P1", "P2", "P3"],
        "category": ["Product", "Delivery", "Battery"],
        "priority": ["Normal", "High", "Low"],
        "assigned_team": ["Chat Frontline", "Logistics", "Voice Frontline"],
        "agent_id": ["A1", "A2", "A3"],
        "transfers": [0, 1, 0],
        "csat_score": [4.0, 0.0, np.nan],
        "refund_amount_inr": [np.nan, 1499.0, np.nan],
        "refund_reason_code": [np.nan, "RETURN-QC-OK", np.nan],
        "replacement_issued": ["N", "N", "N"],
        "customer_message": ["A", "B", "C"],
        "agent_notes": ["A", "B", "C"],
        "source_system": ["helpdesk", "legacy_fd", "helpdesk"],
    })

    df_orders = pd.DataFrame({
        "order_id": ["O2"],
        "customer_id": ["C2"],
        "sku": ["P2"],
        "order_date": ["2025-02-10"],
        "channel": ["Website"],
        "qty": [1],
        "order_value_inr": [1499],
        "lot_code": ["LOT-1"],
    })

    res = derive_ticket_features(df_tickets, df_orders)

    # Date partitions
    assert res.loc[0, "created_date"] == "2025-01-10"
    assert res.loc[0, "created_week"] == "2025-W02"
    assert res.loc[0, "created_month"] == "2025-01"

    # Response & Handle time
    assert res.loc[0, "first_response_minutes"] == 20.0
    assert res.loc[0, "handle_time_minutes"] == 100.0  # 12:00 - 10:20 = 100 mins
    # TK-2 had inverted timestamps, handle time should be NaN
    assert np.isnan(res.loc[1, "handle_time_minutes"])
    # TK-3 is open, handle time should be NaN
    assert np.isnan(res.loc[2, "handle_time_minutes"])

    # CSAT cleanup: 0 -> NaN
    assert res.loc[0, "csat_score_clean"] == 4.0
    assert np.isnan(res.loc[1, "csat_score_clean"])
    assert res.loc[0, "has_csat"] is True or res.loc[0, "has_csat"] == True
    assert res.loc[1, "has_csat"] == False

    # SLA targets and breaches
    assert res.loc[0, "sla_target_minutes"] == 15
    assert res.loc[0, "is_sla_breached"] == True  # 20 > 15
    assert res.loc[1, "sla_target_minutes"] == 480
    assert res.loc[1, "is_sla_breached"] == False  # 10 < 480

    # Inferred fallback order_id
    assert res.loc[1, "order_id_inferred"] == "O2"
    assert pd.isna(res.loc[2, "order_id_inferred"])


def test_raw_data_never_modified_by_normalization(tmp_path: Path):
    """Test that normalize_and_save_all writes only to processed_dir and raw data checksum is unchanged."""
    raw_tickets_before = load_tickets(RAW_TICKETS_FILE)
    
    datasets = {
        "tickets": raw_tickets_before,
        "agents": pd.read_csv("data/raw/agents.csv"),
        "customers": pd.read_csv("data/raw/customers.csv"),
        "orders": pd.read_csv("data/raw/orders.csv"),
        "products": pd.read_csv("data/raw/products.csv"),
    }
    
    processed_dir = tmp_path / "processed_test"
    normalize_and_save_all(datasets, processed_dir)
    
    # Verify outputs exist in target dir
    assert (processed_dir / "tickets_processed.csv").exists()
    assert (processed_dir / "agents_processed.csv").exists()
    assert (processed_dir / "customers_processed.csv").exists()
    assert (processed_dir / "orders_processed.csv").exists()
    assert (processed_dir / "products_processed.csv").exists()
    
    # Verify raw file unchanged
    raw_tickets_after = load_tickets(RAW_TICKETS_FILE)
    pd.testing.assert_frame_equal(raw_tickets_before, raw_tickets_after)
