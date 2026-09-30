VIREO AUDIO Pvt. Ltd. — Take-Home Assignment: Customer Support Intelligence
Dataset & Schema Documentation (README)

Overview:
Vireo Audio is a Bengaluru-based consumer-audio and wearables brand (earbuds, headphones, smart speakers, watches) selling direct-to-consumer (DTC website) and via marketplaces (Amazon, Flipkart). Customer support is delivered across 4 channels (chat, email, voice callbacks, social) by 44 agents located across Bengaluru and Indore sites, working across 3 shifts (Morning 06:00-14:00, Day 14:00-22:00, Night 22:00-06:00 IST).

Files Provided:
- tickets.csv: Support ticket records from 1 January 2025 through 30 June 2026.
- agents.csv: Agent roster history with assignment intervals.
- customers.csv: Registered customer accounts.
- orders.csv: Customer purchase orders.
- products.csv: Product catalog with unit cost, retail price, and warranty terms.
- support-policy.pdf: Vireo Audio Customer Support Operating Policy v3.2.
- email-thread.txt: Email exchange between stakeholders (Priya Raman, Sameer, Arjun, Neha).

Schema Definitions:

1. tickets.csv:
- ticket_id: Helpdesk ticket number (string).
- created_at: Ticket creation timestamp (IST standard report / ISO-8601).
- first_response_at: First human agent reply timestamp.
- resolved_at: Resolution timestamp (blank if open/pending).
- status: Ticket status ('resolved', 'closed', 'open', 'pending').
- channel: Contact channel ('chat', 'email', 'voice', 'social').
- customer_id: Foreign key to customers.csv.
- order_id: Foreign key to orders.csv (blank when customer did not quote it).
- product_sku: Foreign key to products.csv.
- category: Issue category tag (set by bot on intake, agent may correct on closure).
- priority: Ticket priority ('Low', 'Normal', 'High').
- assigned_team: Initial routed team.
- agent_id: Resolving agent ID (foreign key to agents.csv).
- transfers: Hand-offs between teams (integer; exists only in current helpdesk).
- csat_score: Customer satisfaction survey score 1-5 (blank means no response; do not treat as 0).
- refund_amount_inr: Refund amount issued in INR (blank means none).
- refund_reason_code: Standard reason code from dropdown.
- replacement_issued: Replacement product issued ('Y', 'N').
- customer_message: Opening customer message / IVR transcript.
- agent_notes: Closing note recorded by resolving agent.
- source_system: System source ('helpdesk', 'legacy_fd').

2. agents.csv:
- agent_id: Unique agent identifier.
- name: Agent full name.
- site: Operational site ('Bengaluru', 'Indore').
- team: Assigned team (e.g., 'Chat Frontline', 'Escalations & Warranty', etc.).
- shift: Working shift ('Morning', 'Day', 'Night').
- tier: Tier classification ('Tier 1', 'Tier 2').
- from_date: Assignment start date (YYYY-MM-DD).
- to_date: Assignment end date (YYYY-MM-DD, or blank if active).
Note: Roster maintains 1 row per assignment; an agent changing site/shift receives a new row under the same agent_id.

3. customers.csv:
- customer_id: Unique customer identifier.
- name: Customer full name.
- city: Customer city.
- state: Customer state.
- signup_date: Account creation date (YYYY-MM-DD).
- care_plus: Care+ extended warranty subscription flag ('Y', 'N').

4. orders.csv:
- order_id: Unique order identifier.
- customer_id: Purchasing customer ID (foreign key to customers.csv).
- sku: Product SKU purchased (foreign key to products.csv).
- order_date: Purchase date (YYYY-MM-DD).
- channel: Sales channel ('Website', 'Amazon', 'Flipkart').
- qty: Quantity ordered.
- order_value_inr: Total order value in INR.
- lot_code: Manufacturing lot code.

5. products.csv:
- sku: Unique stock-keeping unit.
- product_name: Product marketing name.
- family: Product family ('Earbuds', 'Headphones', 'Smart Speakers', 'Watches').
- launch_date: Product launch date (YYYY-MM-DD).
- unit_cost_inr: Manufacturing / unit cost in INR.
- retail_price_inr: MSRP / retail selling price in INR.
- warranty_months: Standard warranty period in months.
