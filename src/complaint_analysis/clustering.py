"""
Clustering and topic discovery module for customer complaint grouping.
Uses local TF-IDF vectorization and KMeans clustering to generate explainable topic groups.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from src.complaint_analysis.preprocessing import clean_text


@dataclass
class ComplaintCluster:
    cluster_id: int
    label: str
    top_terms: List[str]
    ticket_count: int
    percentage: float
    ticket_ids: List[str]
    dominant_category: str
    dominant_channel: str
    dominant_product: str
    avg_csat: Optional[float] = None
    sla_breach_rate: float = 0.0
    representative_ticket_ids: List[str] = field(default_factory=list)


def generate_explainable_label(top_terms: List[str], dominant_category: str) -> str:
    """
    Generates a clear, grounded topic label based on top discriminating keywords and category.
    Avoids disconnected hallucinations by constructing labels directly from top terms.
    """
    terms_set = set(top_terms)
    
    # Domain-grounded heuristics based on top discovered n-grams
    if any(w in terms_set for w in ["delivery", "delayed", "courier", "tracking", "dispatch", "shipped", "arrived"]):
        return f"Delivery & Logistics ({', '.join(top_terms[:3])})"
    elif any(w in terms_set for w in ["battery", "charge", "charging", "drain", "draining", "backup", "discharged"]):
        return f"Battery & Charging Performance ({', '.join(top_terms[:3])})"
    elif any(w in terms_set for w in ["bluetooth", "pairing", "pair", "connect", "cutting", "disconnect", "sync"]):
        return f"Bluetooth Connectivity & Pairing ({', '.join(top_terms[:3])})"
    elif any(w in terms_set for w in ["mic", "meeting", "audio", "sound", "volume", "static", "buzzing", "distortion"]):
        return f"Audio & Microphone Quality ({', '.join(top_terms[:3])})"
    elif any(w in terms_set for w in ["invoice", "gst", "payment", "duplicate", "failed", "deducted", "bill"]):
        return f"Billing, Payment & GST Invoices ({', '.join(top_terms[:3])})"
    elif any(w in terms_set for w in ["refund", "pickup", "return", "replacement", "doa", "rma", "warranty"]):
        return f"Returns, Refunds & Warranty Claims ({', '.join(top_terms[:3])})"
    elif any(w in terms_set for w in ["app", "firmware", "update", "app crash", "syncing", "login", "password"]):
        return f"App & Firmware Sync Issues ({', '.join(top_terms[:3])})"
    
    # Fallback to category + top 2 terms
    if top_terms:
        return f"{dominant_category} ({', '.join(top_terms[:2])})"
    return f"{dominant_category} Complaints"


def perform_complaint_clustering(
    df_tickets: pd.DataFrame,
    n_clusters: int = 5,
    random_state: int = 42,
) -> Tuple[List[ComplaintCluster], pd.DataFrame, Optional[KMeans], Optional[TfidfVectorizer]]:
    """
    Executes TF-IDF + KMeans clustering on the input ticket slice.
    Returns structured cluster definitions, assigned DataFrame, and model objects.
    """
    if df_tickets.empty:
        return [], df_tickets.copy(), None, None

    df = df_tickets.copy()
    
    # Combine customer opening message and category for richer signal
    df["cleaned_message"] = df["customer_message"].apply(clean_text)
    
    # Handle edge case: all messages empty or whitespace
    non_empty_mask = df["cleaned_message"].str.len() > 0
    if non_empty_mask.sum() < 2:
        # Fallback for empty/single message
        df["cluster_id"] = 0
        cat = df["category"].mode()[0] if not df["category"].empty else "General"
        ch = df["channel"].mode()[0] if not df["channel"].empty else "chat"
        prod = df["product_sku"].mode()[0] if not df["product_sku"].empty else "Unknown"
        single_cluster = ComplaintCluster(
            cluster_id=0,
            label=f"{cat} (General)",
            top_terms=["general", "inquiry"],
            ticket_count=len(df),
            percentage=100.0,
            ticket_ids=df["ticket_id"].tolist(),
            dominant_category=cat,
            dominant_channel=ch,
            dominant_product=prod,
            representative_ticket_ids=df["ticket_id"].head(3).tolist(),
        )
        return [single_cluster], df, None, None

    # Adapt k if samples are fewer than requested clusters
    effective_k = min(n_clusters, non_empty_mask.sum())
    effective_k = max(1, effective_k)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2 if non_empty_mask.sum() >= 10 else 1,
        max_df=0.90,
        sublinear_tf=True,
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(df["cleaned_message"])
    except ValueError:
        # If vocabulary is empty, fallback
        vectorizer = TfidfVectorizer(ngram_range=(1, 1), min_df=1)
        tfidf_matrix = vectorizer.fit_transform(df["cleaned_message"].fillna("general"))

    kmeans = KMeans(n_clusters=effective_k, random_state=random_state, n_init=10)
    df["cluster_id"] = kmeans.fit_predict(tfidf_matrix)

    feature_names = np.array(vectorizer.get_feature_names_out())
    clusters_list = []
    total_tickets = len(df)

    for c_id in range(effective_k):
        c_mask = df["cluster_id"] == c_id
        c_df = df[c_mask]
        c_count = len(c_df)
        c_pct = round((c_count / total_tickets) * 100, 2)
        
        # Extract top 5 discriminating keywords from cluster centroid
        if len(feature_names) > 0:
            centroid = kmeans.cluster_centers_[c_id]
            top_indices = centroid.argsort()[::-1][:5]
            top_terms = [feature_names[idx] for idx in top_indices if centroid[idx] > 0]
            if not top_terms:
                top_terms = [feature_names[idx] for idx in top_indices[:3]]
        else:
            top_terms = ["general"]

        dom_cat = c_df["category"].mode()[0] if not c_df["category"].empty else "Other"
        dom_ch = c_df["channel"].mode()[0] if not c_df["channel"].empty else "chat"
        dom_prod = c_df["product_sku"].mode()[0] if not c_df["product_sku"].empty else "Unknown"
        
        # Metrics
        csat_clean = c_df["csat_score"].replace(0, np.nan).dropna()
        avg_csat = round(float(csat_clean.mean()), 2) if not csat_clean.empty else None
        
        # SLA breach rate if created & first response exist
        breach_rate = 0.0
        if "is_sla_breached" in c_df.columns:
            breach_rate = round(float(c_df["is_sla_breached"].mean() * 100), 2)

        label = generate_explainable_label(top_terms, dom_cat)

        cluster_obj = ComplaintCluster(
            cluster_id=c_id,
            label=label,
            top_terms=top_terms,
            ticket_count=c_count,
            percentage=c_pct,
            ticket_ids=c_df["ticket_id"].tolist(),
            dominant_category=dom_cat,
            dominant_channel=dom_ch,
            dominant_product=dom_prod,
            avg_csat=avg_csat,
            sla_breach_rate=breach_rate,
        )
        clusters_list.append(cluster_obj)

    # Sort clusters descending by ticket volume
    clusters_list.sort(key=lambda c: c.ticket_count, reverse=True)
    return clusters_list, df, kmeans, vectorizer
