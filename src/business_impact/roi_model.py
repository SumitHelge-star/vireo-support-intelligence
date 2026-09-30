"""
Business Impact and ROI Modeling Module for Vireo Audio Support Intelligence.
Computes deterministic financial baselines, scenario opportunities, break-even analyses,
and ensures complete transparency between observed, assumed, and target parameters.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.config import (
    CONTACT_COSTS_INR,
    BLENDED_CONTACT_COST_INR,
    SLA_BREACH_STORE_CREDIT_INR,
    INTERNAL_TRANSFER_COST_INR,
    AGENT_HOURLY_LOADED_COST_INR,
)


@dataclass
class ScenarioResult:
    scenario_name: str
    reduction_percentage: float
    avoided_repeat_contacts_18m: int
    avoided_repeat_cost_18m_inr: float
    annualized_avoided_repeat_cost_inr: float
    avoided_sla_breaches_18m: int
    avoided_sla_liability_18m_inr: float
    annualized_avoided_sla_liability_inr: float
    total_gross_savings_18m_inr: float
    total_annualized_gross_savings_inr: float
    tool_annual_cost_inr: float
    net_annual_benefit_inr: float
    roi_percentage: Optional[float]
    payback_period_months: Optional[float]


@dataclass
class BusinessImpactSummary:
    dataset_period_start: str
    dataset_period_end: str
    total_days: int
    total_tickets: int
    annualized_ticket_volume: float
    
    # Repeat contact baseline
    total_repeat_contacts: int
    repeat_contact_rate: float
    repeat_contact_cost_channel_specific_18m_inr: float
    repeat_contact_cost_blended_18m_inr: float
    annualized_repeat_cost_channel_specific_inr: float
    annualized_repeat_cost_blended_inr: float
    
    # SLA breach baseline
    total_sla_breaches: int
    sla_breach_rate: float
    total_sla_liability_18m_inr: float
    annualized_sla_liability_inr: float
    
    # Total baseline addressable friction
    total_addressable_friction_18m_inr: float
    total_annualized_addressable_friction_inr: float
    
    # Scenario outcomes
    scenarios: Dict[str, Dict[str, Any]]
    
    # Metadata and governance
    observed_vs_assumed_parameters: Dict[str, str]
    methodology_and_limitations: List[str]


def calculate_business_impact(
    df_tickets: pd.DataFrame,
    tool_annual_cost_inr: float = 0.0,
    scenarios_pct: Optional[Dict[str, float]] = None,
) -> BusinessImpactSummary:
    """
    Computes deterministic business impact metrics, channel-level costs,
    SLA credit liabilities, scenario projections, and ROI models.
    """
    if scenarios_pct is None:
        scenarios_pct = {
            "Conservative": 0.05,
            "Base": 0.10,
            "Stretch": 0.20,
        }

    df = df_tickets.copy()
    
    # Ensure created_dt and resolved_dt exist
    if "created_dt" not in df.columns:
        df["created_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
    
    # 1. Dataset period and volume
    min_date = df["created_dt"].min()
    max_date = df["created_dt"].max()
    total_days = max(1, (max_date - min_date).days + 1)
    years_elapsed = total_days / 365.25
    total_tickets = len(df)
    annualized_ticket_volume = round(total_tickets / years_elapsed, 2)
    
    # 2. Repeat contact baseline
    # Check if repeat contact columns are computed
    if "is_repeat_contact" not in df.columns:
        from src.complaint_analysis.repeat_contact import calculate_repeat_contacts
        df, _ = calculate_repeat_contacts(df)
        
    repeats_df = df[df["is_repeat_contact"]].copy()
    total_repeat_contacts = len(repeats_df)
    repeat_contact_rate = round((total_repeat_contacts / total_tickets) * 100, 2)
    
    # Calculate channel-specific vs blended repeat contact cost
    repeat_cost_channel_specific_18m = float(repeats_df["repeat_contact_cost_inr"].sum())
    repeat_cost_blended_18m = float(total_repeat_contacts * BLENDED_CONTACT_COST_INR)
    
    annualized_repeat_cost_channel_specific = round(repeat_cost_channel_specific_18m / years_elapsed, 2)
    annualized_repeat_cost_blended = round(repeat_cost_blended_18m / years_elapsed, 2)
    
    # 3. SLA breach baseline
    if "is_sla_breached" not in df.columns:
        from src.config import SLA_TARGET_MINUTES
        if "first_response_dt" not in df.columns:
            df["first_response_dt"] = pd.to_datetime(df["first_response_at"], errors="coerce")
        resp_mins = (df["first_response_dt"] - df["created_dt"]).dt.total_seconds() / 60.0
        targets = df["channel"].map(SLA_TARGET_MINUTES)
        df["is_sla_breached"] = resp_mins > targets
        
    breaches_df = df[df["is_sla_breached"]].copy()
    total_sla_breaches = len(breaches_df)
    sla_breach_rate = round((total_sla_breaches / total_tickets) * 100, 2)
    total_sla_liability_18m = float(total_sla_breaches * SLA_BREACH_STORE_CREDIT_INR)
    annualized_sla_liability = round(total_sla_liability_18m / years_elapsed, 2)
    
    # 4. Total addressable friction
    total_friction_18m = repeat_cost_channel_specific_18m + total_sla_liability_18m
    total_annualized_friction = round(total_friction_18m / years_elapsed, 2)
    
    # 5. Scenario evaluations
    scenario_results: Dict[str, Dict[str, Any]] = {}
    
    for s_name, pct in scenarios_pct.items():
        avoided_repeats_18m = int(round(total_repeat_contacts * pct))
        avoided_repeat_cost_18m = round(repeat_cost_channel_specific_18m * pct, 2)
        annual_avoided_repeat_cost = round(avoided_repeat_cost_18m / years_elapsed, 2)
        
        avoided_breaches_18m = int(round(total_sla_breaches * pct))
        avoided_sla_liability_18m = round(total_sla_liability_18m * pct, 2)
        annual_avoided_sla_liability = round(avoided_sla_liability_18m / years_elapsed, 2)
        
        total_gross_18m = round(avoided_repeat_cost_18m + avoided_sla_liability_18m, 2)
        total_annual_gross = round(annual_avoided_repeat_cost + annual_avoided_sla_liability, 2)
        
        net_annual = round(total_annual_gross - tool_annual_cost_inr, 2)
        
        # ROI and Payback Period calculations
        if tool_annual_cost_inr > 0:
            roi_pct = round((net_annual / tool_annual_cost_inr) * 100, 2)
            monthly_gross = total_annual_gross / 12.0
            payback_months = round(tool_annual_cost_inr / monthly_gross, 2) if monthly_gross > 0 else None
        else:
            roi_pct = None  # Free / Open-source local runtime (infinite theoretical ROI)
            payback_months = 0.0  # Immediate payback with zero software capital outlay
            
        res = ScenarioResult(
            scenario_name=s_name,
            reduction_percentage=round(pct * 100, 1),
            avoided_repeat_contacts_18m=avoided_repeats_18m,
            avoided_repeat_cost_18m_inr=avoided_repeat_cost_18m,
            annualized_avoided_repeat_cost_inr=annual_avoided_repeat_cost,
            avoided_sla_breaches_18m=avoided_breaches_18m,
            avoided_sla_liability_18m_inr=avoided_sla_liability_18m,
            annualized_avoided_sla_liability_inr=annual_avoided_sla_liability,
            total_gross_savings_18m_inr=total_gross_18m,
            total_annualized_gross_savings_inr=total_annual_gross,
            tool_annual_cost_inr=tool_annual_cost_inr,
            net_annual_benefit_inr=net_annual,
            roi_percentage=roi_pct,
            payback_period_months=payback_months,
        )
        scenario_results[s_name] = asdict(res)

    # 6. Documentation of parameters
    observed_vs_assumed = {
        "dataset_total_tickets": "OBSERVED (Exact row count from tickets.csv)",
        "dataset_date_span": "OBSERVED (2025-01-01 to 2026-06-30 across 12,528 tickets)",
        "channel_contact_costs": "OBSERVED (Support Policy v3.2 schedule: Chat Rs 210, Email Rs 260, Voice Rs 520, Social Rs 240)",
        "blended_contact_cost": "OBSERVED (Support Policy v3.2: Priya Raman verified blended benchmark Rs 290)",
        "sla_breach_store_credit": "OBSERVED (Support Policy v3.2: Flat Rs 350 credit per first-response breach)",
        "repeat_contact_volume": "OBSERVED (Deterministic 30-day customer re-contact window count)",
        "scenario_reduction_percentages": "ASSUMED (5% Conservative, 10% Base, 20% Stretch modeled for scenario analysis)",
        "sla_breach_reduction_linkage": "ASSUMED (Modeled under proportional friction reduction hypothesis; not guaranteed)",
        "tool_annual_cost": "OBSERVED / CONFIGURED (Free local Python/scikit-learn runtime = Rs 0 recurring cloud API cost)",
    }
    
    limitations = [
        "Customer repeat-contact matching approximates exact same-issue FCR due to absence of full conversational transcripts in legacy Freshdesk imports.",
        "Annualization assumes customer inflow and complaint seasonality remain consistent over subsequent 12-month operating periods.",
        "SLA credit liability assumes 100% of eligible first-response breaches trigger store credit issuance without customer waiver or manual exclusion.",
        "Scenario reduction rates (5%, 10%, 20%) represent modeled opportunities and do not constitute guaranteed future performance.",
    ]

    return BusinessImpactSummary(
        dataset_period_start=min_date.strftime("%Y-%m-%d"),
        dataset_period_end=max_date.strftime("%Y-%m-%d"),
        total_days=total_days,
        total_tickets=total_tickets,
        annualized_ticket_volume=annualized_ticket_volume,
        total_repeat_contacts=total_repeat_contacts,
        repeat_contact_rate=repeat_contact_rate,
        repeat_contact_cost_channel_specific_18m_inr=repeat_cost_channel_specific_18m,
        repeat_contact_cost_blended_18m_inr=repeat_cost_blended_18m,
        annualized_repeat_cost_channel_specific_inr=annualized_repeat_cost_channel_specific,
        annualized_repeat_cost_blended_inr=annualized_repeat_cost_blended,
        total_sla_breaches=total_sla_breaches,
        sla_breach_rate=sla_breach_rate,
        total_sla_liability_18m_inr=total_sla_liability_18m,
        annualized_sla_liability_inr=annualized_sla_liability,
        total_addressable_friction_18m_inr=total_friction_18m,
        total_annualized_addressable_friction_inr=total_annualized_friction,
        scenarios=scenario_results,
        observed_vs_assumed_parameters=observed_vs_assumed,
        methodology_and_limitations=limitations,
    )
