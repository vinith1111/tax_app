def format_inr(amount):
    s = str(int(amount))
    if len(s) <= 3:
        return "₹" + s

    last3 = s[-3:]
    rest = s[:-3]

    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]

    if rest:
        parts.insert(0, rest)

    return "₹" + ",".join(parts + [last3])
