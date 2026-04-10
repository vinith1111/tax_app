import streamlit as st

st.set_page_config(page_title="SaveTaxX", page_icon="💰")

# ---------------- INR FORMAT ----------------
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


# ---------------- HEADER ----------------
st.title("💰 SaveTaxX")
st.caption("Real Salary. No Confusion.")

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio(
    "📂 Menu",
    ["Salary Calculator", "Offer Comparison", "Tax Optimizer", "HRA Calculator"]
)

PROFESSIONAL_TAX = 2400


# ---------------- SURCHARGE ----------------
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


# ---------------- TAX FUNCTIONS ----------------
def new_tax(income):
    if income <= 1200000:
        return 0

    original_income = income
    tax = 0

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
    original_income = income
    tax = 0

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


# ---------------- CALCULATION ----------------
def calculate(ctc, section_80c=150000, hra=0, other=0):

    basic = ctc * 0.5
    employer_pf = basic * 0.12
    employee_pf = basic * 0.12

    gross = ctc - employer_pf

    taxable_new = max(gross - 75000, 0)
    tax_new = new_tax(taxable_new)
    inhand_new = gross - employee_pf - tax_new - PROFESSIONAL_TAX

    deductions = 50000 + PROFESSIONAL_TAX + section_80c + hra + other
    taxable_old = max(gross - deductions, 0)
    tax_old = old_tax(taxable_old)
    inhand_old = gross - employee_pf - tax_old - PROFESSIONAL_TAX

    # ✅ FIX: ROUND AT SOURCE (prevents ₹1 mismatch)
    return round(inhand_new), round(inhand_old), round(taxable_new), round(taxable_old)


# ================= SALARY =================
if page == "Salary Calculator":

    ctc = st.number_input("Enter CTC (₹)", 0, step=50000)

    if ctc > 0 and ctc < 100000:
        st.error("CTC should be minimum ₹1,00,000")

    elif ctc >= 100000:

        new, old, _, _ = calculate(ctc)

        st.subheader("💸 Monthly In-Hand")
        st.success(format_inr(round(new / 12)))

        col1, col2 = st.columns(2)
        col1.metric("New Regime", format_inr(new))
        col2.metric("Old Regime", format_inr(old))

        if new == old:
            st.info("⚖️ Both regimes give same result")
        elif new > old:
            st.info(f"New regime better by {format_inr(new - old)}")
        else:
            st.info(f"Old regime better by {format_inr(old - new)}")


# ================= OFFER =================
elif page == "Offer Comparison":

    st.subheader("Compare Offers")

    ctc1 = st.number_input("Offer 1 CTC (₹)", 0, step=50000)
    ctc2 = st.number_input("Offer 2 CTC (₹)", 0, step=50000)

    if (ctc1 > 0 and ctc1 < 100000) or (ctc2 > 0 and ctc2 < 100000):
        st.error("CTC should be minimum ₹1,00,000")

    elif ctc1 >= 100000 and ctc2 >= 100000:

        new1, _, _, _ = calculate(ctc1)
        new2, _, _, _ = calculate(ctc2)

        col1, col2 = st.columns(2)
        col1.metric("Offer 1 Monthly", format_inr(round(new1 / 12)))
        col2.metric("Offer 2 Monthly", format_inr(round(new2 / 12)))

        diff = new2 - new1

        if diff > 0:
            st.success(f"Offer 2 gives {format_inr(round(diff / 12))}/month more")
        else:
            st.success(f"Offer 1 gives {format_inr(round(abs(diff) / 12))}/month more")


# ================= TAX OPTIMIZER =================
elif page == "Tax Optimizer":

    st.header("🧮 Tax Optimizer")

    col1, col2 = st.columns(2)

    with col1:
        ctc = st.number_input("CTC (₹)", 0, step=50000)
        section_80c = st.number_input("80C (₹)", value=150000)

    with col2:
        hra = st.number_input("HRA Exemption (₹)", value=0)
        other = st.number_input("Other Deductions (₹)", value=0)

    if ctc > 0 and ctc < 100000:
        st.error("CTC should be minimum ₹1,00,000")

    elif ctc >= 100000:

        new, old, _, _ = calculate(ctc, section_80c, hra, other)

        col1, col2 = st.columns(2)
        col1.metric("New Regime", format_inr(new))
        col2.metric("Old Regime", format_inr(old))

        diff = abs(new - old)

        if new > old:
            st.success(f"New Regime better by {format_inr(diff)}")
        else:
            st.success(f"Old Regime better by {format_inr(diff)}")


# ================= HRA =================
elif page == "HRA Calculator":

    st.subheader("HRA Calculator")

    is_metro = st.checkbox("Metro city (Delhi, Mumbai, Chennai, Kolkata)")

    salary = st.number_input("Basic Salary (₹)", 0)
    hra_received = st.number_input("HRA Received (₹)", 0)
    rent = st.number_input("Monthly Rent (₹)", 0)

    if salary > 0:

        rent_annual = rent * 12
        rent_minus_10 = max(rent_annual - (0.1 * salary), 0)
        salary_limit = 0.5 * salary if is_metro else 0.4 * salary

        exempt = min(hra_received, rent_minus_10, salary_limit)
        taxable = max(hra_received - exempt, 0)

        st.success(f"Exempt HRA: {format_inr(exempt)}")
        st.error(f"Taxable HRA: {format_inr(taxable)}")


# ---------------- FOOTER ----------------
st.markdown("""
<hr style="border:0.5px solid #2a2f36; margin-top:30px;">

<div style='text-align:center; color:#9DA5B4; font-size:13px;'>
🔒 No data stored. Private & secure.<br>
💰 SaveTaxX — Real Salary. No Confusion.
</div>
""", unsafe_allow_html=True)
