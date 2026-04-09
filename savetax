import streamlit as st

st.set_page_config(page_title="Salary Insights", page_icon="💰")

st.title("💰 Salary Insights App")
st.caption("Know your real in-hand, compare offers, and understand your money")

# ---------------- INPUT ----------------
ctc = st.number_input("Enter your CTC (₹)", min_value=0, step=50000)

st.subheader("💡 Your Inputs")

rent = st.number_input("Monthly Rent (₹)", value=0)
section_80c = st.number_input("80C Investment (₹)", value=150000)
hra = st.number_input("HRA Exemption (₹)", value=0)
other = st.number_input("Other Deductions (₹)", value=0)

# ---------------- CONSTANTS ----------------
STANDARD_DEDUCTION = 75000
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

# ---------------- CORE FUNCTION ----------------
def calculate(ctc):
    basic = ctc * 0.5
    employer_pf = basic * 0.12
    employee_pf = basic * 0.12

    gross = ctc - employer_pf

    # NEW
    taxable_new = max(gross - STANDARD_DEDUCTION, 0)
    tax_new = new_tax(taxable_new)
    inhand_new = gross - employee_pf - tax_new - PROFESSIONAL_TAX

    # OLD
    deductions = STANDARD_DEDUCTION + PROFESSIONAL_TAX + section_80c + hra + other
    taxable_old = max(gross - deductions, 0)
    tax_old = old_tax(taxable_old)
    inhand_old = gross - employee_pf - tax_old - PROFESSIONAL_TAX

    return {
        "new": inhand_new,
        "old": inhand_old,
        "tax_new": tax_new,
        "tax_old": tax_old,
        "pf": employer_pf + employee_pf
    }

# ---------------- MAIN ----------------
if ctc > 0:
    result = calculate(ctc)

    # ===================== RESULT =====================
    st.subheader("📊 Your In-Hand Salary")

    col1, col2 = st.columns(2)
    col1.metric("New Regime", f"₹{result['new']:,.0f}")
    col2.metric("Old Regime", f"₹{result['old']:,.0f}")

    st.write(f"Monthly (New): ₹{result['new']/12:,.0f}")
    st.write(f"Monthly (Old): ₹{result['old']/12:,.0f}")

    # ===================== BEST =====================
    st.subheader("💡 Best Choice")

    if result['new'] > result['old']:
        st.success("New regime gives higher in-hand")
    else:
        st.success("Old regime gives higher in-hand")

    # ===================== SALARY STORY =====================
    st.subheader("📦 Your Salary Reality")

    monthly_new = result['new'] / 12
    savings = monthly_new - rent

    st.write(f"""
    💰 You earn: ₹{ctc:,.0f}

    👉 You actually get: ₹{monthly_new:,.0f} per month

    💸 Expenses (rent): ₹{rent:,.0f}

    💵 Estimated savings: ₹{savings:,.0f}
    """)

    # ===================== WHERE MONEY GOES =====================
    st.subheader("📉 Where your money goes")

    st.write(f"Tax: ₹{result['tax_new']:,.0f}")
    st.write(f"PF (Total): ₹{result['pf']:,.0f}")
    st.write(f"Professional Tax: ₹{PROFESSIONAL_TAX}")

    # ===================== ADVICE =====================
    st.subheader("💡 Simple Advice")

    if result['old'] > result['new']:
        remaining = max(150000 - section_80c, 0)

        if remaining > 0:
            st.write(f"• Invest ₹{remaining:,.0f} more under 80C")

        if hra == 0:
            st.write("• Claim HRA if you pay rent")

        if other == 0:
            st.write("• Add insurance/donations to reduce tax")

    else:
        st.write("• New regime is simpler and good for you")

    # ===================== OFFER COMPARISON =====================
    st.subheader("🏢 Compare Another Offer")

    ctc2 = st.number_input("Enter second offer (₹)", min_value=0, step=50000)

    if ctc2 > 0:
        result2 = calculate(ctc2)

        st.write("### Comparison")

        col1, col2 = st.columns(2)
        col1.metric("Offer 1 (You)", f"₹{result['new']/12:,.0f}/month")
        col2.metric("Offer 2", f"₹{result2['new']/12:,.0f}/month")

        diff = (result2['new'] - result['new']) / 12

        if diff > 0:
            st.success(f"Offer 2 gives ₹{diff:,.0f}/month more")
        else:
            st.success(f"Offer 1 gives ₹{abs(diff):,.0f}/month more")

else:
    st.info("Enter your CTC to begin 🚀")
