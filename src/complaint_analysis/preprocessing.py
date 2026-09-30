"""
Text preprocessing and cleaning module for customer support complaint messages.
"""

import re
from typing import List, Union
import pandas as pd

# Generic conversational stopwords and support boilerplate
CUSTOM_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves",
    # Support desk boilerplate
    "please", "pls", "kindly", "thanks", "thank", "regards", "hello", "hi", "hey",
    "dear", "sir", "madam", "help", "regarding", "regard", "vireo", "customer",
    "support", "agent", "service", "ticket", "issue", "problem", "query", "complaint",
    "told", "colleague", "someone", "anyone", "want", "need", "get", "got", "also",
    "already", "still", "even", "just", "now", "day", "days", "time", "times"
}


def clean_text(text: Union[str, float, None]) -> str:
    """
    Cleans raw customer messages and notes into a normalized, lemmatized-like word sequence.
    Handles edge cases (empty strings, NaNs, boilerplate headers).
    """
    if not isinstance(text, str) or pd.isna(text):
        return ""

    s = text.lower()

    # Remove IVR transcript tags
    s = re.sub(r"\[ivr transcript\]", " ", s)
    s = re.sub(r"\[chat transcript\]", " ", s)
    s = re.sub(r"\[email\]", " ", s)

    # Remove order ID patterns (e.g. VR882661, TK-240001)
    s = re.sub(r"\bvr\d+\b", " ", s)
    s = re.sub(r"\btk-\d+\b", " ", s)

    # Remove URLs and email addresses
    s = re.sub(r"http\S+|www\.\S+", " ", s)
    s = re.sub(r"\S+@\S+", " ", s)

    # Remove phone numbers
    s = re.sub(r"\b\d{10}\b", " ", s)
    s = re.sub(r"\b\+91\d+\b", " ", s)

    # Replace punctuation with spaces
    s = re.sub(r"[^a-z0-9\s]", " ", s)

    # Tokenize and filter stopwords, short tokens, and pure numbers
    tokens = [
        w for w in s.split()
        if w not in CUSTOM_STOPWORDS and len(w) > 2 and not w.isdigit()
    ]

    return " ".join(tokens)


def preprocess_corpus(series: pd.Series) -> pd.Series:
    """Vectorized cleaning of a Pandas text series."""
    return series.apply(clean_text)
