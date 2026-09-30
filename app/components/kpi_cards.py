"""
Executive Overview KPI Component for Streamlit Dashboard.
Displays high-level customer experience, volume, quality, and financial indicators.
"""

from typing import Any, Dict, Optional
import streamlit as st


def render_kpi_cards(
    weekly_digest: Dict[str, Any],
    financial_summary: Any,
    performance_trends: Dict[str, Any],
) -> None:
    """Renders the executive summary KPI metric grid with week-over-week deltas."""
    st.markdown("### 📊 Executive Summary & Weekly High-Level KPIs")
    
    total_tickets = weekly_digest.get("total_tickets", 0)
    
    # Safe extraction from nested or flat keys
    repeat_rate = (
        weekly_digest.get("repeat_contacts", {}).get("rate_pct")
        if isinstance(weekly_digest.get("repeat_contacts"), dict)
        else weekly_digest.get("repeat_contact_rate_pct", 0.0)
    )
    if repeat_rate is None:
        repeat_rate = 0.0
        
    sla_breach_rate = (
        weekly_digest.get("sla_performance", {}).get("breach_rate_pct")
        if isinstance(weekly_digest.get("sla_performance"), dict)
        else weekly_digest.get("sla_breach_rate_pct", 0.0)
    )
    
    csat_dict = weekly_digest.get("csat_performance") if isinstance(weekly_digest.get("csat_performance"), dict) else {}
    avg_csat = csat_dict.get("mean_score") if csat_dict else weekly_digest.get("average_csat")
    csat_count = csat_dict.get("valid_survey_count") if csat_dict else weekly_digest.get("csat_response_count", 0)
    
    t1_summary = performance_trends.get("tier1_summary", {}) if isinstance(performance_trends, dict) else {}
    t1_closed = t1_summary.get("tickets_closed", 0)
    
    wow_t1 = performance_trends.get("tier1_wow_deltas") if isinstance(performance_trends, dict) else None
    wow_digest = weekly_digest.get("wow_comparison") if isinstance(weekly_digest, dict) else None
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        vol_pct = (
            wow_digest.get("volume_pct_change")
            if wow_digest and "volume_pct_change" in wow_digest
            else (wow_digest.get("volume_change_pct") if wow_digest else None)
        )
        delta_str = f"{vol_pct:+.1f}% vs prior week" if vol_pct is not None else None
        st.metric(
            label="Total Weekly Inflow",
            value=f"{total_tickets:,} tickets",
            delta=delta_str,
        )
        
    with col2:
        rep_change = wow_digest.get("repeat_change") if wow_digest else None
        repeat_delta = f"{rep_change:+d} tickets vs prior week" if rep_change is not None else None
        st.metric(
            label="30-Day Repeat Contact Rate",
            value=f"{repeat_rate:.1f}%",
            delta=repeat_delta,
            delta_color="inverse",
        )
        
    with col3:
        csat_val = f"{avg_csat:.2f} / 5.00" if avg_csat is not None else "N/A"
        csat_delta = f"{wow_t1['csat_delta']:+.2f} pts" if wow_t1 and wow_t1.get("csat_delta") is not None else None
        st.metric(
            label=f"Avg CSAT (n={csat_count})",
            value=csat_val,
            delta=csat_delta,
        )
        
    with col4:
        base_annual_opp = financial_summary.scenarios["Base"]["total_annualized_gross_savings_inr"]
        st.metric(
            label="Modeled Annual Opportunity (10% Base)",
            value=f"₹{base_annual_opp:,.0f} / yr",
            help="Modeled annual gross opportunity under 10% friction reduction assumption. Not an achieved or guaranteed business outcome.",
        )
        
    st.caption("ℹ️ *CSAT excludes legacy zero-encoded non-responses. Financial opportunity reflects modeled 10% reduction assumption.*")
