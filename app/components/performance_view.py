"""
Tier 1 Frontline Leaderboard Component for Streamlit Dashboard.
Displays ranked throughput, SLA adherence, CSAT, repeat contacts, and small-sample warnings.
"""

from typing import Any, Dict, List
import pandas as pd
import streamlit as st


def render_performance_view(performance_payload: Dict[str, Any]) -> None:
    """Renders the Tier 1 frontline performance leaderboard table and context metrics."""
    st.markdown("### 🏆 Tier 1 Frontline Performance Leaderboard")
    
    st.info(
        "📌 **Governance Notice:** Ranking is by **Tier 1 closed-ticket volume only** (Chat, Email, Voice). "
        "Tier 2 / Warranty is strictly excluded from volume rankings per Support Policy v3.2. "
        "Supporting metrics provide operational context and are not combined into an opaque score."
    )
    
    t1_list = performance_payload.get("tier1_frontline_leaderboard", [])
    if not t1_list:
        st.warning("No active Tier 1 frontline agent records found for this reporting week.")
        return
        
    rows = []
    for r in t1_list:
        csat_display = f"{r['average_csat']:.2f} (n={r['valid_csat_count']})" if r["average_csat"] is not None else "N/A"
        ht_display = f"{r['average_handle_time_minutes']:.1f}m" if r["average_handle_time_minutes"] is not None else "N/A"
        sample_tag = "⚠️ Small Sample (<5)" if r["is_small_sample"] else "✅ Standard"
        
        rows.append({
            "Rank": f"#{r['rank_by_tickets_closed']}",
            "Agent Name": r["agent_name"],
            "Agent ID": r["agent_id"],
            "Team": r["team"],
            "Site": r["site"],
            "Tickets Closed (In Week)": r["tickets_closed"],
            "Tickets Assigned (In Week)": r["tickets_assigned"],
            "SLA Breach Rate": f"{r['sla_breach_rate_pct']:.1f}% ({r['sla_breaches']})",
            "Avg CSAT": csat_display,
            "Repeat Contact Rate": f"{r['repeat_contact_rate_pct']:.1f}% ({r['repeat_contacts_30d']})",
            "Avg Handle Time": ht_display,
            "Sample Reliability": sample_tag,
        })
        
    df_t1 = pd.DataFrame(rows)
    st.dataframe(df_t1, use_container_width=True, hide_index=True)
    
    st.caption(
        "💡 *Note on Closed vs. Assigned:* Tickets closed includes tickets resolved in the week (which may have been assigned in prior weeks). "
        "CSAT excludes blank/zero non-responses. Handle time excludes invalid historical timestamp inversions."
    )
