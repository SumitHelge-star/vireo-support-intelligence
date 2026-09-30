"""
Representative ticket selection module.
Finds the most representative tickets closest to cluster centroids for verifiable evidence.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from src.complaint_analysis.clustering import ComplaintCluster


def extract_representative_tickets(
    df_clustered: pd.DataFrame,
    clusters: List[ComplaintCluster],
    vectorizer: Optional[TfidfVectorizer],
    kmeans: Optional[KMeans],
    top_n: int = 3,
) -> Dict[int, List[Dict]]:
    """
    Finds top_n representative ticket examples for each cluster by computing
    cosine similarity to the cluster centroid.
    """
    representative_map: Dict[int, List[Dict]] = {}

    # If vectorizer or kmeans is missing (e.g. tiny slice fallback), select top tickets by length
    if vectorizer is None or kmeans is None:
        for c in clusters:
            c_df = df_clustered[df_clustered["cluster_id"] == c.cluster_id]
            reps = []
            for _, row in c_df.head(top_n).iterrows():
                reps.append({
                    "ticket_id": str(row["ticket_id"]),
                    "customer_message": str(row["customer_message"]),
                    "agent_notes": str(row.get("agent_notes", "")),
                    "channel": str(row["channel"]),
                    "category": str(row["category"]),
                    "product_sku": str(row["product_sku"]),
                    "csat_score": row.get("csat_score"),
                    "similarity_score": 1.0,
                })
            c.representative_ticket_ids = [r["ticket_id"] for r in reps]
            representative_map[c.cluster_id] = reps
        return representative_map

    # Transform messages to TF-IDF matrix
    cleaned_texts = df_clustered["cleaned_message"].fillna("")
    tfidf_matrix = vectorizer.transform(cleaned_texts)

    for c in clusters:
        c_indices = df_clustered[df_clustered["cluster_id"] == c.cluster_id].index
        if len(c_indices) == 0:
            representative_map[c.cluster_id] = []
            continue

        # Get subset matrix and centroid
        c_matrix = tfidf_matrix[df_clustered.index.isin(c_indices)]
        centroid = kmeans.cluster_centers_[c.cluster_id].reshape(1, -1)

        # Compute cosine similarity to centroid
        similarities = cosine_similarity(c_matrix, centroid).flatten()
        
        # Sort descending by similarity
        top_sub_indices = similarities.argsort()[::-1][:top_n]
        actual_indices = [c_indices[i] for i in top_sub_indices]

        reps = []
        for idx, sub_idx in zip(actual_indices, top_sub_indices):
            row = df_clustered.loc[idx]
            reps.append({
                "ticket_id": str(row["ticket_id"]),
                "customer_message": str(row["customer_message"]),
                "agent_notes": str(row.get("agent_notes", "")),
                "channel": str(row["channel"]),
                "category": str(row["category"]),
                "product_sku": str(row["product_sku"]),
                "csat_score": row.get("csat_score"),
                "similarity_score": round(float(similarities[sub_idx]), 3),
            })

        c.representative_ticket_ids = [r["ticket_id"] for r in reps]
        representative_map[c.cluster_id] = reps

    return representative_map
