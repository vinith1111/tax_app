import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="SaveTax", page_icon="💰")

# ---------------- PREMIUM UI STYLE ----------------
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}

.block-container {
    max-width: 700px;
    padding-top: 2rem;
}

/* Text */
h1, h2, h3, p {
    color: #E6EDF3;
}

/* Card */
.card {
    background-color: #161B22;
    padding: 20px;
    border-radius: 12px;
    margin-top: 15px;
}

/* Result highlight */
.result {
    font-size: 32px;
    font-weight: 600;
    text-align: center;
    color: #4C9AFF;
}

/* Sub text */
.subtext {
    text-align: center;
    color: gray;
}

/* Hide Streamlit header */
#MainMenu, footer, header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h2 style='text-align:center;'>💰 SaveTax</h2>
<p class='subtext'>Real Salary. No Confusion.</p>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("Menu")
page = st.sidebar.radio("", ["Salary Calculator", "Offer Comparison"])

# ---------------- CONSTANTS ----------------
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

# ---------------- CALCULATION ----------------
def calculate(ctc, section_80c=150000, hra=0, other=0):
    basic = ctc * 0.5

    employer_pf = basic * 0.12
    employee_pf = basic * 0.12

    gross = ctc - employer_pf

    # NEW REGIME
    taxable_new = max(gross - 75000, 0)
    tax_new = new_tax(taxable_new)
    inhand_new = gross - employee_pf - tax_new - PROFESSIONAL_TAX

    # OLD REGIME
    deductions = 50000 + PROFESSIONAL_TAX + section_80c + hra + other
    taxable_old = max(gross - deductions, 0)
    tax_old = old_tax(taxable_old)
    inhand_old = gross - employee_pf - tax_old - PROFESSIONAL_TAX

    return inhand_new, inhand_old

# ================= SALARY CALCULATOR =================
if page == "Salary Calculator":

    ctc = st.number_input("Enter your CTC (₹)", min_value=0, step=50000)

    st.markdown("### Optional (Old Regime)")
    section_80c = st.number_input("80C (₹)", value=150000)
    hra = st.number_input("HRA (₹)", value=0)
    other = st.number_input("Other deductions (₹)", value=0)

    if ctc > 0:
        new, old = calculate(ctc, section_80c, hra, other)

        # RESULT CARD
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<p class='subtext'>Monthly In-Hand</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='result'>₹{new/12:,.0f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # COMPARISON
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.write(f"New Regime: ₹{new:,.0f}")
        st.write(f"Old Regime: ₹{old:,.0f}")

        diff = new - old

        if diff > 0:
            st.write(f"New regime gives ₹{diff:,.0f} more")
        else:
            st.write(f"Old regime gives ₹{abs(diff):,.0f} more")

        st.markdown("</div>", unsafe_allow_html=True)

# ================= OFFER COMPARISON =================
elif page == "Offer Comparison":

    ctc1 = st.number_input("Offer 1 (₹)", min_value=0, step=50000)
    ctc2 = st.number_input("Offer 2 (₹)", min_value=0, step=50000)

    if ctc1 > 0 and ctc2 > 0:
        new1, _ = calculate(ctc1)
        new2, _ = calculate(ctc2)

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.write(f"Offer 1 Monthly: ₹{new1/12:,.0f}")
        st.write(f"Offer 2 Monthly: ₹{new2/12:,.0f}")

        diff = (new2 - new1) / 12

        if diff > 0:
            st.write(f"Offer 2 gives ₹{diff:,.0f}/month more")
        else:
            st.write(f"Offer 1 gives ₹{abs(diff):,.0f}/month more")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.caption("No data stored. Private & secure.")
