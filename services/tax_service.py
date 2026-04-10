def apply_surcharge(tax, income, regime):
    if income > 50_000_000:
        rate = 0.25 if regime == "new" else 0.37
    elif income > 20_000_000:
        rate = 0.25
    elif income > 10_000_000:
        rate = 0.15
    elif income > 5_000_000:
        rate = 0.10
    else:
        rate = 0
    return tax * (1 + rate)


def new_tax(taxable_income):
    """
    New regime slabs (FY 2024-25).
    87A rebate: if taxable ≤ ₹12L → zero tax.
    """
    if taxable_income <= 0:
        return 0, 0, 0

    slabs = [
        (400_000, 0.00),
        (400_000, 0.05),
        (400_000, 0.10),
        (400_000, 0.15),
        (400_000, 0.20),
        (400_000, 0.25),
        (float("inf"), 0.30),
    ]

    base_tax = 0
    temp = taxable_income
    for limit, rate in slabs:
        chunk = min(temp, limit)
        base_tax += chunk * rate
        temp -= chunk
        if temp <= 0:
            break

    # Section 87A rebate — zero tax if taxable ≤ ₹12L
    if taxable_income <= 1_200_000:
        base_tax = 0

    total_with_surcharge = apply_surcharge(base_tax, taxable_income, "new")
    surcharge = total_with_surcharge - base_tax
    cess = (base_tax + surcharge) * 0.04
    total_tax = base_tax + surcharge + cess

    return round(base_tax), round(surcharge), round(cess), round(total_tax)


def old_tax(taxable_income):
    """
    Old regime slabs.
    87A rebate: if taxable ≤ ₹5L → zero tax (rebate up to ₹12,500).
    """
    if taxable_income <= 0:
        return 0, 0, 0, 0

    slabs = [
        (250_000, 0.00),
        (250_000, 0.05),
        (500_000, 0.20),
        (float("inf"), 0.30),
    ]

    base_tax = 0
    temp = taxable_income
    for limit, rate in slabs:
        chunk = min(temp, limit)
        base_tax += chunk * rate
        temp -= chunk
        if temp <= 0:
            break

    # Section 87A rebate — up to ₹12,500 for income ≤ ₹5L
    if taxable_income <= 500_000:
        base_tax = max(0, base_tax - 12_500)

    total_with_surcharge = apply_surcharge(base_tax, taxable_income, "old")
    surcharge = total_with_surcharge - base_tax
    cess = (base_tax + surcharge) * 0.04
    total_tax = base_tax + surcharge + cess

    return round(base_tax), round(surcharge), round(cess), round(total_tax)
