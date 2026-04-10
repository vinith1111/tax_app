from services.tax_service import new_tax, old_tax
from utils.constants import *

def calculate_salary(ctc, section_80c=150000, hra=0, other=0):

    basic = ctc * 0.5
    employer_pf = basic * PF_PERCENT
    employee_pf = basic * PF_PERCENT

    gross = ctc - employer_pf

    taxable_new = max(gross - STD_DEDUCTION_NEW, 0)
    tax_new = new_tax(taxable_new)
    inhand_new = gross - employee_pf - tax_new - PROFESSIONAL_TAX

    deductions = STD_DEDUCTION_OLD + PROFESSIONAL_TAX + section_80c + hra + other
    taxable_old = max(gross - deductions, 0)
    tax_old = old_tax(taxable_old)
    inhand_old = gross - employee_pf - tax_old - PROFESSIONAL_TAX

    return round(inhand_new), round(inhand_old)
