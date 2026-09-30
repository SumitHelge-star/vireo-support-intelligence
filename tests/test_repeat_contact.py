"""
Unit tests for repeat contact calculation and 30-day FCR policy compliance.
"""

import pytest
import pandas as pd
import numpy as np

from src.complaint_analysis.repeat_contact import calculate_repeat_contacts
from src.config import CONTACT_COSTS_INR


def test_calculate_repeat_contacts_30_day_window():
    """Test detection of repeat contacts within and outside 30-day window."""
    df_tickets = pd.DataFrame({
        "ticket_id": ["T1", "T2", "T3", "T4"],
        "customer_id": ["C100", "C100", "C100", "C200"],
        "product_sku": ["SKU1", "SKU1", "SKU2", "SKU3"],
        "category": ["Connectivity", "Connectivity", "Delivery", "Product"],
        "channel": ["chat", "voice", "email", "chat"],
        "created_at": [
            "2025-01-01 10:00",
            "2025-01-10 14:00",  # 9 days after T1 resolution (Repeat!)
            "2025-03-01 09:00",  # 49 days after T2 resolution (>30 days, Not a repeat)
            "2025-01-05 11:00",  # First ticket for C200 (Not a repeat)
        ],
        "resolved_at": [
            "2025-01-01 12:00",
            "2025-01-11 10:00",
            "2025-03-02 12:00",
            "2025-01-05 14:00",
        ],
    })

    df_res, summary = calculate_repeat_contacts(df_tickets, window_days=30)

    # T1 is first contact (False)
    assert df_res.loc[df_res["ticket_id"] == "T1", "is_repeat_contact"].values[0] == False
    # T2 is return within 9 days for same customer and SKU (True)
    assert df_res.loc[df_res["ticket_id"] == "T2", "is_repeat_contact"].values[0] == True
    assert df_res.loc[df_res["ticket_id"] == "T2", "repeat_match_type"].values[0] == "same_sku_and_category"
    assert df_res.loc[df_res["ticket_id"] == "T2", "repeat_contact_cost_inr"].values[0] == CONTACT_COSTS_INR["voice"]

    # T3 is return after 49 days (>30d window, False)
    assert df_res.loc[df_res["ticket_id"] == "T3", "is_repeat_contact"].values[0] == False
    # T4 is first contact for C200 (False)
    assert df_res.loc[df_res["ticket_id"] == "T4", "is_repeat_contact"].values[0] == False

    assert summary["total_tickets"] == 4
    assert summary["total_repeat_contacts"] == 1
    assert summary["repeat_contact_rate_pct"] == 25.0
    assert summary["total_repeat_cost_inr"] == CONTACT_COSTS_INR["voice"]
