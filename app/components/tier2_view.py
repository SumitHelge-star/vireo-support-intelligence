"""
Tier 2 / Warranty Operational Performance Component for Streamlit Dashboard.
Displays multi-day turnaround cycle times, RMA counts, and duration distributions without volume ranking.
"""

from typing import Any, Dict
import pandas as pd
import streamlit as st


def render_tier2_view(performance_payload: Dict[str, Any]) -> None:
    """Renders Tier 2 / Escalations & Warranty operational metrics and unranked workload diagnostics."""
    st.markdown("### 🛠️ Tier 2 / Escalations & Warranty Operational Diagnostics")
    
    st.warning(
        "🛡️ **Hard Governance Rule:** Tier 2 / Warranty cases intentionally require multiple days for deep diagnosis, "
        "hardware testing, and vendor RMA shipping. **Tier 2 agents are NEVER ranked on raw ticket counts.**"
    )
    
    t2 = performance_payload.get("tier2_warranty_operational_summary", {})
    if not t2 or t2.get("cases_handled", 0) == 0 and t2.get("cases_resolved", 0) == 0:
        st.info("No Escalations & Warranty cases recorded for this reporting week.")
        return
        
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Cases Assigned (Inflow)", value=f"{t2.get('cases_handled', 0)} cases")
    with c2:
        st.metric(label="Cases Resolved (Closures)", value=f"{t2.get('cases_resolved', 0)} cases")
    with c3:
        avg_d = f"{t2.get('average_resolution_days'):.2f} days" if t2.get("average_resolution_days") is not None else "N/A"
        st.metric(label="Avg Resolution Turnaround", value=avg_d)
    with c4:
        med_d = f"{t2.get('median_resolution_days'):.2f} days" if t2.get("median_resolution_days") is not None else "N/A"
        st.metric(label="Median Resolution Turnaround", value=med_d)
        
    st.markdown("#### ⏱️ Resolution Turnaround Duration Distribution")
    dist = t2.get("duration_distribution", {})
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Under 2 Days", f"{dist.get('under_2_days', 0)} cases")
    col_b.metric("2 to 5 Days", f"{dist.get('2_to_5_days', 0)} cases")
    col_c.metric("5 to 10 Days", f"{dist.get('5_to_10_days', 0)} cases")
    col_d.metric("Over 10 Days", f"{dist.get('over_10_days', 0)} cases")
    
    st.markdown("#### 👥 Unranked Agent Workload Breakdown")
    agents = t2.get("agent_operational_summary", [])
    if agents:
        rows = []
        for a in agents:
            avg_str = f"{a['average_resolution_days']:.2f} days" if a["average_resolution_days"] is not None else "N/A"
            rows.append({
                "Agent Name": a["agent_name"],
                "Agent ID": a["agent_id"],
                "Site": a["site"],
                "Cases Assigned (In Week)": a["cases_handled"],
                "Cases Resolved (In Week)": a["cases_resolved"],
                "Avg Turnaround": avg_str,
                "Repeat Contacts (30d)": a["repeat_contacts_30d"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.write("No agent breakdowns available for this week.")
