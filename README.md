# Vireo Audio — Customer Support Intelligence System
## Complete Executive Decision-Support Tool & Analytics Platform (Phases 1–6)

### 1. Project Overview
Vireo Audio is a Bengaluru-based consumer-audio and wearables brand (earbuds, headphones, smart speakers, smartwatches) selling direct-to-consumer and via major marketplaces (Amazon, Flipkart). Customer support is provided across 4 channels (Chat, Email, Voice callbacks, Social) by 44 support agents across two operating centers (Bengaluru and Indore) and 3 shifts (Morning, Day, Night).

This repository contains the complete, production-ready **Vireo Audio Support Intelligence System**. Operating 100% locally with open-source Python (zero paid per-ticket AI cloud bills), the system digests 18 months of operational logs (12,528 tickets; 8,381 annualized) to answer four fundamental business questions:
1. **What are customers complaining about?** (Dynamic TF-IDF + KMeans topic clustering with verifiable raw ticket drill-downs)
2. **Where is customer friction occurring?** (30-day First Contact Resolution repeat contact rates and SLA breach liabilities)
3. **How is frontline support performing?** (Tier 1 throughput leaderboards with contextual metrics and small-sample shields)
4. **What is the estimated financial opportunity?** (Addressable friction baseline and multi-scenario ROI forecasting)

---

### 2. Architecture & Directory Topology
```text
banai/
├── app/                          # Interactive Streamlit Executive Dashboard
│   ├── streamlit_app.py          # Dashboard entrypoint & caching layer
│   └── components/               # Modular presentation components
│       ├── __init__.py
│       ├── kpi_cards.py          # Macro KPI metric cards & WoW deltas
│       ├── complaint_view.py     # Topic clusters & raw ticket evidence drill-down
│       ├── performance_view.py   # Tier 1 frontline ranked leaderboard
│       ├── tier2_view.py         # Escalations & Warranty cycle-time diagnostics
│       └── finance_view.py       # Financial ROI simulator & break-even analysis
├── data/
│   ├── raw/                      # Immutable raw source CSVs & documentation
│   │   ├── tickets.csv           # 12,528 support tickets (18 months)
│   │   ├── agents.csv            # 44 agent roster assignments
│   │   ├── customers.csv         # 9,500 registered customers
│   │   ├── orders.csv            # 15,000 purchase orders
│   │   ├── products.csv          # 14 product catalog SKUs
│   │   └── support-policy.pdf    # Customer Support Operating Policy v3.2
│   └── processed/                # Normalized, validated datasets (derived fields added)
│       ├── tickets_processed.csv
│       ├── agents_processed.csv
│       ├── customers_processed.csv
│       ├── orders_processed.csv
│       └── products_processed.csv
├── docs/                         # Authoritative documentation & submission assets
│   ├── README.txt                # System schemas & field definitions
│   ├── email-thread.txt          # Stakeholder alignment notes (Priya, Sameer, Arjun, Neha)
│   ├── support-policy.pdf        # Support Operating Policy v3.2
│   ├── screen_recording_walkthrough.md # 3-minute executive video walkthrough script
│   └── submission_form_content.md      # Copy-pasteable hiring submission form answers
├── src/                          # Modular core deterministic data engines
│   ├── __init__.py
│   ├── config.py                 # Paths, SLA thresholds, channel costs, schemas
│   ├── data_loader.py            # Non-destructive, validated file loading
│   ├── validators.py             # Schema, timestamp, FK, and policy rule validators
│   ├── normalization.py          # Deterministic feature derivation & export
│   ├── audit.py                  # Audit orchestration & Markdown report generator
│   ├── complaint_analysis/       # Local AI text processing & weekly digest engines
│   │   ├── __init__.py
│   │   ├── text_cleaner.py       # Deterministic boilerplate stripping & normalization
│   │   ├── clustering.py         # TF-IDF + KMeans clustering & centroid keyword extraction
│   │   ├── representative_tickets.py # Centroid distance citation extraction
│   │   ├── repeat_contact.py     # 30-day FCR window tracking & channel costing
│   │   └── weekly_digest.py      # Weekly intelligence payload generator
│   ├── business_impact/          # Financial ROI & friction economics engine
│   │   ├── __init__.py
│   │   └── roi_model.py          # Deterministic annualization, scenarios, break-even
│   └── performance/              # Role-governed performance & throughput engine
│       ├── __init__.py
│       ├── assignment.py         # Agent roster resolution & team classification
│       ├── leaderboard.py        # Tier 1 volume ranking & small-sample shielding
│       ├── tier2_summary.py      # Tier 2 turnaround cycle-time analytics (unranked)
│       └── weekly_metrics.py     # Unified performance payload & trend generator
├── tests/                        # Comprehensive test suite (44 automated tests)
│   ├── test_audit.py
│   ├── test_data_loader.py
│   ├── test_normalization.py
│   ├── test_phase2_complaints.py
│   ├── test_phase3_roi.py
│   ├── test_phase4_assignment.py
│   ├── test_phase4_leaderboard.py
│   ├── test_phase4_tier2.py
│   ├── test_phase4_weekly_metrics.py
│   ├── test_phase5_dashboard.py
│   ├── test_repeat_contact.py
│   ├── test_validators.py
│   └── test_weekly_digest.py
├── reports/                      # Verified analytical reports & executive deliverables
│   ├── phase1_data_quality_report.md
│   ├── phase2_complaint_analysis_report.md
│   ├── phase3_business_impact_report.md
│   ├── phase3_business_impact.json
│   ├── phase4_performance_report.md
│   ├── phase4_weekly_leaderboard.json
│   ├── phase5_dashboard_report.md
│   ├── phase6_final_delivery_report.md
│   └── executive_memo_priya_raman.md  # 1-Page Executive Memo for Leadership
├── scripts/                      # Automated pipeline execution CLI scripts
│   ├── run_phase1_audit.py       # Phase 1 Data Foundation Audit CLI
│   ├── run_phase2_analysis.py    # Phase 2 Complaint Intelligence CLI
│   ├── run_phase3_roi.py         # Phase 3 Business Impact & ROI CLI
│   ├── run_phase4_performance.py # Phase 4 Role-Governed Performance CLI
│   └── run_phase5_app_check.py   # Phase 5 Dashboard Smoke Check CLI
├── requirements.txt              # Production dependencies (pandas, scikit-learn, streamlit, pytest)
├── pytest.ini                    # Pytest configuration
├── .gitignore                    # Environment & cache ignore rules
└── README.md                     # Project documentation
```

---

### 3. Quick Start & Execution Commands

#### Prerequisites:
- Python 3.11+ (Tested on Python 3.14)
- Standard virtual environment

```bash
# 1. Activate the virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 2. Install dependencies (if not already installed)
pip install -r requirements.txt

# 3. Execute all analytical pipelines sequentially
python scripts/run_phase1_audit.py
python scripts/run_phase2_analysis.py
python scripts/run_phase3_roi.py
python scripts/run_phase4_performance.py
python scripts/run_phase5_app_check.py

# 4. Run full automated test suite (44 tests)
pytest -v

# 5. Launch the Streamlit Executive Dashboard
streamlit run app/streamlit_app.py
```

---

### 4. Key Methodologies & Governance Safeguards

1. **Complaint Clustering Methodology:**
   - Uses `scikit-learn` TF-IDF vectorization (unigrams + bigrams) and KMeans clustering.
   - **Global 18-Month Corpus Analysis (Phase 2):** $k=6$ clusters over all 12,528 tickets.
   - **Weekly Operational Digest & Dashboard (Phase 2 & Phase 5):** $k=5$ clusters dynamically fitted on weekly ticket slices (~200 tickets/week).
   - **Data Quality Notice:** In global analysis, the largest cluster contains ~44.2% of tickets and is broad/generic due to conversational user phrasing. The dashboard provides transparent warnings and links directly to verifiable raw ticket citations.
2. **Tier 1 Frontline Leaderboard:**
   - Ranks Chat, Email, and Voice frontline agents strictly by **Closed Tickets in Week**.
   - Accompanied by operational context metrics (CSAT, SLA Breach %, Repeat Contact %, Handle Time) without composite score distortion.
   - Agents with $<5$ closures receive an explicit `⚠️ Small Sample (<5)` badge.
3. **Tier 2 Escalations & Warranty Governance:**
   - Strictly excluded from ticket-volume leaderboards per Neha Kulkarni's operational guidelines.
   - Evaluated on **Turnaround Cycle Time (Mean/Median Days)**, **Duration Distribution**, and **RMA Counts**.
   - Explains cross-week asynchronous cohorts ($Closed > Assigned$ occurs naturally when multi-day cases resolve across weekly boundaries).
4. **Financial ROI Economics (Arjun Mehta Standards):**
   - **Baseline Operating Friction:** ₹9,44,693 / year (Repeat contact handling: ₹6,82,635/yr; SLA breach store credit liabilities: ₹2,62,058/yr).
   - **Scenario Opportunities:** Conservative 5% (₹47,235/yr), Base 10% (₹94,469/yr), Stretch 20% (₹1,88,939/yr).
   - All reduction rates are explicitly labeled as modeled scenario assumptions, not observed historical savings.
   - Software operating cost is ₹0 (local runtime).

---

### 5. Automated Testing & Verification
The system is protected by **44 unit and integration tests** covering:
- Raw file immutability and schema validations
- 100% foreign key integrity and order fallback matching
- TF-IDF clustering, centroid keywords, and citation extraction
- 30-day FCR repeat contact window and channel cost modeling
- SLA first-response breach detection and store credit liability
- Role-governed agent assignment and Tier 2 exclusion
- Streamlit UI component imports and KPI consistency
- Full 79-week dataset metric integrity audit (all defined Phase 4 integrity checks passed across 79 ISO calendar weeks)


#### Run Automated Test Suite:
```bash
python -m pytest -v
```
*Executes 44 comprehensive unit and integration tests validating schema detection, duplicate detection, timestamp parsing, missing field handling, referential integrity, business rules, CSAT sanitization, TF-IDF clustering, repeat contacts, ROI economics, role-governed performance, and Streamlit dashboard integration.*

---

### 6. Summary of Verified Data Findings

| Dataset | Total Rows | Unique Keys | Null Checks & Integrity Status |
| :--- | :--- | :--- | :--- |
| `tickets.csv` | 12,528 | 11,875 (653 dup pairs) | 100% FK integrity; 644 null `resolved_at` (open/pending) |
| `agents.csv` | 44 | 44 unique agents | 100% active assignments; roster history preserved |
| `customers.csv` | 9,500 | 9,500 unique IDs | 100% complete; 0 nulls; 100% valid signup dates |
| `orders.csv` | 15,000 | 15,000 unique IDs | 100% FK integrity to customers and products |
| `products.csv` | 14 | 14 unique SKUs | 100% positive margins; valid warranty terms (12-24 mos) |

#### Critical Audit Highlights:
1. **Migration Duplication:** 653 ticket IDs appear under both `source_system = 'helpdesk'` and `'legacy_fd'` (1,306 rows total) due to post-migration re-import on 14 September 2025. Deduplication preserves canonical modern helpdesk rows.
2. **Legacy Timestamp Inversion:** 2,472 legacy tickets have `resolved_at < first_response_at` due to UTC event log reconstruction. Zero timestamp anomalies exist in the modern helpdesk.
3. **CSAT Sanitization:** 2,083 tickets in `legacy_fd` contain `csat_score = 0.0`. Per Operating Policy v3.2, score 0 represents survey non-response and is converted to `NaN` in downstream metrics.
4. **Order ID Fallback Matching:** For 4,218 tickets missing an explicit `order_id`, matching by `(customer_id, product_sku)` date proximity uniquely resolves 3,467 tickets (82.2%), while 751 (17.8%) have ambiguous multi-order histories and are safely retained as null.
5. **Policy Exceptions:** Identified 4 dual-settlement cases (both refund > 0 and replacement issued) and 38 goodwill refunds exceeding the ₹500 cap.

---

### 7. Core Stakeholder Alignment
* **Priya Raman (Head of CX):** Weekly executive complaint intelligence digest and frontline throughput leaderboard.
* **Neha Kulkarni (Support Operations Manager):** Multi-day Tier 2 turnaround diagnostics with strict exclusion from volume rankings.
* **Arjun Mehta (Finance Controller):** Transparent financial model with baseline friction breakdown and scenario simulators.

