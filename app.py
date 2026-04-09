import streamlit as st

st.set_page_config(page_title="SaveTaxX", page_icon="💰")

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


# ---------------- TAX BREAKDOWN ----------------
def tax_breakdown(income, regime):

    original_income = income
    tax = 0

    if regime == "new":
        slabs = [
            (400000, 0),(400000, 0.05),(400000, 0.10),
            (400000, 0.15),(400000, 0.20),(400000, 0.25),
            (float('inf'), 0.30)
        ]
    else:
        slabs = [
            (250000, 0),(250000, 0.05),
            (500000, 0.20),(float('inf'), 0.30)
        ]

    temp_income = income

    for limit, rate in slabs:
        if temp_income > 0:
            taxable = min(temp_income, limit)
            tax += taxable * rate
            temp_income -= taxable

    base_tax = tax

    # surcharge
    if original_income > 50000000:
        surcharge_rate = 0.25 if regime == "new" else 0.37
    elif original_income > 20000000:
        surcharge_rate = 0.25
    elif original_income > 10000000:
        surcharge_rate = 0.15
    elif original_income > 5000000:
        surcharge_rate = 0.10
    else:
        surcharge_rate = 0

    surcharge = base_tax * surcharge_rate

    # cess
    cess = (base_tax + surcharge) * 0.04

    total = base_tax + surcharge + cess

    return base_tax, surcharge, cess, total


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

    # NEW
    taxable_new = max(gross - 75000, 0)
    tax_new = new_tax(taxable_new)
    inhand_new = gross - employee_pf - tax_new - PROFESSIONAL_TAX

    # OLD
    deductions = 50000 + PROFESSIONAL_TAX + section_80c + hra + other
    taxable_old = max(gross - deductions, 0)
    tax_old = old_tax(taxable_old)
    inhand_old = gross - employee_pf - tax_old - PROFESSIONAL_TAX

    return inhand_new, inhand_old, taxable_new, taxable_old


# ================= SALARY =================
if page == "Salary Calculator":

    ctc = st.number_input("Enter CTC (₹)", 0, step=50000)

    if ctc > 0:
        new, old, _, _ = calculate(ctc)

        st.subheader("💸 Monthly In-Hand")
        st.success(f"₹{new/12:,.0f}")

        col1, col2 = st.columns(2)
        col1.metric("New Regime", f"₹{new:,.0f}")
        col2.metric("Old Regime", f"₹{old:,.0f}")

        if abs(new > old) < 1:
            st.info(f"Both regime gives same result")
        elif new > old:
            st.info(f"New regime better by ₹{new-old:,.0f}")
        else:
            st.info(f"Old regime better by ₹{old-new:,.0f}")


# ================= OFFER =================
elif page == "Offer Comparison":

    st.subheader("Compare Offers")

    ctc1 = st.number_input("Offer 1 CTC (₹)", 0, step=50000)
    ctc2 = st.number_input("Offer 2 CTC (₹)", 0, step=50000)

    if ctc1 > 0 and ctc2 > 0:
        new1, _, _, _ = calculate(ctc1)
        new2, _, _, _ = calculate(ctc2)

        col1, col2 = st.columns(2)
        col1.metric("Offer 1 Monthly", f"₹{new1/12:,.0f}")
        col2.metric("Offer 2 Monthly", f"₹{new2/12:,.0f}")

        diff = new2 - new1

        if diff > 0:
            st.success(f"Offer 2 gives ₹{diff/12:,.0f}/month more")
        else:
            st.success(f"Offer 1 gives ₹{abs(diff)/12:,.0f}/month more")


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

    if ctc > 0:

        new, old, taxable_new, taxable_old = calculate(ctc, section_80c, hra, other)

        st.subheader("📊 Tax Comparison")

        col1, col2 = st.columns(2)
        col1.metric("New Regime", f"₹{new:,.0f}")
        col2.metric("Old Regime", f"₹{old:,.0f}")

        diff = abs(new - old)

        if new > old:
            st.success(f"✅ New Regime better by ₹{diff:,.0f}")
        else:
            st.success(f"✅ Old Regime better by ₹{diff:,.0f}")

        with st.expander("🔍 View Detailed Breakdown"):

            st.markdown("### New Regime")
            b, s, c, t = tax_breakdown(taxable_new, "new")
            st.write(f"Base Tax: ₹{b:,.0f}")
            st.write(f"Surcharge: ₹{s:,.0f}")
            st.write(f"Cess: ₹{c:,.0f}")
            st.success(f"Total Tax: ₹{t:,.0f}")

            st.markdown("### Old Regime")
            b, s, c, t = tax_breakdown(taxable_old, "old")
            st.write(f"Base Tax: ₹{b:,.0f}")
            st.write(f"Surcharge: ₹{s:,.0f}")
            st.write(f"Cess: ₹{c:,.0f}")
            st.success(f"Total Tax: ₹{t:,.0f}")

        st.caption("Includes surcharge & cess as per latest rules")


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

        st.success(f"Exempt HRA: ₹{exempt:,.0f}")
        st.error(f"Taxable HRA: ₹{taxable:,.0f}")
