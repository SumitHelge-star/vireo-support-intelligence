# VIREO AUDIO SUPPORT INTELLIGENCE
## PHASE 4 REPORT: ROLE-GOVERNED WEEKLY PERFORMANCE & THROUGHPUT ANALYSIS

**Document Release:** Phase 4 Performance Report  
**Author:** Senior Data & AI Software Engineering Lead  
**Date:** September 30, 2026  
**Target Stakeholders:** Priya Raman (Head of CX), Neha Kulkarni (Support Operations Manager), Arjun Mehta (Finance Controller)

---

## 1. Executive Summary & Governance Mandate

This report implements the **Role-Governed Weekly Performance and Throughput System** for Vireo Audio.

### Key Governance Safeguards (Neha Kulkarni Policy Rule):
> **GOVERNANCE MANDATE:** Tier 1 frontline agents are ranked strictly on closed-ticket throughput, SLA adherence, and customer satisfaction. **Tier 2 / Escalations & Warranty is strictly EXCLUDED from ticket-volume rankings**, because warranty investigations intentionally take multiple days for diagnostics and vendor RMA processing.

### Summary for Sample Reporting Week (2025-W41):
* **Tier 1 Frontline Closed Tickets:** 90 tickets closed across 25 active frontline agents.
* **Tier 1 SLA Breach Rate:** 10.3% first-response breach rate.
* **Tier 1 Customer Satisfaction:** Average CSAT = 3.58 / 5.00 (legacy zero-responses excluded).
* **Tier 2 / Warranty Load:** 9 cases assigned in week, 7 cases resolved in week, with a median turnaround of **5.38 days**.

---

## 2. Part A: Previous-Phase Corrections Completed

1. **Week Labeling Correction (ISO 8601 Standardization):**
   - Standardized calendar week labeling from 0-indexed `%Y-W%W` to standard ISO 8601 format (`%G-W%V`).
   - Proved that `2025-10-06` through `2025-10-12` is correctly designated as **ISO Week `2025-W41`**.
2. **Base Scenario Neutral Assumption Wording:**
   - Corrected Phase 3 report wording to **`Base Scenario — 10% Reduction Assumption`**.
   - Clarified that the ₹94,469/year value represents a modeled gross opportunity under the 10% reduction hypothesis, preserving strict separation between **OBSERVED**, **ASSUMED**, and **TARGET** parameters.
3. **Cohort Attribution: Closed vs. Assigned Definitions:**
   - **`Tickets Assigned`:** Tickets created/assigned to the agent during the reporting week.
   - **`Tickets Closed`:** Eligible tickets resolved/closed by the agent during the reporting week.
   - *Note on Asynchrony:* Because support cases can be assigned in Week $W-1$ and resolved in Week $W$, `Tickets Closed` can legitimately exceed `Tickets Assigned` for an agent in a given week without constituting a data error.

---

## 3. Tier Classification & Agent Assignment Methodology

### Team & Tier Boundaries (Support Operating Policy v3.2):
* **Tier 1 Frontline (Ranked by Weekly Closures):** `Chat Frontline`, `Email Frontline`, `Voice Frontline`.
* **Tier 2 / Escalations & Warranty (Evaluated by Cycle Time):** `Escalations & Warranty`.
* **Other Operational Back-Office Teams (Tracked Separately):** `Logistics`, `Billing`, `Returns Desk`.

### Temporal Roster Assignment & De-duplication Logic:
* **Temporal Roster Interval:** Agent metadata (`team`, `site`, `shift`, `tier`) is resolved against assignment intervals (`from_date <= ticket_date <= to_date`) in `agents.csv` to ensure historical promotions or site transfers are preserved.
* **Migration De-duplication:** All 653 cross-system duplicate re-import pairs are de-duplicated (retaining the primary `helpdesk` record) to prevent artificial inflation of agent closed-ticket counts.

---

## 4. View 1: Tier 1 Frontline Weekly Leaderboard (2025-W41)

> *Notice: Only eligible frontline agents (Chat, Email, Voice) are ranked. Multi-touch warranty cases are excluded.*

| Rank | Agent Name | Agent ID | Team | Site | Closed | Assigned | SLA Breach % | Avg CSAT | Repeat Contact % | Avg Handle Time |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **#1** | Rahul Sen | `A3012` | Chat Frontline | Bengaluru | **10** | 11 | 9.1% (1) | 3.50 (n=4) | 10.0% (1) | 19.0m |
| **#2** | Pooja Dhillon | `A3021` | Email Frontline | Bengaluru | **8** | 9 | 0.0% (0) | 4.00 (n=4) | 62.5% (5) | 384.5m |
| **#3** | Aishwarya Shinde | `A3004` | Chat Frontline | Bengaluru | **7** | 7 | 0.0% (0) | 3.25 (n=4) | 42.9% (3) | 22.9m |
| **#4** | Tenzin Saxena | `A3006` | Chat Frontline | Bengaluru | **6** | 6 | 0.0% (0) | 2.75 (n=4) | 50.0% (3) | 264.7m |
| **#5** | Kavya D'Souza | `A3019` | Email Frontline | Bengaluru | **6** | 6 | 50.0% (3) | 3.67 (n=3) | 0.0% (0) | 736.8m |
| **#6** | Kavya Goyal | `A3011` | Chat Frontline | Bengaluru | **5** | 5 | 0.0% (0) | 4.00 (n=1) | 20.0% (1) | 16.8m |
| **#7** | Sameer Menon | `A3005` | Chat Frontline | Indore | **5** | 6 | 16.7% (1) | 3.67 (n=3) | 40.0% (2) | 30.4m |
| **#8** | Om Varghese | `A3010` | Chat Frontline | Indore | **5** | 5 | 20.0% (1) | 4.00 (n=3) | 0.0% (0) | 20.8m |
| **#9** | Faisal Pereira | `A3015` | Chat Frontline | Indore | **5** | 5 | 20.0% (1) | 3.33 (n=3) | 20.0% (1) | 19.8m |
| **#10** | Yash Mittal ⚠️ (Small Sample) | `A3022` | Email Frontline | Bengaluru | **4** | 5 | 0.0% (0) | 4.33 (n=3) | 25.0% (1) | 15.8m |
| **#11** | Rohit Yadav ⚠️ (Small Sample) | `A3003` | Chat Frontline | Indore | **3** | 4 | 0.0% (0) | 4.00 (n=1) | 33.3% (1) | 28.7m |
| **#12** | Shreya Dhillon ⚠️ (Small Sample) | `A3007` | Chat Frontline | Bengaluru | **3** | 3 | 0.0% (0) | N/A (n=0) | 33.3% (1) | 16.3m |
| **#13** | Mohammed Kaur ⚠️ (Small Sample) | `A3024` | Voice Frontline | Indore | **3** | 3 | 33.3% (1) | N/A (n=0) | 33.3% (1) | 17.7m |
| **#14** | Zoya Srivastava ⚠️ (Small Sample) | `A3002` | Chat Frontline | Indore | **2** | 2 | 0.0% (0) | 4.00 (n=2) | 0.0% (0) | 14.5m |
| **#15** | Manish Jain ⚠️ (Small Sample) | `A3008` | Chat Frontline | Indore | **2** | 2 | 0.0% (0) | 4.00 (n=2) | 0.0% (0) | 35.5m |
| **#16** | Sameer Agarwal ⚠️ (Small Sample) | `A3009` | Chat Frontline | Bengaluru | **2** | 2 | 0.0% (0) | N/A (n=0) | 0.0% (0) | 31.0m |
| **#17** | Ayaan Dutta ⚠️ (Small Sample) | `A3013` | Chat Frontline | Bengaluru | **2** | 2 | 0.0% (0) | 3.00 (n=1) | 50.0% (1) | 22.5m |
| **#18** | Kabir Mathew ⚠️ (Small Sample) | `A3017` | Email Frontline | Indore | **2** | 3 | 0.0% (0) | N/A (n=0) | 0.0% (0) | 16.0m |
| **#19** | Vihaan Dutta ⚠️ (Small Sample) | `A3026` | Voice Frontline | Bengaluru | **2** | 2 | 0.0% (0) | 3.00 (n=1) | 0.0% (0) | 10.0m |
| **#20** | Manpreet Iyer ⚠️ (Small Sample) | `A3014` | Chat Frontline | Bengaluru | **2** | 2 | 50.0% (1) | 2.50 (n=2) | 50.0% (1) | 29.5m |
| **#21** | Ankit Ansari ⚠️ (Small Sample) | `A3020` | Email Frontline | Bengaluru | **2** | 2 | 50.0% (1) | 4.00 (n=2) | 0.0% (0) | 22.0m |
| **#22** | Shreya Kumar ⚠️ (Small Sample) | `A3001` | Chat Frontline | Indore | **1** | 2 | 0.0% (0) | N/A (n=0) | 0.0% (0) | 25.0m |
| **#23** | Ayaan Pawar ⚠️ (Small Sample) | `A3016` | Email Frontline | Indore | **1** | 1 | 0.0% (0) | N/A (n=0) | 100.0% (1) | 23.0m |
| **#24** | Farah George ⚠️ (Small Sample) | `A3023` | Voice Frontline | Indore | **1** | 1 | 0.0% (0) | 3.00 (n=1) | 100.0% (1) | 16.0m |
| **#25** | Riya Siddiqui ⚠️ (Small Sample) | `A3025` | Voice Frontline | Bengaluru | **1** | 1 | 0.0% (0) | 4.00 (n=1) | 0.0% (0) | 15.0m |

---

## 5. View 2: Tier 2 / Warranty Operational Performance (2025-W41)

> *Notice: Tier 2 agents are evaluated on diagnostic quality and resolution cycle time, NEVER on closed ticket volume.*

### Operational Metrics:
* **Total Cases Assigned (Inflow):** 9 cases
* **Total Cases Resolved (Closures):** 7 cases
* **Average Resolution Turnaround:** 6.76 days
* **Median Resolution Turnaround:** 5.38 days
* **Longest Case Duration:** 12.09 days
* **Warranty / RMA Replacements:** 1 units
* **30-Day Customer Repeat Rate:** 28.6% (2 return contacts)
* **Average CSAT:** 2.0 / 5.00 (n=1)

### Turnaround Duration Distribution:
* Under 2 Days: **1 cases**
* 2 to 5 Days: **0 cases**
* 5 to 10 Days: **4 cases**
* Over 10 Days: **2 cases**

### Unranked Agent Workload Breakdown:
| Agent Name | Agent ID | Site | Cases Assigned | Cases Resolved | Avg Resolution Days | Repeat Contacts |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Aishwarya Kaur | `A3042` | Bengaluru | 1 | 1 | 12.09 days | 0 |
| Meera Joshi | `A3044` | Indore | 4 | 3 | 3.86 days | 0 |
| Rahul Gupta | `A3043` | Bengaluru | 0 | 3 | 7.88 days | 2 |
| Sai Sharma | `A3040` | Bengaluru | 2 | 0 | N/A | 0 |
| Vivaan Kulkarni | `A3039` | Indore | 2 | 0 | N/A | 0 |

---

## 6. View 3: Other Operational Teams (2025-W41)

| Team Name | Tickets Closed | Average CSAT | Active Headcount |
| :--- | :---: | :---: | :---: |
| **Billing** | 36 | 3.77 (n=13) | 5 |
| **Logistics** | 28 | 2.86 (n=14) | 6 |
| **Returns Desk** | 24 | 3.60 (n=10) | 5 |

---

## 7. Week-over-Week Performance Trends

### Frontline (Tier 1) Delta vs. Prior Week (2025-W40):
* **Tickets Closed Change:** +8 tickets (+9.8%)
* **SLA Breach Rate Change:** +0.8% pts
* **Average CSAT Change:** +0.45 pts

### Warranty (Tier 2) Delta vs. Prior Week (2025-W40):
* **Cases Resolved Change:** -3 cases
* **Average Resolution Days Change:** +1.19 days

---

## 8. Phase 4 Metric Integrity Audit (Full 79-Week Dataset Scan)

An automated dataset-wide integrity scan was executed across all **79 calendar weeks (2025-W01 through 2026-W27)** covering all 12,528 tickets:

| Integrity Check | Scope | Violations Found | Status |
| :--- | :--- | :---: | :---: |
| **Non-Tier-1 Agents in Tier 1 Ranking** | All 79 weeks | **0** | PASSED |
| **Tier 2 Agents in Tier 1 Ranking** | All 79 weeks | **0** | PASSED |
| **Negative Ticket Counts (Closed / Assigned)** | All 79 weeks | **0** | PASSED |
| **CSAT Score Out-of-Bounds (<1.0 or >5.0)** | All 79 weeks | **0** | PASSED |
| **SLA Breaches > Assigned Tickets** | All 79 weeks | **0** | PASSED |
| **Repeat Contacts > Closed Tickets** | All 79 weeks | **0** | PASSED |
| **Negative Tier 2 Turnaround Days** | All 79 weeks | **0** | PASSED |

---

## 9. Data Quality & Small-Sample Warnings

* ⚠️ **Warning:** Small sample size warning (<5 closed tickets): Yash Mittal, Rohit Yadav, Shreya Dhillon, Mohammed Kaur and 12 others.
* ⚠️ **Warning:** Low CSAT response count (<3 responses): Kavya Goyal.

---

## 10. Recommendations for Phase 5

With all Phase 4 correction items verified and metric integrity proven across all 79 weeks:
1. **Streamlit Executive Dashboard:** Build a clean, modular decision-support dashboard integrating Executive KPIs, Complaint Intelligence, Tier 1 Leaderboards, Tier 2 Operations, and Financial ROI scenario modeling.
2. **Evidence Traceability:** Enable interactive drill-down from weekly aggregates directly into representative ticket IDs.
3. **Zero-Paid-API Architecture:** Ensure dashboard runtime operates 100% locally on existing Python engines.
