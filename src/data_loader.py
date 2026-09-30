"""
Data loader module for Vireo Audio Support Intelligence.
Provides safe, validated loading of raw datasets without modifying original files.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd

from src.config import (
    RAW_DATA_DIR,
    RAW_TICKETS_FILE,
    RAW_AGENTS_FILE,
    RAW_CUSTOMERS_FILE,
    RAW_ORDERS_FILE,
    RAW_PRODUCTS_FILE,
    SCHEMA_TICKETS,
    SCHEMA_AGENTS,
    SCHEMA_CUSTOMERS,
    SCHEMA_ORDERS,
    SCHEMA_PRODUCTS,
)


class DataLoaderError(Exception):
    """Raised when data loading or initial schema verification fails."""
    pass


def verify_file_exists(file_path: Path) -> None:
    """Verifies that the specified file exists on disk."""
    if not file_path.exists():
        raise DataLoaderError(f"Required data file not found: {file_path}")
    if not file_path.is_file():
        raise DataLoaderError(f"Path exists but is not a file: {file_path}")
    if file_path.stat().st_size == 0:
        raise DataLoaderError(f"Data file is empty (0 bytes): {file_path}")


def validate_columns(df: pd.DataFrame, expected_columns: list[str], dataset_name: str) -> None:
    """Validates that a DataFrame contains the expected schema columns."""
    actual_columns = list(df.columns)
    missing = set(expected_columns) - set(actual_columns)
    extra = set(actual_columns) - set(expected_columns)
    
    if missing:
        raise DataLoaderError(
            f"Schema mismatch for {dataset_name}: Missing expected columns: {sorted(list(missing))}"
        )
    if extra:
        raise DataLoaderError(
            f"Schema mismatch for {dataset_name}: Unexpected extra columns: {sorted(list(extra))}"
        )


def load_tickets(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Loads tickets.csv safely.
    Preserves raw data without coercion.
    """
    path = file_path or RAW_TICKETS_FILE
    verify_file_exists(path)
    
    # Read without aggressive auto-conversion to keep raw types intact
    df = pd.read_csv(
        path,
        dtype={
            "ticket_id": str,
            "status": str,
            "channel": str,
            "customer_id": str,
            "order_id": str,
            "product_sku": str,
            "category": str,
            "priority": str,
            "assigned_team": str,
            "agent_id": str,
            "refund_reason_code": str,
            "replacement_issued": str,
            "customer_message": str,
            "agent_notes": str,
            "source_system": str,
        },
        keep_default_na=True,
    )
    
    validate_columns(df, SCHEMA_TICKETS, "tickets.csv")
    return df


def load_agents(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Loads agents.csv roster.
    Preserves multiple assignments per agent without deduplication.
    """
    path = file_path or RAW_AGENTS_FILE
    verify_file_exists(path)
    
    df = pd.read_csv(
        path,
        dtype={
            "agent_id": str,
            "name": str,
            "site": str,
            "team": str,
            "shift": str,
            "from_date": str,
            "to_date": str,
        },
        keep_default_na=True,
    )
    
    validate_columns(df, SCHEMA_AGENTS, "agents.csv")
    return df


def load_customers(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Loads customers.csv safely."""
    path = file_path or RAW_CUSTOMERS_FILE
    verify_file_exists(path)
    
    df = pd.read_csv(
        path,
        dtype={
            "customer_id": str,
            "name": str,
            "city": str,
            "state": str,
            "signup_date": str,
            "care_plus": str,
        },
        keep_default_na=True,
    )
    
    validate_columns(df, SCHEMA_CUSTOMERS, "customers.csv")
    return df


def load_orders(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Loads orders.csv safely."""
    path = file_path or RAW_ORDERS_FILE
    verify_file_exists(path)
    
    df = pd.read_csv(
        path,
        dtype={
            "order_id": str,
            "customer_id": str,
            "sku": str,
            "order_date": str,
            "channel": str,
            "lot_code": str,
        },
        keep_default_na=True,
    )
    
    validate_columns(df, SCHEMA_ORDERS, "orders.csv")
    return df


def load_products(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Loads products.csv safely."""
    path = file_path or RAW_PRODUCTS_FILE
    verify_file_exists(path)
    
    df = pd.read_csv(
        path,
        dtype={
            "sku": str,
            "product_name": str,
            "family": str,
            "launch_date": str,
        },
        keep_default_na=True,
    )
    
    validate_columns(df, SCHEMA_PRODUCTS, "products.csv")
    return df


def load_all_datasets(raw_dir: Optional[Path] = None) -> Dict[str, pd.DataFrame]:
    """Loads all five datasets into a dictionary."""
    base = raw_dir or RAW_DATA_DIR
    return {
        "tickets": load_tickets(base / "tickets.csv"),
        "agents": load_agents(base / "agents.csv"),
        "customers": load_customers(base / "customers.csv"),
        "orders": load_orders(base / "orders.csv"),
        "products": load_products(base / "products.csv"),
    }
