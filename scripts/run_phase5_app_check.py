"""
Phase 5 Headless Dashboard Execution and Smoke Check Script.
Validates that Streamlit dashboard data loaders, components, and weekly payloads execute error-free.
"""

from pathlib import Path
import sys
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_all_datasets
from src.normalization import derive_ticket_features
from src.complaint_analysis.repeat_contact import calculate_repeat_contacts
from src.complaint_analysis.weekly_digest import generate_weekly_digest
from src.business_impact.roi_model import calculate_business_impact
from src.performance import (
    resolve_agent_assignment,
    build_weekly_performance_payload,
)


def main():
    print("=" * 70)
    print("VIREO AUDIO SUPPORT INTELLIGENCE -- PHASE 5 DASHBOARD APP CHECK")
    print("=" * 70)

    print("\n[1/4] Testing data loaders and deterministic pipelines...")
    datasets = load_all_datasets()
    df_tickets = derive_ticket_features(datasets["tickets"], datasets.get("orders"))
    df_tickets, repeat_summary = calculate_repeat_contacts(df_tickets)
    df_tickets = resolve_agent_assignment(df_tickets, datasets["agents"])
    financial_summary = calculate_business_impact(df_tickets, tool_annual_cost_inr=0.0)
    print(f"  [OK] Successfully prepared {len(df_tickets):,} tickets across {len(datasets['agents'])} agents")

    print("\n[2/4] Validating weekly performance & complaint payload generation...")
    test_week = "2025-W41"
    weekly_digest = generate_weekly_digest(df_tickets, target_week=test_week, n_clusters=5)
    performance_payload = build_weekly_performance_payload(
        df_tickets=df_tickets,
        df_agents=datasets["agents"],
        target_week=test_week,
        previous_week="2025-W40",
    )
    print(f"  [OK] Weekly Digest Generated: {weekly_digest['target_week']} ({weekly_digest['total_tickets']} tickets)")
    print(f"  [OK] Tier 1 Frontline Leaderboard: {len(performance_payload['tier1_frontline_leaderboard'])} ranked agents")
    print(f"  [OK] Tier 2 Operational Summary: {performance_payload['tier2_warranty_operational_summary']['cases_handled']} cases handled (unranked)")

    print("\n[3/4] Validating financial model integration...")
    base_sc = financial_summary.scenarios["Base"]
    print(f"  [OK] Base Scenario Annual Opportunity: Rs {base_sc['total_annualized_gross_savings_inr']:,.0f} / year")
    print(f"  [OK] Tool Cost: Rs {base_sc['tool_annual_cost_inr']:,.0f} (Local/Free runtime)")

    print("\n[4/4] Validating component importability...")
    from app.components import (
        render_kpi_cards,
        render_complaint_view,
        render_performance_view,
        render_tier2_view,
        render_finance_view,
    )
    print("  [OK] All Streamlit UI components imported successfully")

    print("\n" + "=" * 70)
    print("PHASE 5 DASHBOARD SMOKE CHECK COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
