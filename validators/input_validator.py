MIN_CTC = 120000


def validate_ctc(ctc):
    if ctc <= 0:
        return False, ""
    if ctc < MIN_CTC:
        return False, "CTC should be minimum ₹1,20,000"
    return True, ""


def validate_positive(value, label):
    if value < 0:
        return False, f"{label} cannot be negative"
    return True, ""
