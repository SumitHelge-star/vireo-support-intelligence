"""
Unit tests for data_loader module.
Tests schema validation, error handling, missing file detection, and raw data preservation.
"""

import pytest
import pandas as pd
from pathlib import Path

from src.data_loader import (
    load_tickets,
    load_agents,
    load_customers,
    load_orders,
    load_products,
    load_all_datasets,
    validate_columns,
    verify_file_exists,
    DataLoaderError,
)
from src.config import (
    RAW_DATA_DIR,
    RAW_TICKETS_FILE,
    RAW_AGENTS_FILE,
    RAW_CUSTOMERS_FILE,
    RAW_ORDERS_FILE,
    RAW_PRODUCTS_FILE,
    SCHEMA_TICKETS,
)


def test_verify_file_exists_nonexistent(tmp_path: Path):
    """Test that verify_file_exists raises DataLoaderError on missing file."""
    fake_file = tmp_path / "nonexistent.csv"
    with pytest.raises(DataLoaderError, match="Required data file not found"):
        verify_file_exists(fake_file)


def test_verify_file_exists_empty(tmp_path: Path):
    """Test that verify_file_exists raises DataLoaderError on empty file."""
    empty_file = tmp_path / "empty.csv"
    empty_file.touch()
    with pytest.raises(DataLoaderError, match="Data file is empty"):
        verify_file_exists(empty_file)


def test_validate_columns_missing_and_extra():
    """Test that validate_columns detects missing and unexpected columns."""
    df_missing = pd.DataFrame({"ticket_id": ["TK-1"], "status": ["resolved"]})
    with pytest.raises(DataLoaderError, match="Missing expected columns"):
        validate_columns(df_missing, SCHEMA_TICKETS, "test_dataset")

    df_extra = pd.DataFrame({col: ["val"] for col in SCHEMA_TICKETS})
    df_extra["extra_col"] = "unexpected"
    with pytest.raises(DataLoaderError, match="Unexpected extra columns"):
        validate_columns(df_extra, SCHEMA_TICKETS, "test_dataset")


def test_load_all_datasets_schema_and_types():
    """Test that load_all_datasets successfully loads all 5 datasets with exact schemas."""
    datasets = load_all_datasets(RAW_DATA_DIR)
    
    assert set(datasets.keys()) == {"tickets", "agents", "customers", "orders", "products"}
    
    assert len(datasets["tickets"]) == 12528
    assert len(datasets["agents"]) == 44
    assert len(datasets["customers"]) == 9500
    assert len(datasets["orders"]) == 15000
    assert len(datasets["products"]) == 14
    
    # Check that tickets data has expected columns
    for col in SCHEMA_TICKETS:
        assert col in datasets["tickets"].columns


def test_blank_order_id_is_allowed():
    """Test that blank order_id does not raise loader errors and loads as NaN/null."""
    df_tickets = load_tickets(RAW_TICKETS_FILE)
    assert df_tickets["order_id"].isnull().sum() == 4218


def test_multiple_agent_roster_rows_preserved():
    """Test that agents dataset maintains all roster entries without collapsing."""
    df_agents = load_agents(RAW_AGENTS_FILE)
    assert len(df_agents) == 44
    assert df_agents["agent_id"].nunique() == 44
    # All to_date are null (active assignments)
    assert df_agents["to_date"].isnull().sum() == 44
