"""
Normalization and feature derivation module for Vireo Audio Support Intelligence.
Computes deterministic derived fields and exports processed datasets without altering raw sources.
"""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import numpy as np

from src.config import (
    PROCESSED_DATA_DIR,
    PROCESSED_TICKETS_FILE,
    PROCESSED_AGENTS_FILE,
    PROCESSED_CUSTOMERS_FILE,
    PROCESSED_ORDERS_FILE,
    PROCESSED_PRODUCTS_FILE,
    SLA_TARGET_MINUTES,
)


def derive_ticket_features(
    df_tickets: pd.DataFrame, df_orders: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Computes deterministic derived fields for support tickets.
    Ensures safe, reproducible transformations and preserves policy constraints.
    """
    df = df_tickets.copy()
    
    # 1. Parse timestamps
    df["created_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["first_response_dt"] = pd.to_datetime(df["first_response_at"], errors="coerce")
    df["resolved_dt"] = pd.to_datetime(df["resolved_at"], errors="coerce")
    
    # 2. Date and interval partitions
    df["created_date"] = df["created_dt"].dt.strftime("%Y-%m-%d")
    df["created_week"] = df["created_dt"].dt.strftime("%G-W%V")
    df["created_month"] = df["created_dt"].dt.strftime("%Y-%m")
    
    df["resolved_date"] = df["resolved_dt"].dt.strftime("%Y-%m-%d")
    df["resolved_week"] = df["resolved_dt"].dt.strftime("%G-W%V")
    
    # 3. Response and handle time (in minutes)
    df["first_response_minutes"] = (
        (df["first_response_dt"] - df["created_dt"]).dt.total_seconds() / 60.0
    ).round(2)
    
    # For handle time: only valid when resolved_dt >= first_response_dt
    valid_handle_mask = (
        df["resolved_dt"].notnull()
        & (df["resolved_dt"] >= df["first_response_dt"])
    )
    df["handle_time_minutes"] = np.nan
    df.loc[valid_handle_mask, "handle_time_minutes"] = (
        (df.loc[valid_handle_mask, "resolved_dt"] - df.loc[valid_handle_mask, "first_response_dt"]).dt.total_seconds() / 60.0
    ).round(2)
    
    # 4. Status flags
    df["is_resolved_or_closed"] = df["status"].isin(["resolved", "closed"])
    df["is_legacy"] = df["source_system"] == "legacy_fd"
    
    # 5. CSAT cleanup: per policy v3.2, 0 is legacy no-response and must not be treated as 0
    df["csat_score_clean"] = df["csat_score"].copy()
    df.loc[df["csat_score_clean"] == 0, "csat_score_clean"] = np.nan
    df["has_csat"] = df["csat_score_clean"].notnull()
    
    # 6. Refund and replacement flags
    df["has_refund"] = df["refund_amount_inr"].fillna(0) > 0
    df["has_replacement"] = df["replacement_issued"] == "Y"
    df["has_order_id"] = df["order_id"].notnull()
    
    # 7. SLA targets and breach determination
    df["sla_target_minutes"] = df["channel"].map(SLA_TARGET_MINUTES)
    df["is_sla_breached"] = df["first_response_minutes"] > df["sla_target_minutes"]
    
    # 8. Deterministic Fallback Order Resolution
    # When order_id is missing, check if customer_id + product_sku uniquely resolves in orders.csv
    df["order_id_inferred"] = pd.Series(index=df.index, dtype=object)
    if df_orders is not None:
        order_sku_counts = df_orders.groupby(["customer_id", "sku"]).size().reset_index(name="_count")
        unique_pairs = order_sku_counts[order_sku_counts["_count"] == 1]
        unique_order_map = df_orders.merge(
            unique_pairs[["customer_id", "sku"]], on=["customer_id", "sku"]
        ).set_index(["customer_id", "sku"])["order_id"].to_dict()
        
        no_order_mask = df["order_id"].isnull()
        pairs = list(zip(df.loc[no_order_mask, "customer_id"], df.loc[no_order_mask, "product_sku"]))
        inferred_values = [unique_order_map.get(p, np.nan) for p in pairs]
        df.loc[no_order_mask, "order_id_inferred"] = inferred_values
            
    return df


def normalize_and_save_all(
    datasets: Dict[str, pd.DataFrame], output_dir: Optional[Path] = None
) -> Dict[str, pd.DataFrame]:
    """
    Normalizes all datasets, generates derived fields, and writes to processed directory.
    Original raw files are left untouched.
    """
    out_dir = output_dir or PROCESSED_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    
    processed_tickets = derive_ticket_features(
        datasets["tickets"], datasets.get("orders")
    )
    processed_agents = datasets["agents"].copy()
    processed_customers = datasets["customers"].copy()
    processed_orders = datasets["orders"].copy()
    processed_products = datasets["products"].copy()
    
    # Save to disk
    processed_tickets.to_csv(out_dir / "tickets_processed.csv", index=False)
    processed_agents.to_csv(out_dir / "agents_processed.csv", index=False)
    processed_customers.to_csv(out_dir / "customers_processed.csv", index=False)
    processed_orders.to_csv(out_dir / "orders_processed.csv", index=False)
    processed_products.to_csv(out_dir / "products_processed.csv", index=False)
    
    return {
        "tickets": processed_tickets,
        "agents": processed_agents,
        "customers": processed_customers,
        "orders": processed_orders,
        "products": processed_products,
    }
