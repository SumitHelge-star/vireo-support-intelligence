"""
Unit tests for audit orchestration module and CLI execution.
Tests report generation, findings aggregation, and end-to-end audit execution.
"""

import pytest
import pandas as pd
from pathlib import Path

from src.data_loader import load_all_datasets
from src.audit import run_full_audit, generate_markdown_report
from src.config import RAW_DATA_DIR, REPORTS_DIR


def test_run_full_audit_structure():
    """Test that run_full_audit returns all expected audit sections and non-empty metrics."""
    datasets = load_all_datasets(RAW_DATA_DIR)
    audit_res = run_full_audit(datasets)

    expected_keys = {
        "tickets",
        "timestamps",
        "agents",
        "customers",
        "products",
        "orders",
        "business_rules",
    }
    assert set(audit_res.keys()) == expected_keys

    # Check key ticket metrics on real data
    assert audit_res["tickets"]["total_rows"] == 12528
    assert audit_res["tickets"]["unique_ticket_ids"] == 11875
    assert audit_res["tickets"]["duplicated_unique_ids"] == 653
    assert audit_res["tickets"]["duplicated_rows_count"] == 1306

    # Check customer & product integrity on real data
    assert audit_res["customers"]["unmatched_ticket_customers_count"] == 0
    assert audit_res["products"]["unmatched_ticket_skus_count"] == 0
    assert audit_res["orders"]["invalid_ticket_order_ids_count"] == 0

    # Check fallback resolution numbers on real data (row-level mutually exclusive & collectively exhaustive)
    assert audit_res["orders"]["fallback_unique_matches"] == 3467
    assert audit_res["orders"]["fallback_ambiguous_matches"] == 751
    assert audit_res["orders"]["fallback_unmatched"] == 0
    assert (
        audit_res["orders"]["fallback_unique_matches"]
        + audit_res["orders"]["fallback_ambiguous_matches"]
        + audit_res["orders"]["fallback_unmatched"]
    ) == audit_res["orders"]["tickets_without_order_id_count"]


def test_generate_markdown_report(tmp_path: Path):
    """Test that generate_markdown_report creates a valid markdown report with required sections."""
    datasets = load_all_datasets(RAW_DATA_DIR)
    audit_res = run_full_audit(datasets)

    report_file = tmp_path / "test_report.md"
    generate_markdown_report(audit_res, report_file)

    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")

    assert "# Vireo Audio Customer Support Intelligence" in content
    assert "1. Executive Summary" in content
    assert "2. Dataset Topologies & Record Counts" in content
    assert "3. Schema & Column Validation" in content
    assert "4. Referential Integrity & Fallback Order Resolution" in content
    assert "5. Timestamp Quality & Migration Reconstruction Analysis" in content
    assert "6. Channel SLAs & Response Performance Audit" in content
    assert "7. Business Policy & Governance Compliance Findings" in content
    assert "8. Structured Finding Catalog" in content
    assert "9. Normalization Decisions & Derived Fields Catalog" in content
    assert "10. Downstream Directives for Phase 2+" in content
