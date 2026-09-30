"""
Complaint Analysis & Intelligence Package for Vireo Audio Support.
Provides text preprocessing, clustering, representative evidence extraction,
repeat contact analysis, and deterministic weekly digest generation.
"""

from src.complaint_analysis.preprocessing import clean_text, preprocess_corpus
from src.complaint_analysis.clustering import perform_complaint_clustering, ComplaintCluster
from src.complaint_analysis.representative_tickets import extract_representative_tickets
from src.complaint_analysis.repeat_contact import calculate_repeat_contacts
from src.complaint_analysis.weekly_digest import generate_weekly_digest
from src.complaint_analysis.ai_summarizer import generate_executive_summary

__all__ = [
    "clean_text",
    "preprocess_corpus",
    "perform_complaint_clustering",
    "ComplaintCluster",
    "extract_representative_tickets",
    "calculate_repeat_contacts",
    "generate_weekly_digest",
    "generate_executive_summary",
]
