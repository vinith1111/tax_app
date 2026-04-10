def format_inr(amount):
    amount = int(round(amount))
    if amount < 0:
        return "−" + format_inr(-amount)
    s = str(abs(amount))
    if len(s) <= 3:
        return "₹" + s
    result = s[-3:]
    s = s[:-3]
    while s:
        result = s[-2:] + "," + result
        s = s[:-2]
    return "₹" + result.lstrip(",")


def format_lpa(amount):
    lpa = round(amount / 100000, 2)
    return f"{lpa} LPA"


def effective_tax_rate(tax, gross):
    if gross <= 0:
        return 0.0
    return round((tax / gross) * 100, 1)
