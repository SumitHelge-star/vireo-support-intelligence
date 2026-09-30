# MEMORANDUM

**TO:** Priya Raman, Head of Customer Experience  
**CC:** Neha Kulkarni, Support Operations Manager; Arjun Mehta, Finance Controller  
**FROM:** Senior Customer Experience & Analytics Engineering Lead  
**DATE:** September 30, 2026  
**SUBJECT:** Customer Support Intelligence — Weekly Decision-Support Pilot  

---

### EXECUTIVE SUMMARY
To provide actionable weekly decision support without building an expensive, complex platform, we developed the **Vireo Audio Support Intelligence System**. Operating 100% locally with zero external API fees, the system digests operational logs to answer four core business questions: what customers complain about, where operational friction occurs, how frontline agents perform, and what financial impact can be captured. Over an 18-month historical baseline (12,528 tickets; 8,381 annualized), the data reveals **₹9.45 Lakh/year** in addressable operating friction driven by repeat contacts (30.2%) and SLA first-response breaches (8.9%). Under a **10% friction reduction scenario assumption**, the modeled annual gross opportunity is **₹94,469 / year** at ₹0 software operating cost.

---

### WHAT THE DATA SHOWS
1. **Customer Inflow & Repeat Friction:** Vireo receives ~160–210 tickets weekly (8,381 annualized). The 30-day customer repeat contact rate is **30.2%** (3,788 return tickets), heavily concentrated in Bluetooth pairing and battery drain inquiries for the *Pulse 2 Earbuds* (`VA-EB-PL2`) and *Wave Pro Headphones* (`VA-HP-WP`).
2. **SLA Adherence & Credit Liabilities:** First-response SLA breach rate is **8.9%** (1,119 tickets across 18 months), triggering **₹3.92 Lakh** in store credit policy liabilities (₹350 credit per breach).
3. **Frontline Throughput vs. Context:** Frontline agents (Chat, Email, Voice) close an average of 6–10 tickets weekly. Volume leaderboards provide operational visibility but are contextualized with CSAT, SLA adherence, and repeat contact rates to avoid distorting service quality.
4. **Tier 2 Multi-Day Resolution:** Escalations & Warranty cases require deep investigation and vendor RMA shipping, averaging **5.38 days median turnaround** (5.86 days mean). Because cases span multiple days, weekly closures represent cross-week cohorts ($Closed > Assigned$ is normal operational outflow).

---

### BUSINESS IMPACT & FINANCIAL OPPORTUNITY
Addressing Arjun Mehta’s core question (*"What does it save?"*), we distinguish **observed baseline costs** from **modeled scenario opportunities**:

* **Observed Annualized Operating Friction Baseline:**
  * Repeat Contact Handling (Channel Cost Schedule: Voice ₹520, Email ₹260, Social ₹240, Chat ₹210): **₹6,82,635 / year**
  * Automated SLA Breach Store Credit Liability (₹350 flat credit): **₹2,62,058 / year**
  * **Total Addressable Annual Friction Baseline:** **₹9,44,693 / year** (18-Month Total: ₹14,12,190)

| Scenario Model | Reduction Assumption | Avoided Repeat Cost | Avoided SLA Credits | Modeled Annual Opportunity | Software Cost | Net Annual Benefit |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Conservative** | 5.0% | ₹34,132 / yr | ₹13,103 / yr | **₹47,235 / year** | ₹0 | **₹47,235 / year** |
| **Base** | 10.0% | ₹68,264 / yr | ₹26,206 / yr | **₹94,469 / year** | ₹0 | **₹94,469 / year** |
| **Stretch** | 20.0% | ₹1,36,527 / yr | ₹52,412 / yr | **₹1,88,939 / year** | ₹0 | **₹1,88,939 / year** |

*Note: Reduction percentages are modeled scenario assumptions, not observed historical results or guaranteed savings.*

---

### WHAT THE TOOL DOES
The lightweight **Streamlit Executive Dashboard** (`streamlit run app/streamlit_app.py`) provides:
1. **Executive Overview:** High-level KPIs with true Week-over-Week deltas and automated briefing narrative.
2. **Complaint Intelligence:** Dynamic topic clustering (TF-IDF + KMeans) with verifiable raw ticket citation drill-downs.
3. **Frontline Leaderboard:** Tier 1 volume ranking with small-sample shields (`⚠️ Small Sample (<5)`) and context metrics.
4. **Tier 2 Operations:** Cycle time diagnostics, duration distribution (<2d, 2–5d, 5–10d, >10d), and unranked workload views.
5. **Financial ROI Simulator:** Interactive scenario testing and break-even budget thresholds for finance review.

---

### GOVERNANCE & OPERATIONAL SAFEGUARDS
* **Strict Tier Separation:** Per Neha Kulkarni's operational mandate, Tier 2 / Warranty agents are **strictly excluded from volume leaderboards** to prevent rushing hardware diagnostics.
* **Fairness Safeguards:** Small-sample agents are shielded to prevent outlier distortion; ranking uses pure volume rather than opaque composite scoring.
* **Data Quality Transparency:** Historical ticket text is unstructured; the largest complaint cluster (~44.2%) is broad/generic, requiring cited raw-ticket inspection. CSAT excludes legacy zero-encoded non-responses.

---

### PROPOSED NEXT STEPS
1. **Pilot Weekly Review:** CX leadership utilizes the dashboard for weekly operational standups starting with ISO week `2025-W41`.
2. **Targeted Frontline Interventions:** Deploy standard troubleshooting macros for *Pulse 2* Bluetooth pairing to reduce repeat contacts.
3. **Measure Impact:** Track whether weekly repeat contact rates and SLA breach liabilities decrease over an 8-week evaluation window against the baseline.
