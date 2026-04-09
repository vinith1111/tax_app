import streamlit as st

st.set_page_config(page_title="SaveTax", page_icon="💰")

# ---------------- SIDEBAR ----------------
st.sidebar.title("📂 Menu")

page = st.sidebar.radio(
    "Go to",
    ["📊 Salary Calculator", "🏢 Offer Comparison", "💡 Tax Optimizer", "🏠 HRA Calculator"]
)

# ---------------- CONSTANTS ----------------
STANDARD_DEDUCTION_NEW = 75000
STANDARD_DEDUCTION_OLD = 50000
PROFESSIONAL_TAX = 2400

# ---------------- TAX FUNCTIONS ----------------
def new_tax(income):
    if income <= 1200000:
        return 0

    slabs = [
        (400000, 0),
        (400000, 0.05),
        (400000, 0.10),
        (400000, 0.15),
        (400000, 0.20),
        (400000, 0.25),
        (float('inf'), 0.30)
    ]

    tax = 0
    for limit, rate in slabs:
        if income > 0:
            taxable = min(income, limit)
            tax += taxable * rate
            income -= taxable

    return tax * 1.04


def old_tax(income):
    slabs = [
        (250000, 0),
        (250000, 0.05),
        (500000, 0.20),
        (float('inf'), 0.30)
    ]

    tax = 0
    for limit, rate in slabs:
        if income > 0:
            taxable = min(income, limit)
            tax += taxable * rate
            income -= taxable

    return tax * 1.04


# ---------------- SALARY CALCULATION ----------------
def calculate(ctc, section_80c=150000, hra=0, other=0):
    basic = ctc * 0.5
    employer_pf = basic * 0.12
    employee_pf = basic * 0.12

    gross = ctc - employer_pf

    # NEW REGIME
    taxable_new = max(gross - STANDARD_DEDUCTION_NEW, 0)
    tax_new = new_tax(taxable_new)
    inhand_new = gross - employee_pf - tax_new - PROFESSIONAL_TAX

    # OLD REGIME
    deductions_old = (
        STANDARD_DEDUCTION_OLD +
        PROFESSIONAL_TAX +
        section_80c +
        hra +
        other
    )

    taxable_old = max(gross - deductions_old, 0)
    tax_old = old_tax(taxable_old)
    inhand_old = gross - employee_pf - tax_old - PROFESSIONAL_TAX

    return inhand_new, inhand_old


# ================= PAGE 1 =================
if page == "📊 Salary Calculator":
    st.title("💰 SaveTax – Salary Calculator")

    ctc = st.number_input("Enter your CTC (₹)", min_value=0, step=50000)

    if ctc > 0:
        new, old = calculate(ctc)

        col1, col2 = st.columns(2)
        col1.metric("New Regime", f"₹{new:,.0f}")
        col2.metric("Old Regime", f"₹{old:,.0f}")

        st.write(f"Monthly (New): ₹{new/12:,.0f}")
        st.write(f"Monthly (Old): ₹{old/12:,.0f}")

        diff = new - old
        if diff > 0:
            st.success(f"You get ₹{diff:,.0f} more with New Regime")
        else:
            st.success(f"You get ₹{abs(diff):,.0f} more with Old Regime")

        st.caption("✔ Includes tax, PF, and deductions")


# ================= PAGE 2 =================
elif page == "🏢 Offer Comparison":
    st.title("🏢 Offer Comparison")

    ctc1 = st.number_input("Offer 1 CTC (₹)", min_value=0, step=50000)
    ctc2 = st.number_input("Offer 2 CTC (₹)", min_value=0, step=50000)

    if ctc1 > 0 and ctc2 > 0:
        new1, _ = calculate(ctc1)
        new2, _ = calculate(ctc2)

        col1, col2 = st.columns(2)
        col1.metric("Offer 1 (Monthly)", f"₹{new1/12:,.0f}")
        col2.metric("Offer 2 (Monthly)", f"₹{new2/12:,.0f}")

        diff = (new2 - new1) / 12

        if diff > 0:
            st.success(f"Offer 2 gives ₹{diff:,.0f}/month more")
        else:
            st.success(f"Offer 1 gives ₹{abs(diff):,.0f}/month more")


# ================= PAGE 3 =================
elif page == "💡 Tax Optimizer":
    st.title("💡 Tax Optimizer")

    ctc = st.number_input("Enter your CTC (₹)", min_value=0, step=50000)
    section_80c = st.number_input("80C Investment (₹)", value=150000)
    hra = st.number_input("HRA (₹)", value=0)
    other = st.number_input("Other Deductions (₹)", value=0)

    if ctc > 0:
        new, old = calculate(ctc, section_80c, hra, other)

        st.write(f"New Regime: ₹{new:,.0f}")
        st.write(f"Old Regime: ₹{old:,.0f}")

        if old > new:
            st.success("Old Regime gives better in-hand")
        else:
            st.info("New Regime is better and simpler")


# ================= PAGE 4 =================
elif page == "🏠 HRA Calculator":
    st.title("🏠 HRA Calculator")

    salary = st.number_input("Basic Salary (₹)", min_value=0)
    hra_received = st.number_input("HRA Received (₹)", min_value=0)
    rent_paid = st.number_input("Rent Paid (₹)", min_value=0)

    metro = st.checkbox(" Do you live in Metro City?")
    st.caption("✔ Metro cities: Delhi, Mumbai, Chennai, Kolkata (as per current rules)")

    if salary > 0 and hra_received > 0 and rent_paid > 0:

        percent_salary = 0.5 if metro else 0.4

        exemption1 = hra_received
        exemption2 = rent_paid - (0.1 * salary)
        exemption3 = percent_salary * salary

        hra_exempt = min(exemption1, exemption2, exemption3)
        hra_exempt = max(hra_exempt, 0)

        st.subheader("📊 HRA Breakdown")

        st.write(f"HRA Received: ₹{exemption1:,.0f}")
        st.write(f"Rent - 10% Salary: ₹{exemption2:,.0f}")
        st.write(f"{'50%' if metro else '40%'} of Salary: ₹{exemption3:,.0f}")

        st.subheader("✅ Result")

        st.success(f"Exempt HRA: ₹{hra_exempt:,.0f}")
        st.write(f"Taxable HRA: ₹{hra_received - hra_exempt:,.0f}")

    else:
        st.info("Enter salary, HRA, and rent to calculate")
