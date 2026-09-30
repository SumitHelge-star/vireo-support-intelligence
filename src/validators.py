"""
Validators module for Vireo Audio Support Intelligence.
Performs comprehensive data quality checks, schema audits, referential integrity tests,
timestamp consistency analysis, and business rule compliance audits.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

from src.config import (
    SLA_TARGET_MINUTES,
    VALID_STATUSES,
    VALID_CHANNELS,
    VALID_PRIORITIES,
    VALID_SOURCE_SYSTEMS,
    VALID_REPLACEMENT_FLAGS,
    VALID_CARE_PLUS_FLAGS,
    VALID_REFUND_REASONS,
    VALID_SHIFTS,
    VALID_SITES,
    GOODWILL_CREDIT_CAP_INR,
    MIGRATION_DATE,
)


def audit_tickets(df: pd.DataFrame) -> Dict[str, Any]:
    """Audits tickets dataset for volume, completeness, duplicates, and domains."""
    total_rows = len(df)
    unique_ids = df["ticket_id"].nunique()
    missing_ids = df["ticket_id"].isnull().sum()
    
    dup_mask = df.duplicated(subset=["ticket_id"], keep=False)
    dup_rows = df[dup_mask]
    dup_count = len(dup_rows)
    dup_unique_ids = dup_rows["ticket_id"].nunique()
    
    # Analyze duplicate pairs across source systems
    dup_by_source = dup_rows["source_system"].value_counts().to_dict()
    
    # Missing rates
    missing_counts = df.isnull().sum().to_dict()
    missing_rates = {k: round((v / total_rows) * 100, 2) for k, v in missing_counts.items()}
    
    # Status distribution
    status_dist = df["status"].value_counts(dropna=False).to_dict()
    invalid_statuses = df[~df["status"].isin(VALID_STATUSES)]["status"].tolist()
    
    # Channel distribution
    channel_dist = df["channel"].value_counts(dropna=False).to_dict()
    invalid_channels = df[~df["channel"].isin(VALID_CHANNELS)]["channel"].tolist()
    
    # Priority distribution
    priority_dist = df["priority"].value_counts(dropna=False).to_dict()
    invalid_priorities = df[~df["priority"].isin(VALID_PRIORITIES)]["priority"].tolist()
    
    # Source system distribution
    source_dist = df["source_system"].value_counts(dropna=False).to_dict()
    invalid_sources = df[~df["source_system"].isin(VALID_SOURCE_SYSTEMS)]["source_system"].tolist()
    
    # CSAT breakdown
    csat_counts = df["csat_score"].value_counts(dropna=False).to_dict()
    csat_zero_count = int((df["csat_score"] == 0).sum())
    csat_null_count = int(df["csat_score"].isnull().sum())
    csat_valid_survey = df[df["csat_score"].isin([1, 2, 3, 4, 5])]
    csat_response_rate = round((len(csat_valid_survey) / total_rows) * 100, 2)
    
    # Refund and Replacement
    repl_dist = df["replacement_issued"].value_counts(dropna=False).to_dict()
    refund_counts = df["refund_reason_code"].value_counts(dropna=False).to_dict()
    invalid_refund_reasons = df[
        df["refund_reason_code"].notnull() & ~df["refund_reason_code"].isin(VALID_REFUND_REASONS)
    ]["refund_reason_code"].tolist()
    
    return {
        "total_rows": total_rows,
        "unique_ticket_ids": unique_ids,
        "missing_ticket_ids": int(missing_ids),
        "duplicated_rows_count": dup_count,
        "duplicated_unique_ids": dup_unique_ids,
        "duplicates_by_source": dup_by_source,
        "missing_counts": missing_counts,
        "missing_rates_pct": missing_rates,
        "status_distribution": status_dist,
        "invalid_statuses": invalid_statuses,
        "channel_distribution": channel_dist,
        "invalid_channels": invalid_channels,
        "priority_distribution": priority_dist,
        "invalid_priorities": invalid_priorities,
        "source_distribution": source_dist,
        "invalid_sources": invalid_sources,
        "csat_breakdown": csat_counts,
        "csat_zero_count": csat_zero_count,
        "csat_null_count": csat_null_count,
        "csat_valid_response_rate_pct": csat_response_rate,
        "replacement_distribution": repl_dist,
        "refund_reason_distribution": refund_counts,
        "invalid_refund_reasons": invalid_refund_reasons,
    }


def audit_timestamps(df: pd.DataFrame) -> Dict[str, Any]:
    """Audits timestamp consistency, chronological integrity, and migration artifacts."""
    created = pd.to_datetime(df["created_at"], errors="coerce")
    first_resp = pd.to_datetime(df["first_response_at"], errors="coerce")
    resolved = pd.to_datetime(df["resolved_at"], errors="coerce")
    
    created_unparseable = int(created.isnull().sum())
    first_resp_unparseable = int(first_resp.isnull().sum())
    # resolved_at is legitimately missing for open/pending tickets
    
    # Open/pending vs resolved_at checks
    open_pending_mask = df["status"].isin(["open", "pending"])
    resolved_closed_mask = df["status"].isin(["resolved", "closed"])
    
    open_with_resolved = int((open_pending_mask & df["resolved_at"].notnull()).sum())
    resolved_without_resolved = int((resolved_closed_mask & df["resolved_at"].isnull()).sum())
    
    # Chronological comparisons
    # 1. First response before created
    first_resp_before_created = int((first_resp < created).sum())
    
    # 2. Resolved before created
    resolved_before_created_mask = (resolved.notnull()) & (resolved < created)
    resolved_before_created_total = int(resolved_before_created_mask.sum())
    resolved_before_created_legacy = int(
        (resolved_before_created_mask & (df["source_system"] == "legacy_fd")).sum()
    )
    resolved_before_created_helpdesk = int(
        (resolved_before_created_mask & (df["source_system"] == "helpdesk")).sum()
    )
    
    # 3. Resolved before first response
    resolved_before_first_resp_mask = (resolved.notnull()) & (resolved < first_resp)
    resolved_before_first_resp_total = int(resolved_before_first_resp_mask.sum())
    resolved_before_first_resp_legacy = int(
        (resolved_before_first_resp_mask & (df["source_system"] == "legacy_fd")).sum()
    )
    resolved_before_first_resp_helpdesk = int(
        (resolved_before_first_resp_mask & (df["source_system"] == "helpdesk")).sum()
    )
    
    # SLA breaches
    resp_minutes = (first_resp - created).dt.total_seconds() / 60.0
    sla_breaches_by_channel = {}
    for ch, target in SLA_TARGET_MINUTES.items():
        ch_mask = df["channel"] == ch
        breached = (resp_minutes > target) & ch_mask
        sla_breaches_by_channel[ch] = {
            "total_tickets": int(ch_mask.sum()),
            "breached_count": int(breached.sum()),
            "breach_rate_pct": round((breached.sum() / ch_mask.sum()) * 100, 2) if ch_mask.sum() > 0 else 0.0,
            "target_minutes": target,
        }
    
    return {
        "created_unparseable": created_unparseable,
        "first_resp_unparseable": first_resp_unparseable,
        "open_with_resolved_timestamp": open_with_resolved,
        "resolved_missing_resolved_timestamp": resolved_without_resolved,
        "first_resp_before_created": first_resp_before_created,
        "resolved_before_created_total": resolved_before_created_total,
        "resolved_before_created_legacy": resolved_before_created_legacy,
        "resolved_before_created_helpdesk": resolved_before_created_helpdesk,
        "resolved_before_first_resp_total": resolved_before_first_resp_total,
        "resolved_before_first_resp_legacy": resolved_before_first_resp_legacy,
        "resolved_before_first_resp_helpdesk": resolved_before_first_resp_helpdesk,
        "sla_breaches_by_channel": sla_breaches_by_channel,
    }


def audit_agents(df_agents: pd.DataFrame, df_tickets: pd.DataFrame) -> Dict[str, Any]:
    """Audits agent roster, multiple assignments, and ticket volume distributions."""
    total_roster_rows = len(df_agents)
    unique_agent_ids = df_agents["agent_id"].nunique()
    
    # Check multiple assignments per agent_id
    assignment_counts = df_agents["agent_id"].value_counts()
    agents_with_multiple_rows = int((assignment_counts > 1).sum())
    
    # Missing checks
    missing_fields = df_agents.isnull().sum().to_dict()
    
    # Check dates
    from_dates = pd.to_datetime(df_agents["from_date"], errors="coerce")
    to_dates = pd.to_datetime(df_agents["to_date"], errors="coerce")
    invalid_from = int(from_dates.isnull().sum())
    
    # Active vs inactive
    active_assignments = int(df_agents["to_date"].isnull().sum())
    
    # Site, team, tier, shift distribution
    site_dist = df_agents["site"].value_counts().to_dict()
    team_dist = df_agents["team"].value_counts().to_dict()
    shift_dist = df_agents["shift"].value_counts().to_dict()
    tier_dist = df_agents["tier"].value_counts().to_dict()
    
    # Tickets referencing agents
    ticket_agents = set(df_tickets["agent_id"].dropna())
    roster_agents = set(df_agents["agent_id"])
    
    missing_in_roster = ticket_agents - roster_agents
    agents_with_no_tickets = roster_agents - ticket_agents
    
    return {
        "total_roster_rows": total_roster_rows,
        "unique_agents_count": unique_agent_ids,
        "agents_with_multiple_assignments": agents_with_multiple_rows,
        "active_assignments_count": active_assignments,
        "missing_fields": missing_fields,
        "invalid_from_dates": invalid_from,
        "site_distribution": site_dist,
        "team_distribution": team_dist,
        "shift_distribution": shift_dist,
        "tier_distribution": tier_dist,
        "ticket_agents_missing_in_roster": list(missing_in_roster),
        "agents_with_zero_tickets": list(agents_with_no_tickets),
    }


def audit_customers(df_customers: pd.DataFrame, df_tickets: pd.DataFrame) -> Dict[str, Any]:
    """Audits customers dataset and ticket linkage."""
    total_customers = len(df_customers)
    unique_ids = df_customers["customer_id"].nunique()
    missing_ids = int(df_customers["customer_id"].isnull().sum())
    
    care_plus_dist = df_customers["care_plus"].value_counts(dropna=False).to_dict()
    city_count = df_customers["city"].nunique()
    state_count = df_customers["state"].nunique()
    
    # Date validation
    signup_dates = pd.to_datetime(df_customers["signup_date"], errors="coerce")
    invalid_signups = int(signup_dates.isnull().sum())
    
    # Referential integrity from tickets
    ticket_cust = set(df_tickets["customer_id"].dropna())
    valid_cust = set(df_customers["customer_id"])
    unmatched_ticket_customers = list(ticket_cust - valid_cust)
    
    return {
        "total_customers": total_customers,
        "unique_customer_ids": unique_ids,
        "missing_customer_ids": missing_ids,
        "care_plus_distribution": care_plus_dist,
        "unique_cities": city_count,
        "unique_states": state_count,
        "invalid_signup_dates": invalid_signups,
        "unmatched_ticket_customers_count": len(unmatched_ticket_customers),
    }


def audit_products(df_products: pd.DataFrame, df_tickets: pd.DataFrame) -> Dict[str, Any]:
    """Audits product catalog and price integrity."""
    total_products = len(df_products)
    unique_skus = df_products["sku"].nunique()
    
    # Financial checks
    negative_cost = int((df_products["unit_cost_inr"] <= 0).sum())
    negative_price = int((df_products["retail_price_inr"] <= 0).sum())
    cost_exceeds_retail = int((df_products["unit_cost_inr"] > df_products["retail_price_inr"]).sum())
    
    # Referential integrity from tickets
    ticket_skus = set(df_tickets["product_sku"].dropna())
    valid_skus = set(df_products["sku"])
    unmatched_ticket_skus = list(ticket_skus - valid_skus)
    
    return {
        "total_products": total_products,
        "unique_skus": unique_skus,
        "negative_unit_cost_count": negative_cost,
        "negative_retail_price_count": negative_price,
        "cost_exceeds_retail_count": cost_exceeds_retail,
        "unmatched_ticket_skus_count": len(unmatched_ticket_skus),
        "families": df_products["family"].value_counts().to_dict(),
    }


def audit_orders(
    df_orders: pd.DataFrame,
    df_customers: pd.DataFrame,
    df_products: pd.DataFrame,
    df_tickets: pd.DataFrame,
) -> Dict[str, Any]:
    """Audits orders dataset, order-ticket references, and fallback resolution."""
    total_orders = len(df_orders)
    unique_orders = df_orders["order_id"].nunique()
    missing_order_ids = int(df_orders["order_id"].isnull().sum())
    
    # Foreign key checks inside orders.csv
    valid_cust = set(df_customers["customer_id"])
    valid_skus = set(df_products["sku"])
    orders_cust_unmatched = int((~df_orders["customer_id"].isin(valid_cust)).sum())
    orders_sku_unmatched = int((~df_orders["sku"].isin(valid_skus)).sum())
    
    # Ticket order_id audit
    tickets_with_order_id = df_tickets[df_tickets["order_id"].notnull()]
    tickets_without_order_id = df_tickets[df_tickets["order_id"].isnull()]
    
    valid_order_ids = set(df_orders["order_id"])
    invalid_ticket_order_ids = int(
        (~tickets_with_order_id["order_id"].isin(valid_order_ids)).sum()
    )
    
    # Fallback matching: tickets missing order_id matched by customer_id + product_sku against orders
    order_sku_counts = df_orders.groupby(["customer_id", "sku"]).size().reset_index(name="_match_count")
    merged_fallback_rows = tickets_without_order_id.merge(
        order_sku_counts,
        left_on=["customer_id", "product_sku"],
        right_on=["customer_id", "sku"],
        how="left",
    )
    merged_fallback_rows["_match_count"] = merged_fallback_rows["_match_count"].fillna(0).astype(int)
    
    # Row-level counts (sum exactly to len(tickets_without_order_id))
    row_unique_fallback = int((merged_fallback_rows["_match_count"] == 1).sum())
    row_ambiguous_fallback = int((merged_fallback_rows["_match_count"] > 1).sum())
    row_unmatched_fallback = int((merged_fallback_rows["_match_count"] == 0).sum())
    
    # Unique ticket_id entity counts
    unique_no_order = tickets_without_order_id.drop_duplicates(subset=["ticket_id"]).merge(
        order_sku_counts,
        left_on=["customer_id", "product_sku"],
        right_on=["customer_id", "sku"],
        how="left",
    )
    unique_no_order["_match_count"] = unique_no_order["_match_count"].fillna(0).astype(int)
    uniq_ticket_unique_fallback = int((unique_no_order["_match_count"] == 1).sum())
    uniq_ticket_ambiguous_fallback = int((unique_no_order["_match_count"] > 1).sum())
    uniq_ticket_unmatched_fallback = int((unique_no_order["_match_count"] == 0).sum())
    
    return {
        "total_orders": total_orders,
        "unique_order_ids": unique_orders,
        "missing_order_ids": missing_order_ids,
        "orders_customer_unmatched": orders_cust_unmatched,
        "orders_sku_unmatched": orders_sku_unmatched,
        "tickets_with_order_id_count": len(tickets_with_order_id),
        "tickets_without_order_id_count": len(tickets_without_order_id),
        "invalid_ticket_order_ids_count": invalid_ticket_order_ids,
        "fallback_unique_matches": row_unique_fallback,
        "fallback_ambiguous_matches": row_ambiguous_fallback,
        "fallback_unmatched": row_unmatched_fallback,
        "unique_ticket_fallback_unique": uniq_ticket_unique_fallback,
        "unique_ticket_fallback_ambiguous": uniq_ticket_ambiguous_fallback,
        "unique_ticket_fallback_unmatched": uniq_ticket_unmatched_fallback,
    }


def audit_business_rules(
    df_tickets: pd.DataFrame, df_agents: pd.DataFrame
) -> Dict[str, Any]:
    """Audits adherence to policy constraints (refund/replacement exclusivity, caps, tiers)."""
    # 1. Mutual exclusivity: refund AND replacement on the same ticket
    both_refund_and_repl = df_tickets[
        (df_tickets["refund_amount_inr"].fillna(0) > 0)
        & (df_tickets["replacement_issued"] == "Y")
    ]
    both_count = len(both_refund_and_repl)
    
    # 2. Goodwill credit cap: GW-OTHER refund > Rs 500
    goodwill_exceeded = df_tickets[
        (df_tickets["refund_reason_code"] == "GW-OTHER")
        & (df_tickets["refund_amount_inr"] > GOODWILL_CREDIT_CAP_INR)
    ]
    goodwill_exceeded_count = len(goodwill_exceeded)
    
    # 3. Replacements approved by Tier 1 vs Tier 2 agents
    merged = df_tickets.merge(
        df_agents[["agent_id", "tier", "team"]], on="agent_id", how="left"
    )
    repl_tickets = merged[merged["replacement_issued"] == "Y"]
    tier1_replacements = int((repl_tickets["tier"] == 1).sum())
    tier2_replacements = int((repl_tickets["tier"] == 2).sum())
    
    return {
        "tickets_with_both_refund_and_replacement": both_count,
        "goodwill_refunds_exceeding_cap": goodwill_exceeded_count,
        "replacements_by_tier1_agents": tier1_replacements,
        "replacements_by_tier2_agents": tier2_replacements,
    }
