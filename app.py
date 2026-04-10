import streamlit as st

from services.salary_service import calculate_salary
from services.hra_service import calculate_hra
from utils.formatter import format_inr
from validators.input_validator import validate_ctc

st.set_page_config(page_title="SaveTaxX", page_icon="💰")

# ---------------- HEADER ----------------
st.title("💰 SaveTaxX")
st.caption("Real Salary. No Confusion.")

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio(
    "📂 Menu",
    ["Salary Calculator", "Offer Comparison", "Tax Optimizer", "HRA Calculator"]
)

# ================= SALARY =================
if page == "Salary Calculator":

    ctc = st.number_input("Enter CTC (₹)", 0, step=50000)

    valid, msg = validate_ctc(ctc)

    if ctc > 0 and not valid:
        st.error(msg)

    elif valid and ctc > 0:

        result = calculate_salary(ctc)

        new = result["new_inhand"]
        old = result["old_inhand"]

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

        # ----------- BREAKDOWN -----------
        with st.expander("📊 View Salary Breakdown"):

            st.markdown("### 💼 Salary Structure")
            st.write(f"CTC: {format_inr(ctc)}")
            st.write(f"Basic Salary (50%): {format_inr(result['basic'])}")
            st.write(f"Employer PF (12%): {format_inr(result['employer_pf'])}")
            st.write(f"Gross Salary: {format_inr(result['gross'])}")

            st.markdown("### 🧾 Deductions")
            st.write(f"Employee PF (12%): {format_inr(result['employee_pf'])}")
            st.write("Professional Tax: ₹2,400")

            st.markdown("### 🏛 Tax")
            st.write(f"Tax (New Regime): {format_inr(result['tax_new'])}")
            st.write(f"Tax (Old Regime): {format_inr(result['tax_old'])}")

            st.markdown("### 💰 Final")
            st.write(f"New In-hand: {format_inr(new)}")
            st.write(f"Old In-hand: {format_inr(old)}")


# ================= OFFER =================
elif page == "Offer Comparison":

    st.subheader("Compare Offers")

    ctc1 = st.number_input("Offer 1 CTC (₹)", 0, step=50000)
    ctc2 = st.number_input("Offer 2 CTC (₹)", 0, step=50000)

    if (ctc1 > 0 and ctc1 < 100000) or (ctc2 > 0 and ctc2 < 100000):
        st.error("CTC should be minimum ₹1,00,000")

    elif ctc1 >= 100000 and ctc2 >= 100000:

        new1, _ = calculate_salary(ctc1)
        new2, _ = calculate_salary(ctc2)

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

        result = calculate_salary(ctc, section_80c, hra, other)

        new = result["new_inhand"]
        old = result["old_inhand"]

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

        exempt, taxable = calculate_hra(salary, hra_received, rent, is_metro)

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
