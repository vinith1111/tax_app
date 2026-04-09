import streamlit as st

st.set_page_config(page_title="SaveTaxX", page_icon="💰")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 80px;
}

.main {
    background-color: #0E1117;
}

h1,h2,h3 { color: #E6EDF3; }
label { color: #9DA5B4 !important; }

div[data-baseweb="input"] {
    background-color: #161B22 !important;
    border-radius: 10px !important;
}

.card {
    background-color: #161B22;
    padding: 20px;
    border-radius: 14px;
    margin-top: 15px;
}

.result {
    font-size: 34px;
    font-weight: 600;
    color: #4C9AFF;
    text-align: center;
}

.subtext {
    text-align: center;
    color: #9DA5B4;
    font-size: 14px;
}

.divider {
    border: 0.5px solid #2a2f36;
    margin: 15px 0;
}

.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: #0E1117;
    color: #6B7280;
    text-align: center;
    padding: 10px;
    font-size: 13px;
    border-top: 1px solid #2a2f36;
}

#MainMenu, header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h2 style='text-align:center;'>💰 SaveTaxX</h2>
<p class='subtext'>Real Salary. No Confusion.</p>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio(
    "📂 Menu",
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
    return tax * 1.04


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

    return inhand_new, inhand_old


# ================= SALARY =================
if page == "Salary Calculator":

    ctc = st.number_input("Enter CTC (₹)", 0, step=50000)

    if ctc > 0:
        new, old = calculate(ctc)

        st.markdown(f"""
        <div class="card">
            <div class="subtext">Monthly In-Hand</div>
            <div class="result">₹{new/12:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="card">
                <div class="subtext">New Regime</div>
                <div class="result">₹{new:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <div class="subtext">Old Regime</div>
                <div class="result">₹{old:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)


# ================= OFFER =================
elif page == "Offer Comparison":

    ctc1 = st.number_input("Offer 1 (₹)", 0, step=50000)
    ctc2 = st.number_input("Offer 2 (₹)", 0, step=50000)

    if ctc1 > 0 and ctc2 > 0:
        new1, _ = calculate(ctc1)
        new2, _ = calculate(ctc2)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="card">
                <div class="subtext">Offer 1</div>
                <div class="result">₹{new1/12:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <div class="subtext">Offer 2</div>
                <div class="result">₹{new2/12:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)


# ================= TAX OPTIMIZER =================
elif page == "Tax Optimizer":

    ctc = st.number_input("CTC (₹)", 0, step=50000)
    section_80c = st.number_input("80C Investment (₹)", value=150000)
    hra = st.number_input("HRA Exemption (₹)", value=0)
    other = st.number_input("Other Deductions (₹)", value=0)

    if ctc > 0:
        new, old = calculate(ctc, section_80c, hra, other)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="card">
                <div class="subtext">New Regime</div>
                <div class="result">₹{new:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <div class="subtext">Old Regime</div>
                <div class="result">₹{old:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)


# ================= HRA =================
elif page == "HRA Calculator":

    st.markdown("### 📍 Location")

    is_metro = st.checkbox("Do you live in a metro city?")
    st.caption("Metro cities: Delhi, Mumbai, Chennai, Kolkata")

    salary = st.number_input("Basic Salary (₹)", 0)
    hra_received = st.number_input("HRA Received (₹)", 0)
    rent = st.number_input("Monthly Rent (₹)", 0)

    st.caption("Enter monthly rent (example: 20000)")

    if salary > 0:

        rent_annual = rent * 12
        rent_minus_10 = max(rent_annual - (0.1 * salary), 0)
        salary_limit = 0.5 * salary if is_metro else 0.4 * salary

        exempt = min(hra_received, rent_minus_10, salary_limit)
        taxable_hra = max(hra_received - exempt, 0)

        st.markdown(f"""
        <div class="card" style="text-align:center;">

            <div class="result">₹{exempt:,.0f}</div>
            <div class="subtext">Exempt HRA</div>

            <div class="divider"></div>

            <div style="font-size:24px;">₹{taxable_hra:,.0f}</div>
            <div class="subtext">Taxable HRA</div>

        </div>
        """, unsafe_allow_html=True)

        with st.expander("Show calculation details"):
            st.markdown(f"**HRA Received:** ₹{hra_received:,.0f}")
            st.markdown(f"**Rent - 10% Salary:** ₹{rent_minus_10:,.0f}")
            st.markdown(f"**{'50%' if is_metro else '40%'} Salary:** ₹{salary_limit:,.0f}")


# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
🔒 No data stored • Private & secure • SaveTaxX
</div>
""", unsafe_allow_html=True)
