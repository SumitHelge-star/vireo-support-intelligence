"""
Unit tests for complaint analysis, text preprocessing, clustering, and representative ticket extraction.
"""

import pytest
import pandas as pd
import numpy as np

from src.complaint_analysis.preprocessing import clean_text, preprocess_corpus
from src.complaint_analysis.clustering import (
    perform_complaint_clustering,
    generate_explainable_label,
    ComplaintCluster,
)
from src.complaint_analysis.representative_tickets import extract_representative_tickets


def test_clean_text_normalizes_and_strips_boilerplate():
    """Test that clean_text removes IVR tags, order codes, URLs, and support stopwords."""
    raw = "[IVR transcript] Hello sir, regarding order VR882661, my Pulse 2 bluetooth keeps cutting out. Please help!"
    cleaned = clean_text(raw)
    assert "ivr" not in cleaned
    assert "vr882661" not in cleaned
    assert "pulse" in cleaned
    assert "bluetooth" in cleaned
    assert "cutting" in cleaned
    assert "sir" not in cleaned
    assert "please" not in cleaned


def test_clean_text_edge_cases():
    """Test handling of None, NaN, empty strings, and numbers."""
    assert clean_text(None) == ""
    assert clean_text(np.nan) == ""
    assert clean_text("") == ""
    assert clean_text("   \n\t  ") == ""
    assert clean_text("12345 67890") == ""


def test_perform_complaint_clustering_basic():
    """Test clustering on sample complaint dataset."""
    df = pd.DataFrame({
        "ticket_id": [f"T{i}" for i in range(10)],
        "customer_message": [
            "My bluetooth keeps disconnecting on Pulse 2 earbuds",
            "Pairing issue with my phone and pulse earbuds",
            "Bluetooth cutting out during audio playback",
            "Battery drains in 2 hours on my smart watch",
            "Watch is not charging properly and battery drops",
            "Battery backup is very poor on watch",
            "Where is my courier package delivery is delayed",
            "Tracking says dispatched but delivery not arrived",
            "Courier delayed my shipment for 5 days",
            "Wrong invoice amount and GST number missing",
        ],
        "category": [
            "Connectivity", "Connectivity", "Connectivity",
            "Charging & Battery", "Charging & Battery", "Charging & Battery",
            "Delivery & Shipping", "Delivery & Shipping", "Delivery & Shipping",
            "Billing & Payments",
        ],
        "channel": ["chat"] * 10,
        "product_sku": ["VA-EB-PL2"] * 3 + ["VA-WT-ACT"] * 3 + ["VA-EB-PL1"] * 3 + ["VA-SP-ORB"],
        "csat_score": [4.0, 5.0, 3.0, 2.0, 1.0, 3.0, 4.0, 2.0, 1.0, 5.0],
        "is_sla_breached": [False, True, False, False, True, False, True, False, False, False],
    })

    clusters, df_clustered, kmeans, vectorizer = perform_complaint_clustering(
        df, n_clusters=3, random_state=42
    )

    assert len(clusters) == 3
    assert sum(c.ticket_count for c in clusters) == 10
    assert sum(c.percentage for c in clusters) == pytest.approx(100.0, rel=1e-2)
    assert "cluster_id" in df_clustered.columns

    # Test representative ticket extraction
    reps = extract_representative_tickets(df_clustered, clusters, vectorizer, kmeans, top_n=2)
    assert len(reps) == 3
    for c in clusters:
        assert len(c.representative_ticket_ids) <= 2
        assert len(c.representative_ticket_ids) > 0


def test_perform_complaint_clustering_empty_and_single():
    """Test graceful fallback for empty DataFrame or single record."""
    empty_df = pd.DataFrame(columns=["ticket_id", "customer_message", "category", "channel", "product_sku", "csat_score"])
    clusters_empty, _, _, _ = perform_complaint_clustering(empty_df)
    assert clusters_empty == []

    single_df = pd.DataFrame({
        "ticket_id": ["T1"],
        "customer_message": ["Need help with battery"],
        "category": ["Charging & Battery"],
        "channel": ["email"],
        "product_sku": ["VA-EB-PL1"],
        "csat_score": [4.0],
    })
    clusters_single, df_single, _, _ = perform_complaint_clustering(single_df, n_clusters=2)
    assert len(clusters_single) == 1
    assert clusters_single[0].ticket_count == 1
    assert clusters_single[0].percentage == 100.0
