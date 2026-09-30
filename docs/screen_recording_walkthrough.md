# VIREO AUDIO SUPPORT INTELLIGENCE
## Executive Screen-Recording Walkthrough Script (3-Minute Demonstration)

**Presenter:** Lead Customer Experience & Analytics Engineer  
**Audience:** Priya Raman (Head of CX), Neha Kulkarni (Support Operations Manager), Arjun Mehta (Finance Controller)  
**Total Target Duration:** 2 minutes 50 seconds (< 3 minutes)  
**Command to Run Application:** `streamlit run app/streamlit_app.py`

---

### [0:00 – 0:20] 1. Problem Statement & Executive Purpose
* **Visual:** Browser showing the Vireo Audio Support Intelligence Dashboard running on `http://localhost:8501`. Sidebar displays ISO Week Selector (`2025-W41`).
* **Speaker Script:**
  > *"Hello Priya, Neha, and Arjun. Today I am presenting the Vireo Audio Support Intelligence tool. Customer support leadership needs a lightweight, weekly decision-support layer to track customer complaint drivers, monitor frontline agent throughput, oversee escalation cycle times, and quantify financial operating friction—all without building an expensive, complex software platform or paying per-ticket AI cloud bills."*

---

### [0:20 – 0:50] 2. Executive Overview & Weekly Macro KPIs
* **Visual:** Highlight **Tab 1: Executive Overview**. Point mouse to the 4 KPI cards and narrative brief.
* **Speaker Script:**
  > *"Starting in our Executive Overview for ISO week 2025-W41, the dashboard immediately reveals key weekly indicators: 203 tickets received (+4.1% WoW), a 28.1% 30-day customer repeat contact rate, an 7.9% first-response SLA breach rate, and an average valid CSAT of 3.48 across 168 surveys. On the far right, we display our modeled annual financial opportunity—₹94,469 per year under a conservative 10% friction reduction assumption. Below, an automated briefing highlights operational risks and top product friction drivers."*

---

### [0:50 – 1:20] 3. Customer Complaint Intelligence & Verifiable Evidence
* **Visual:** Switch to **Tab 2: Customer Complaints**. Show the cluster summary table, then select a cluster in the drill-down dropdown to reveal the underlying raw ticket rows.
* **Speaker Script:**
  > *"Moving to Customer Complaints, the system uses local TF-IDF vectorization and KMeans clustering to categorize weekly issues into actionable groups like Billing & Payments and Delivery Inquiries. Importantly, we provide full transparency: our data quality notice explains that the largest macro group is broad and generic due to unstructured ticket descriptions. Leadership can immediately drill down into any topic to read exact customer opening messages and verify ticket IDs, such as TK-244806, ensuring 100% trust in the findings."*

---

### [1:20 – 1:50] 4. Role-Governed Performance: Tier 1 vs. Tier 2
* **Visual:** Switch to **Tab 3: Frontline Performance**, showing ranked leaderboard with `⚠️ Small Sample (<5)` tags. Then switch to **Tab 4: Tier 2 Operations**, highlighting turnaround metrics and the unranked workload table.
* **Speaker Script:**
  > *"In Frontline Performance, Tier 1 agents in Chat, Email, and Voice are ranked strictly by closed tickets, such as Rahul Sen with 7 closures. Supporting metrics like CSAT, SLA breach rate, and handle time provide vital context without distorting rankings through opaque scoring. Agents with under 5 closures receive explicit small-sample tags.*  
  > *Next, in Tier 2 Operations, we enforce Neha’s crucial governance rule: Escalations and Warranty are NEVER ranked by ticket volume. These multi-day hardware cases average a 5.38-day median turnaround. Cases resolved in a week frequently exceed cases assigned because multi-touch investigations span weekly boundaries."*

---

### [1:50 – 2:20] 5. Financial Impact & Arjun Mehta's ROI Model
* **Visual:** Switch to **Tab 5: Financial Impact**. Toggle through Conservative (5%), Base (10%), and Stretch (20%) scenario radios.
* **Speaker Script:**
  > *"In Financial Impact, we answer Arjun Mehta's core question: 'What does it save?' Across our 18-month historical baseline, repeat contact handling and SLA credit liabilities total ₹9.45 Lakh per year in addressable friction. Using our scenario selector, we model potential opportunities: ₹47,000 at 5%, ₹94,000 at 10%, and ₹1.89 Lakh at 20%. Because our analytical pipeline runs 100% locally with open-source Python, software operating costs are ₹0, delivering an immediate positive net return."*

---

### [2:20 – 2:45] 6. Architecture, Integrity & Test Suite
* **Visual:** Switch to **Tab 6: Data Integrity & Governance**, briefly scrolling through test verification stats and policy rules.
* **Speaker Script:**
  > *"Behind this dashboard is an enterprise data foundation: immutable raw CSVs, deterministic feature derivations, and 44 automated pytest unit tests validating every business rule from zero-encoded CSAT filtering to duplicate ticket deduplication. There are zero hallucinated metrics or paid API dependencies."*

---

### [2:45 – 3:00] 7. Closing & Next Steps
* **Visual:** Return to **Tab 1: Executive Overview**.
* **Speaker Script:**
  > *"In summary, this dashboard gives Vireo leadership an evidence-backed, weekly decision-support cockpit. We recommend using it for weekly standups to deploy targeted troubleshooting interventions on high-friction products like the Pulse 2 Earbuds. Thank you."*
