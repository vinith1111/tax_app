def validate_ctc(ctc):
    if ctc < 100000:
        return False, "CTC should be minimum ₹1,20,000"
    return True, ""
