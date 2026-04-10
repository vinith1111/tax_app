def apply_surcharge(tax, income, regime):
    if income > 50000000:
        surcharge = 0.25 if regime == "new" else 0.37
    elif income > 20000000:
        surcharge = 0.25
    elif income > 10000000:
        surcharge = 0.15
    elif income > 5000000:
        surcharge = 0.10
    else:
        surcharge = 0

    return tax * (1 + surcharge)


def new_tax(income):
    if income <= 1200000:
        return 0

    tax = 0
    original_income = income

    slabs = [
        (400000, 0),(400000, 0.05),(400000, 0.10),
        (400000, 0.15),(400000, 0.20),(400000, 0.25),
        (float('inf'), 0.30)
    ]

    for limit, rate in slabs:
        if income > 0:
            taxable = min(income, limit)
            tax += taxable * rate
            income -= taxable

    tax = apply_surcharge(tax, original_income, "new")
    return tax * 1.04


def old_tax(income):
    tax = 0
    original_income = income

    slabs = [
        (250000, 0),(250000, 0.05),
        (500000, 0.20),(float('inf'), 0.30)
    ]

    for limit, rate in slabs:
        if income > 0:
            taxable = min(income, limit)
            tax += taxable * rate
            income -= taxable

    tax = apply_surcharge(tax, original_income, "old")
    return tax * 1.04
