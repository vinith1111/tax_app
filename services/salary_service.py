from services.tax_service import apply_surcharge
from utils.constants import *

def calculate_salary(ctc, section_80c=150000, hra=0, other=0):

    basic = ctc * 0.5
    employer_pf = basic * PF_PERCENT
    employee_pf = basic * PF_PERCENT

    gross = ctc - employer_pf

    # ---------- NEW REGIME ----------
    taxable_new = max(gross - STD_DEDUCTION_NEW, 0)

    base_tax_new = 0
    temp = taxable_new

    slabs = [
        (400000, 0),(400000, 0.05),(400000, 0.10),
        (400000, 0.15),(400000, 0.20),(400000, 0.25),
        (float('inf'), 0.30)
    ]

    for limit, rate in slabs:
        if temp > 0:
            taxable = min(temp, limit)
            base_tax_new += taxable * rate
            temp -= taxable

    total_with_surcharge_new = apply_surcharge(base_tax_new, taxable_new, "new")
    surcharge_new = total_with_surcharge_new - base_tax_new
    cess_new = (base_tax_new + surcharge_new) * 0.04

    tax_new = base_tax_new + surcharge_new + cess_new

    inhand_new = gross - employee_pf - tax_new - PROFESSIONAL_TAX

    # ---------- OLD REGIME ----------
    deductions = STD_DEDUCTION_OLD + PROFESSIONAL_TAX + section_80c + hra + other
    taxable_old = max(gross - deductions, 0)

    base_tax_old = 0
    temp = taxable_old

    slabs_old = [
        (250000, 0),(250000, 0.05),
        (500000, 0.20),(float('inf'), 0.30)
    ]

    for limit, rate in slabs_old:
        if temp > 0:
            taxable = min(temp, limit)
            base_tax_old += taxable * rate
            temp -= taxable

    total_with_surcharge_old = apply_surcharge(base_tax_old, taxable_old, "old")
    surcharge_old = total_with_surcharge_old - base_tax_old
    cess_old = (base_tax_old + surcharge_old) * 0.04

    tax_old = base_tax_old + surcharge_old + cess_old

    inhand_old = gross - employee_pf - tax_old - PROFESSIONAL_TAX

    return {
        "new_inhand": round(inhand_new),
        "old_inhand": round(inhand_old),

        "basic": round(basic),
        "employer_pf": round(employer_pf),
        "employee_pf": round(employee_pf),
        "gross": round(gross),

        "base_tax_new": round(base_tax_new),
        "surcharge_new": round(surcharge_new),
        "cess_new": round(cess_new),
        "tax_new": round(tax_new),

        "base_tax_old": round(base_tax_old),
        "surcharge_old": round(surcharge_old),
        "cess_old": round(cess_old),
        "tax_old": round(tax_old)
    }
