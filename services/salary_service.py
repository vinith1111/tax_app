from services.tax_service import new_tax, old_tax
from utils.constants import (
    PROFESSIONAL_TAX,
    STD_DEDUCTION_NEW,
    STD_DEDUCTION_OLD,
    PF_PERCENT,
    PF_CAP_MONTHLY,
    PF_INTEREST_RATE,
)


def calculate_salary(ctc, section_80c=150_000, hra=0, other=0):
    basic = ctc * 0.5

    # PF capped at ₹15,000/month basic
    #pf_annual = min(basic * PF_PERCENT, PF_CAP_MONTHLY * 12)
    pf_annual = basic * 0.12 #calculation based on actual basic
    employer_pf = pf_annual
    employee_pf = pf_annual
    pf_taxable_contribution_excess = max(employee_pf - 250_000, 0)
    taxable_pf_interest = pf_taxable_contribution_excess * PF_INTEREST_RATE

    gross = ctc - employer_pf

    # ── NEW REGIME ──────────────────────────────────────────────
    taxable_new = max(gross - STD_DEDUCTION_NEW, 0)

    base_tax_new, surcharge_new, cess_new, tax_new = new_tax(taxable_new)

    original_tax_new = tax_new  # before relief

    REBATE_LIMIT_NEW = 1200000  # ₹12L

    if taxable_new <= REBATE_LIMIT_NEW:
        tax_new = 0
        excess = 0
        threshold_msg = "🟢 Within ₹12L rebate zone (No tax)"
    else:
        excess = taxable_new - REBATE_LIMIT_NEW

        if tax_new > excess:
            tax_new = excess

        threshold_msg = "🟠 Above ₹12L - Marginal relief applied"

    # Marginal relief savings
    marginal_relief_savings = max(original_tax_new - tax_new, 0)

    inhand_new = gross - employee_pf - tax_new - PROFESSIONAL_TAX

    # ── OLD REGIME ──────────────────────────────────────────────
    deductions = STD_DEDUCTION_OLD + PROFESSIONAL_TAX + section_80c + hra + other

    taxable_old = max(gross - deductions, 0)

    base_tax_old, surcharge_old, cess_old, tax_old = old_tax(taxable_old)

    REBATE_LIMIT_OLD = 500000

    if taxable_old <= REBATE_LIMIT_OLD:
        tax_old = 0

    inhand_old = gross - employee_pf - tax_old - PROFESSIONAL_TAX

    # ── DERIVED INSIGHTS ─────────────────────────────────────────
    monthly_inhand_new = inhand_new / 12
    monthly_inhand_old = inhand_old / 12

    effective_tax_new = (tax_new / gross) * 100 if gross > 0 else 0
    effective_tax_old = (tax_old / gross) * 100 if gross > 0 else 0

    # Best regime
    if inhand_new > inhand_old:
        best_regime = "New Regime 🟢"
        benefit = inhand_new - inhand_old
    else:
        best_regime = "Old Regime 🔵"
        benefit = inhand_old - inhand_new

    # Extras
    excess_income = excess if taxable_new > REBATE_LIMIT_NEW else 0

    return {
        # In-hand
        "new_inhand": round(inhand_new),
        "old_inhand": round(inhand_old),

        # Monthly
        "monthly_new": round(monthly_inhand_new),
        "monthly_old": round(monthly_inhand_old),

        # Salary structure
        "basic": round(basic),
        "employer_pf": round(employer_pf),
        "employee_pf": round(employee_pf),
        "gross": round(gross),
        "pf_taxable_contribution_excess": round(pf_taxable_contribution_excess),
        "taxable_pf_interest": round(taxable_pf_interest),

        # New regime tax breakdown
        "taxable_new": round(taxable_new),
        "base_tax_new": base_tax_new,
        "surcharge_new": surcharge_new,
        "cess_new": cess_new,
        "tax_new": tax_new,

        # Old regime tax breakdown
        "taxable_old": round(taxable_old),
        "base_tax_old": base_tax_old,
        "surcharge_old": surcharge_old,
        "cess_old": cess_old,
        "tax_old": tax_old,

        # Insights
        "effective_tax_new": round(effective_tax_new, 2),
        "effective_tax_old": round(effective_tax_old, 2),
        "best_regime": best_regime,
        "benefit_amount": round(benefit),

        # Marginal relief
        "excess_income": round(excess_income),
        "marginal_relief_savings": round(marginal_relief_savings),

        # UX message
        "threshold_message": threshold_msg,
    }
