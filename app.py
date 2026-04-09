import streamlit as st

st.set_page_config(page_title="SaveTax", page_icon="💰")

# ---------------- UI ----------------
st.markdown("""
<style>
.main { background-color: #0E1117; }
.block-container { max-width: 700px; padding-top: 2rem; }

h1,h2,h3,p { color: #E6EDF3; }

.card {
    background-color: #161B22;
    padding: 20px;
    border-radius: 12px;
    margin-top: 15px;
}

.result {
    font-size: 30px;
    font-weight: 600;
    text-align: center;
    color: #4C9AFF;
}

.subtext { text-align:center; color: gray; }

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h2 style='text-align:center;'>💰 SaveTax</h2>
<p class='subtext'>Real Salary. No Confusion.</p>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio(
    "Menu",
    ["Salary Calculator", "Offer Comparison", "Tax Optimizer", "HRA Calculator"]
)

PROFESSIONAL_TAX = 2400

# ---------------- SURCHARGE ----------------
def apply_surcharge(tax, income, regime="old"):

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

    slabs = [
        (400000, 0),(400000, 0.05),(400000, 0.10),
        (400000, 0.15),(400000, 0.20),(400000, 0.25),
        (float('inf'), 0.30)
    ]

    tax = 0
    for limit, rate in slabs:
        if income > 0:
            taxable = min(income, limit)
            tax += taxable * rate
            income -= taxable

    tax = apply_surcharge(tax, original_income, "new")

    return tax * 1.04  # cess


def old_tax(income):
    original_income = income

    slabs = [
        (250000, 0),(250000, 0.05),
        (500000, 0.20),(float('inf'), 0.30)
    ]

    tax = 0
    for limit, rate in slabs:
        if income > 0:
            taxable = min(income, limit)
            tax += taxable * rate
            income -= taxable

    tax = apply_surcharge(tax, original_income, "old")

    return tax * 1.04  # cess


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


# ================= SALARY =================
if page == "Salary Calculator":

    ctc = st.number_input("Enter CTC (₹)", 0, step=50000)

    if ctc > 0:
        new, old = calculate(ctc)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<p class='subtext'>Monthly In-Hand</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='result'>₹{new/12:,.0f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(f"New Regime: ₹{new:,.0f}")
        st.write(f"Old Regime: ₹{old:,.0f}")

        diff = new - old
        if diff > 0:
            st.write(f"New regime gives ₹{diff:,.0f} more")
        else:
            st.write(f"Old regime gives ₹{abs(diff):,.0f} more")

        st.markdown("</div>", unsafe_allow_html=True)


# ================= OFFER =================
elif page == "Offer Comparison":

    ctc1 = st.number_input("Offer 1 (₹)", 0, step=50000)
    ctc2 = st.number_input("Offer 2 (₹)", 0, step=50000)

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


# ================= TAX =================
elif page == "Tax Optimizer":

    ctc = st.number_input("CTC (₹)", 0, step=50000)
    section_80c = st.number_input("80C (₹)", value=150000)
    hra = st.number_input("HRA Exemption (₹)", value=0)
    other = st.number_input("Other Deductions (₹)", value=0)

    if ctc > 0:
        new, old = calculate(ctc, section_80c, hra, other)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(f"New Regime: ₹{new:,.0f}")
        st.write(f"Old Regime: ₹{old:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)


# ================= HRA =================
elif page == "HRA Calculator":

    salary = st.number_input("Basic Salary (₹)", 0)
    hra_received = st.number_input("HRA Received (₹)", 0)
    rent = st.number_input("Monthly Rent (₹)", 0)
    is_metro = st.checkbox("Do you live in Metro City")
    st.caption("✔ Metro cities: Delhi, Mumbai, Chennai, Kolkata (as per current rules)")

    if salary > 0:
        rent_annual = rent * 12
        rent_minus_10 = rent_annual - (0.1 * salary)
        salary_limit = 0.5 * salary if is_metro else 0.4 * salary

        exempt = min(hra_received, rent_minus_10, salary_limit)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='result'>₹{exempt:,.0f}</div>", unsafe_allow_html=True)
        st.write("Exempt HRA")
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Show details"):
            st.write(f"HRA: ₹{hra_received:,.0f}")
            st.write(f"Rent - 10%: ₹{rent_minus_10:,.0f}")
            st.write(f"{'50%' if is_metro else '40%'} Salary: ₹{salary_limit:,.0f}")


# ---------------- FOOTER ----------------
st.caption("No data stored. Private & secure.")
