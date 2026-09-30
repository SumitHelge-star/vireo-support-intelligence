# VIREO AUDIO SUPPORT INTELLIGENCE
## Final Hiring-Assignment Submission Form Content

This document provides structured, copy-pasteable answers for standard hiring-assignment submission fields.

---

### 1. Project Name
**Vireo Audio Customer Support Intelligence — Weekly Executive Decision-Support Tool**

---

### 2. Problem Statement
Vireo Audio’s customer support leadership (Priya Raman - Head of CX, Neha Kulkarni - Support Operations Manager, and Arjun Mehta - Finance Controller) lacks a unified, weekly operational view of customer complaints, agent throughput, multi-day escalation cycle times, and financial friction costs. Without actionable visibility, leadership cannot identify recurring product defect trends, mitigate ₹9.45 Lakh/year in addressable support friction (repeat contacts and SLA breach store credit liabilities), or fairly govern Tier 1 vs. Tier 2 performance.

---

### 3. Solution Overview
We engineered a lightweight, modular decision-support system and interactive Streamlit executive dashboard (`streamlit run app/streamlit_app.py`). The system:
1. Ingests and normalizes 18 months of support logs (12,528 tickets across 44 agents) without modifying raw source files.
2. Extracts customer complaint themes and provides interactive raw-ticket citation drill-downs.
3. Ranks Tier 1 frontline agents (Chat, Email, Voice) by closed-ticket volume with small-sample shields and context metrics.
4. Governs Tier 2 Escalations & Warranty on turnaround cycle time (days) and strictly excludes them from volume ranking.
5. Models addressable friction economics and delivers multi-scenario financial ROI forecasts for finance review.

---

### 4. AI / ML Methodology (100% Free & Local)
* **Local Machine Learning:** Uses `scikit-learn` TF-IDF vectorization (unigrams + bigrams) and KMeans clustering ($k=6$ for the 18-month corpus, $k=5$ for weekly dynamic slices) to group customer complaint descriptions into interpretable operational categories.
* **Deterministic Traceability:** Top discriminating keywords are extracted from cluster centroids, and representative tickets are identified via Euclidean/cosine similarity to centroids.
* **Zero External Paid APIs:** Built with 100% open-source Python libraries (`pandas`, `numpy`, `scikit-learn`, `streamlit`); zero dependencies on OpenAI, Anthropic, or Gemini cloud APIs (₹0 runtime cost).

---

### 5. Business Impact & Financial ROI
* **Observed Baseline Addressable Friction:** **₹9,44,693 / year** across 8,381 annualized tickets (Repeat Contact Handling: ₹6,82,635/yr; SLA Breach Store Credit Liability: ₹2,62,058/yr).
* **Modeled Financial Opportunities:**
  - **Conservative (5% Reduction):** ₹47,235 / year gross benefit.
  - **Base (10% Reduction Assumption):** ₹94,469 / year gross benefit.
  - **Stretch (20% Reduction):** ₹1,88,939 / year gross benefit.
* **Software Operating Cost:** ₹0 / year. All savings deliver immediate positive net return.

---

### 6. Data Foundation & Integrity Audit
* **Authoritative Raw Data:** 12,528 ticket rows (11,875 unique IDs, 653 cross-system re-import pairs) spanning 2025-01-01 to 2026-06-30.
* **Referential Integrity:** 100% foreign key matching across customers, agents, products, and orders (including deterministic customer+sku date proximity matching for 4,218 blank order IDs).
* **Policy Compliance:** Clean separation of zero-encoded CSAT non-responses (2,083 tickets in legacy Freshdesk), detection of 38 goodwill refunds exceeding ₹500 cap, and resolution of 4 dual refund+replacement policy exceptions.

---

### 7. Governance & Ethical Safeguards
* **Tier 2 Non-Ranking Mandate:** Tier 2 / Warranty cases intentionally require multi-day hardware diagnostics (5.38 days median turnaround). They are never ranked by volume.
* **Small-Sample Protection:** Agents with $<5$ closed tickets in a week receive explicit `⚠️ Small Sample (<5)` tags to prevent misinterpretation of outlier CSAT or SLA percentages.
* **Transparency on Broad Clusters:** The largest cluster contains ~44.2% of tickets due to generic user text; the UI prominently warns users and links directly to verifiable raw ticket examples.

---

### 8. Validation & Testing
* **Automated Test Suite:** 44 automated unit and integration tests across 13 test modules executing via `pytest -v` (100% passing).
* **Metric Integrity Audit:** Scanned all 79 calendar weeks across all 12,528 tickets for impossible conditions (zero negative durations, zero out-of-bounds CSAT, zero Tier 2 in Tier 1 rankings).

---

### 9. Demo & Local Execution
```bash
# 1. Activate Virtual Environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# 2. Run All Verification Pipelines
python scripts/run_phase1_audit.py
python scripts/run_phase2_analysis.py
python scripts/run_phase3_roi.py
python scripts/run_phase4_performance.py
python scripts/run_phase5_app_check.py

# 3. Launch Interactive Streamlit Executive Dashboard
streamlit run app/streamlit_app.py
```
