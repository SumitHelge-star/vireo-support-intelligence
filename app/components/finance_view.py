"""
Financial Impact & ROI Modeling Component for Streamlit Dashboard.
Visualizes baseline support friction, scenario models, break-even budgets, and transparent formulas for Arjun Mehta.
"""

from typing import Any, Dict
import pandas as pd
import streamlit as st


def render_finance_view(financial_summary: Any) -> None:
    """Renders the financial impact model, scenario simulator, and break-even analysis."""
    st.markdown("### 💰 Business Impact & Financial ROI Modeling")
    st.info(
        "📊 **Finance Governance (Arjun Mehta Standard):** All baseline metrics are derived from actual support operating records "
        "and Support Policy v3.2 cost schedules. **Reduction percentages are scenario assumptions, NOT observed historical outcomes.**"
    )
    
    # 1. Baseline Addressable Friction
    st.markdown("#### 1. Observed Annualized Baseline Operating Friction")
    c1, c2, c3 = st.columns(3)
    c1.metric(
        label="Annualized Ticket Inflow",
        value=f"{financial_summary.annualized_ticket_volume:,.0f} tickets/yr",
        help="Derived from 12,528 total tickets over 18.0 operating months.",
    )
    c2.metric(
        label="Annualized Repeat Handling Friction",
        value=f"₹{financial_summary.annualized_repeat_cost_channel_specific_inr:,.0f} / yr",
        help="Calculated using channel cost schedule: Chat ₹210, Email ₹260, Voice ₹520, Social ₹240.",
    )
    c3.metric(
        label="Annualized SLA Store Credit Liability",
        value=f"₹{financial_summary.annualized_sla_liability_inr:,.0f} / yr",
        help="1,119 first-response breaches * ₹350 store credit annualized.",
    )
    
    st.markdown(
        f"**Total Addressable Annual Operating Friction:** **₹{financial_summary.total_annualized_addressable_friction_inr:,.0f} / year** "
        f"(18-Month Total: ₹{financial_summary.total_addressable_friction_18m_inr:,.0f})"
    )
    
    # 2. Scenario Comparison Table
    st.markdown("#### 2. Avoidable Friction Scenario Opportunities")
    
    scenario_choice = st.radio(
        "Select Scenario Assumption for Detailed Breakdown:",
        options=["Conservative (5% Reduction)", "Base (10% Reduction)", "Stretch (20% Reduction)"],
        index=1,
        horizontal=True,
    )
    
    s_key = "Base" if "Base" in scenario_choice else ("Conservative" if "Conservative" in scenario_choice else "Stretch")
    sc = financial_summary.scenarios[s_key]
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric(
        label="Avoided Repeat Contacts",
        value=f"~{sc['avoided_repeat_contacts_18m']/1.5:.0f} / yr",
        help=f"{sc['avoided_repeat_contacts_18m']:,} contacts over 18 months",
    )
    col_s2.metric(
        label="Annual Repeat Handling Savings",
        value=f"₹{sc['annualized_avoided_repeat_cost_inr']:,.0f} / yr",
    )
    col_s3.metric(
        label="Avoided SLA Credit Liability",
        value=f"₹{sc['annualized_avoided_sla_liability_inr']:,.0f} / yr",
    )
    col_s4.metric(
        label="Total Annual Gross Opportunity",
        value=f"₹{sc['total_annualized_gross_savings_inr']:,.0f} / yr",
    )
    
    # 3. Cost & Break-Even Analysis
    st.markdown("#### 3. Software Budget & Break-Even Analysis")
    st.write(
        "* **Current Local/Open-Source AI Runtime Cost:** **₹0 / year** (Zero OpenAI/Anthropic/Gemini cloud API fees).\n"
        f"* **Net Annual Financial Opportunity ({s_key} Scenario @ ₹0 Software Cost):** **₹{sc['net_annual_benefit_inr']:,.0f} / year**.\n"
        f"* **Arjun Mehta Break-Even Threshold:** Any future software budget below **₹{sc['total_annualized_gross_savings_inr']:,.0f} / year** delivers positive net ROI."
    )
    
    # All Scenarios Summary Table
    st.markdown("#### 4. Multi-Scenario Overview Table")
    table_rows = []
    for s_name, data in financial_summary.scenarios.items():
        table_rows.append({
            "Scenario Name": s_name,
            "Reduction Assumption": f"{data['reduction_percentage']:.1f}%",
            "Annual Avoided Repeat Cost": f"₹{data['annualized_avoided_repeat_cost_inr']:,.0f}",
            "Annual Avoided SLA Credits": f"₹{data['annualized_avoided_sla_liability_inr']:,.0f}",
            "Total Annual Gross Opportunity": f"₹{data['total_annualized_gross_savings_inr']:,.0f}",
            "Software Operating Cost": f"₹{data['tool_annual_cost_inr']:,.0f}",
            "Net Annual Benefit": f"₹{data['net_annual_benefit_inr']:,.0f}",
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
