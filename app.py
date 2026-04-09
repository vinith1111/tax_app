import streamlit as st

st.set_page_config(page_title="SaveTaxX", page_icon="💰")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.block-container {
    max-width: 850px;
    padding-bottom: 80px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("💰 SaveTaxX")
st.caption("Real Salary. No Confusion.")

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio(
    "📂 Menu",
    ["Salary Calculator", "Offer Comparison", "Tax Optimizer", "HRA Calculator"]
)

PROFESSIONAL_TAX = 2400

# ---------------- TAX ----------------
def new_tax(income):
    if income <= 1200000:
        return 0

    tax = 0
    slabs = [
        (400000, 0),
        (400000, 0.05),
        (400000, 0.10),
        (400000, 0.15),
        (400000, 0.20),
        (400000, 0.25),
        (float('inf'), 0.30)
    ]

    for limit, rate in slabs:
        if income > 0:
            taxable = min(income, limit)
            tax += taxable * rate
            income -= taxable

    return tax * 1.04


def old_tax(income):
    tax = 0
    slabs = [
        (250000, 0),
        (250000, 0.05),
        (500000, 0.20),
        (float('inf'), 0.30)
    ]

    for limit, rate in slabs:
        if income > 0:
            taxable = min(income, limit)
            tax += taxable * rate
            income -= taxable

    return tax * 1.04


# ---------------- CALC ----------------
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

    return inhand_new, inhand_old


# ================= SALARY =================
if page == "Salary Calculator":

    ctc = st.number_input("Enter CTC (₹)", 0, step=50000)

    if ctc > 0:
        new, old = calculate(ctc)

        st.subheader("💸 Monthly In-Hand")
        st.success(f"₹{new/12:,.0f}")

        col1, col2 = st.columns(2)

        col1.metric("New Regime", f"₹{new:,.0f}")
        col2.metric("Old Regime", f"₹{old:,.0f}")

        if new > old:
            st.info(f"New regime better by ₹{new-old:,.0f}")
        else:
            st.info(f"Old regime better by ₹{old-new:,.0f}")


# ================= OFFER =================
elif page == "Offer Comparison":

    st.subheader("Compare Offers")

    ctc1 = st.number_input("Offer 1 CTC (₹)", 0, step=50000)
    ctc2 = st.number_input("Offer 2 CTC (₹)", 0, step=50000)

    if ctc1 > 0 and ctc2 > 0:
        new1, _ = calculate(ctc1)
        new2, _ = calculate(ctc2)

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

    st.subheader("Optimize Your Tax")

    ctc = st.number_input("CTC (₹)", 0, step=50000)
    section_80c = st.number_input("80C (₹)", value=150000)
    hra = st.number_input("HRA Exemption (₹)", value=0)
    other = st.number_input("Other Deductions (₹)", value=0)

    if ctc > 0:
        new, old = calculate(ctc, section_80c, hra, other)

        col1, col2 = st.columns(2)

        col1.metric("New Regime", f"₹{new:,.0f}")
        col2.metric("Old Regime", f"₹{old:,.0f}")

        if old < new:
            st.success("Use Old Regime to save tax")
        else:
            st.success("Use New Regime (simpler)")


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

        with st.expander("Details"):
            st.write("HRA Received:", hra_received)
            st.write("Rent - 10% Salary:", rent_minus_10)
            st.write("Salary Limit:", salary_limit)


# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("🔒 No data stored • SaveTaxX")
