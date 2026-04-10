from services.tax_service import new_tax, old_tax
from utils.constants import (
    PROFESSIONAL_TAX,
    STD_DEDUCTION_NEW,
    STD_DEDUCTION_OLD,
    PF_PERCENT,
    PF_CAP_MONTHLY,
)

def calculate_salary(ctc, section_80c=150_000, hra=0, other=0):
    basic = ctc * 0.5

    # PF capped at ₹15,000/month basic
    pf_annual = min(basic * PF_PERCENT, PF_CAP_MONTHLY * 12)
    employer_pf = pf_annual
    employee_pf = pf_annual

    gross = ctc - employer_pf

    # ── NEW REGIME ──────────────────────────────────────────────
    taxable_new = max(gross - STD_DEDUCTION_NEW, 0)
    base_tax_new, surcharge_new, cess_new, tax_new = new_tax(taxable_new)
    inhand_new = gross - employee_pf - tax_new - PROFESSIONAL_TAX
    excess_income = max(taxable_new - 1_200_000, 0)

    # ── OLD REGIME ──────────────────────────────────────────────
    deductions = STD_DEDUCTION_OLD + PROFESSIONAL_TAX + section_80c + hra + other
    taxable_old = max(gross - deductions, 0)
    base_tax_old, surcharge_old, cess_old, tax_old = old_tax(taxable_old)
    inhand_old = gross - employee_pf - tax_old - PROFESSIONAL_TAX

    return {
        # In-hand
        "new_inhand": round(inhand_new),
        "old_inhand": round(inhand_old),

        # Salary structure
        "basic": round(basic),
        "employer_pf": round(employer_pf),
        "employee_pf": round(employee_pf),
        "gross": round(gross),

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

        # Extras
        "excess_income": round(excess_income),
    }
