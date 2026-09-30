"""
Unit tests for weekly digest generator and verifiable executive summarizer.
"""

import pytest
import pandas as pd
import numpy as np

from src.complaint_analysis.weekly_digest import generate_weekly_digest
from src.complaint_analysis.ai_summarizer import generate_executive_summary


@pytest.fixture
def sample_multiweek_tickets():
    return pd.DataFrame({
        "ticket_id": [f"TK-{100+i}" for i in range(12)],
        "created_at": [
            "2025-01-01 10:00", "2025-01-02 11:00", "2025-01-03 12:00", "2025-01-04 14:00", "2025-01-05 15:00", "2025-01-05 16:00", # Week 01 (6 tickets)
            "2025-01-06 09:00", "2025-01-07 10:00", "2025-01-08 11:00", "2025-01-09 12:00", "2025-01-10 13:00", "2025-01-11 14:00", # Week 02 (6 tickets)
        ],
        "first_response_at": [
            "2025-01-06 10:10", "2025-01-07 11:20", "2025-01-08 12:05", "2025-01-09 14:15", "2025-01-10 15:10", "2025-01-11 16:10",
            "2025-01-13 09:10", "2025-01-14 10:15", "2025-01-15 11:10", "2025-01-16 12:10", "2025-01-17 13:10", "2025-01-18 14:10",
        ],
        "resolved_at": [
            "2025-01-02 12:00", "2025-01-03 13:00", "2025-01-04 14:00", "2025-01-05 16:00", "2025-01-06 17:00", "2025-01-07 18:00",
            "2025-01-09 11:00", "2025-01-10 12:00", "2025-01-11 13:00", "2025-01-12 14:00", "2025-01-13 15:00", "2025-01-14 16:00",
        ],
        "customer_id": ["C1", "C2", "C3", "C4", "C5", "C6", "C1", "C7", "C8", "C9", "C10", "C11"],
        "product_sku": ["VA-EB-PL2", "VA-EB-PL2", "VA-WT-ACT", "VA-SP-ORB", "VA-EB-PL1", "VA-EB-PL2"] * 2,
        "category": ["Connectivity", "Connectivity", "Charging & Battery", "Audio Quality", "Delivery & Shipping", "Connectivity"] * 2,
        "channel": ["chat", "chat", "email", "voice", "social", "chat"] * 2,
        "assigned_team": ["Chat Frontline", "Chat Frontline", "Email Frontline", "Voice Frontline", "Chat Frontline", "Escalations & Warranty"] * 2,
        "agent_id": ["A3001", "A3002", "A3003", "A3004", "A3001", "A3010"] * 2,
        "csat_score": [4.0, 5.0, 3.0, np.nan, 2.0, 0.0] * 2,
        "customer_message": [
            "Bluetooth cutting out during calls",
            "Cannot pair with phone bluetooth",
            "Battery dying too quickly on watch",
            "Static noise in audio speaker",
            "Delivery delayed courier not moving",
            "Hardware broken replacement required",
        ] * 2,
        "status": ["resolved"] * 12,
        "source_system": ["helpdesk"] * 12,
    })


def test_generate_weekly_digest_metrics_and_traceability(sample_multiweek_tickets):
    """Test that weekly digest computes exact metrics, clusters, and WoW comparisons."""
    digest = generate_weekly_digest(sample_multiweek_tickets, target_week="2025-W02", previous_week="2025-W01", n_clusters=3)

    assert digest["target_week"] == "2025-W02"
    assert digest["total_tickets"] == 6
    assert len(digest["complaint_clusters"]) <= 3
    assert digest["tier2_warranty_ticket_count"] == 1

    # WoW comparison
    assert digest["wow_comparison"] is not None
    assert digest["wow_comparison"]["previous_week"] == "2025-W01"
    assert digest["wow_comparison"]["previous_volume"] == 6
    assert digest["wow_comparison"]["volume_change"] == 0

    # Executive summary generation test
    summary_text = generate_executive_summary(digest)
    assert "2025-W02" in summary_text
    assert "**Total Ticket Volume:** **6 tickets**" in summary_text
    assert "Priya Raman" in summary_text
    assert "Neha Kulkarni" in summary_text
    assert "Arjun Mehta" in summary_text
    assert "Tier 2 / Warranty Governance:" in summary_text
