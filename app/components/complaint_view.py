"""
Customer Complaint Intelligence Component for Streamlit Dashboard.
Visualizes topic clusters, keyword drivers, and representative ticket evidence drill-downs.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st


def _get_cluster_field(cluster_item: Any, field_name: str, default: Any = None) -> Any:
    """Safely extracts a field from either a ComplaintCluster object or a dictionary."""
    if isinstance(cluster_item, dict):
        return cluster_item.get(field_name, default)
    return getattr(cluster_item, field_name, default)


def render_complaint_view(weekly_digest: Dict[str, Any], week_df: pd.DataFrame) -> None:
    """Renders the complaint intelligence breakdown, clusters, and evidence table."""
    st.markdown("### 🔍 Customer Complaint Groups & Topic Intelligence")
    st.info("💡 **Methodology:** Complaint topics are generated using local TF-IDF vectorization and KMeans clustering over actual ticket text. All insights link directly to verifiable ticket IDs.")
    st.warning("⚠️ **Data Quality Notice:** In global corpus analysis, the largest complaint cluster contains approximately 44.2% of tickets and is broad/generic, limiting its usefulness for precise root-cause classification. Weekly cluster slices provide operational guidance and should be verified against the cited raw ticket samples below.")
    
    clusters = weekly_digest.get("complaint_clusters", [])
    if not clusters:
        st.warning("Insufficient ticket volume for reliable complaint clustering in this week.")
        return

    # Overview Table
    cluster_rows = []
    for c in clusters:
        cluster_id = _get_cluster_field(c, "cluster_id", 0)
        label = _get_cluster_field(c, "label", "Topic")
        ticket_count = _get_cluster_field(c, "ticket_count", 0)
        percentage = _get_cluster_field(c, "percentage", 0.0)
        top_terms = _get_cluster_field(c, "top_terms", [])
        dominant_channel = _get_cluster_field(c, "dominant_channel", "chat")
        rep_ids_list = _get_cluster_field(c, "representative_ticket_ids", [])

        if rep_ids_list:
            rep_ids_str = ", ".join(str(tid) for tid in rep_ids_list[:3])
        else:
            rep_ids_str = "No representative tickets available."

        cluster_rows.append({
            "Cluster": f"Cluster {cluster_id + 1}",
            "Topic / Category Label": label,
            "Ticket Volume": ticket_count,
            "Share of Week": f"{percentage:.1f}%",
            "Key Discriminating Terms": ", ".join(top_terms[:4]) if top_terms else "None",
            "Dominant Channel": str(dominant_channel).title(),
            "Representative Ticket IDs": rep_ids_str,
        })
        
    df_clusters = pd.DataFrame(cluster_rows)
    st.dataframe(df_clusters, use_container_width=True, hide_index=True)
    
    st.markdown("#### 📂 Drill-Down into Complaint Evidence")
    cluster_labels = [_get_cluster_field(c, "label", "Topic") for c in clusters]
    selected_cluster_label = st.selectbox(
        "Select a complaint topic to inspect representative ticket citations:",
        options=cluster_labels,
    )
    
    # Find matching cluster
    matched = next((c for c in clusters if _get_cluster_field(c, "label") == selected_cluster_label), None)
    if matched:
        c_ticket_ids = _get_cluster_field(matched, "ticket_ids", [])
        evidence_slice = week_df[week_df["ticket_id"].isin(c_ticket_ids)].copy()
        
        matched_label = _get_cluster_field(matched, "label", "Topic")
        st.write(f"Showing **{min(len(evidence_slice), 10)}** sample tickets for **{matched_label}**:")
        display_cols = ["ticket_id", "created_at", "channel", "product_sku", "customer_message", "csat_score"]
        available_cols = [col for col in display_cols if col in evidence_slice.columns]
        
        st.dataframe(
            evidence_slice[available_cols].head(10),
            use_container_width=True,
            hide_index=True,
        )

