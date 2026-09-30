"""
Configuration module for Vireo Audio Support Intelligence.
Contains file paths, expected schemas, policy parameters, and audit constants.
"""

from pathlib import Path
from typing import Dict, List

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DOCS_DIR = BASE_DIR / "docs"
REPORTS_DIR = BASE_DIR / "reports"

# Raw file paths
RAW_TICKETS_FILE = RAW_DATA_DIR / "tickets.csv"
RAW_AGENTS_FILE = RAW_DATA_DIR / "agents.csv"
RAW_CUSTOMERS_FILE = RAW_DATA_DIR / "customers.csv"
RAW_ORDERS_FILE = RAW_DATA_DIR / "orders.csv"
RAW_PRODUCTS_FILE = RAW_DATA_DIR / "products.csv"
SUPPORT_POLICY_PDF = DOCS_DIR / "support-policy.pdf"

# Processed output paths
PROCESSED_TICKETS_FILE = PROCESSED_DATA_DIR / "tickets_processed.csv"
PROCESSED_AGENTS_FILE = PROCESSED_DATA_DIR / "agents_processed.csv"
PROCESSED_CUSTOMERS_FILE = PROCESSED_DATA_DIR / "customers_processed.csv"
PROCESSED_ORDERS_FILE = PROCESSED_DATA_DIR / "orders_processed.csv"
PROCESSED_PRODUCTS_FILE = PROCESSED_DATA_DIR / "products_processed.csv"

# Expected Schemas per README.txt and source specifications
SCHEMA_TICKETS: List[str] = [
    "ticket_id",
    "created_at",
    "first_response_at",
    "resolved_at",
    "status",
    "channel",
    "customer_id",
    "order_id",
    "product_sku",
    "category",
    "priority",
    "assigned_team",
    "agent_id",
    "transfers",
    "csat_score",
    "refund_amount_inr",
    "refund_reason_code",
    "replacement_issued",
    "customer_message",
    "agent_notes",
    "source_system",
]

SCHEMA_AGENTS: List[str] = [
    "agent_id",
    "name",
    "site",
    "team",
    "shift",
    "tier",
    "from_date",
    "to_date",
]

SCHEMA_CUSTOMERS: List[str] = [
    "customer_id",
    "name",
    "city",
    "state",
    "signup_date",
    "care_plus",
]

SCHEMA_ORDERS: List[str] = [
    "order_id",
    "customer_id",
    "sku",
    "order_date",
    "channel",
    "qty",
    "order_value_inr",
    "lot_code",
]

SCHEMA_PRODUCTS: List[str] = [
    "sku",
    "product_name",
    "family",
    "launch_date",
    "unit_cost_inr",
    "retail_price_inr",
    "warranty_months",
]

# Business Rules & Support Operating Policy v3.2 Constants
SLA_TARGET_MINUTES: Dict[str, int] = {
    "chat": 15,
    "voice": 120,    # 2 hours
    "social": 240,   # 4 hours
    "email": 480,    # 8 hours
}

SLA_BREACH_STORE_CREDIT_INR = 350

# FY26 Fully Loaded Planning Contact Costs (INR)
CONTACT_COSTS_INR: Dict[str, int] = {
    "chat": 210,
    "email": 260,
    "voice": 520,
    "social": 240,
    "blended": 290,
}

BLENDED_CONTACT_COST_INR = 290
INTERNAL_TRANSFER_COST_INR = 305
AGENT_HOURLY_COST_INR = 165
AGENT_HOURLY_LOADED_COST_INR = 165
SHIFT_HOURS = 8
GOODWILL_CREDIT_CAP_INR = 500
REPLACEMENT_SHIPPING_LOGISTICS_INR = 340

# Valid Domains
VALID_STATUSES = {"resolved", "closed", "open", "pending"}
VALID_CHANNELS = {"chat", "email", "voice", "social"}
VALID_PRIORITIES = {"Low", "Normal", "High"}
VALID_SOURCE_SYSTEMS = {"helpdesk", "legacy_fd"}
VALID_REPLACEMENT_FLAGS = {"Y", "N"}
VALID_CARE_PLUS_FLAGS = {"Y", "N"}
VALID_REFUND_REASONS = {
    "GW-OTHER",
    "DOA-REPL",
    "LOST-TRANSIT",
    "DUP-PAYMENT",
    "CANCEL",
    "PRICE-ADJ",
    "RETURN-QC-OK",
    "WTY-BUYBACK",
}
VALID_SHIFTS = {"Morning", "Day", "Night"}
VALID_SITES = {"Bengaluru", "Indore"}
VALID_TIERS = {1, 2, "Tier 1", "Tier 2"}

# Migration & Re-import boundary
MIGRATION_DATE = "2025-09-14"
