import streamlit as st
from services.salary_service import calculate_salary
from utils.formatter import format_inr
from validators.input_validator import validate_ctc

def render():

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

   with st.expander("📊 Salary Breakdown"):

    st.markdown("### 💼 Salary Structure")
    st.write(f"CTC: {format_inr(ctc)}")
    st.write(f"Basic: {format_inr(result['basic'])}")
    st.write(f"Employer PF: {format_inr(result['employer_pf'])}")
    st.write(f"Gross: {format_inr(result['gross'])}")

    st.markdown("### 🧾 Deductions")
    st.write(f"Employee PF: {format_inr(result['employee_pf'])}")
    st.write("Professional Tax: ₹2,400")

    # ---------- NEW REGIME ----------
    st.markdown("### 🏛 Tax (New Regime)")
    st.write(f"Base Tax: {format_inr(result['base_tax_new'])}")
    st.write(f"Surcharge: {format_inr(result['surcharge_new'])}")
    st.write(f"Cess (4%): {format_inr(result['cess_new'])}")
    st.success(f"Total Tax: {format_inr(result['tax_new'])}")

    if result['surcharge_new'] > 0:
        st.caption("⚠️ Surcharge applied based on high income slab")

    # ---------- OLD REGIME ----------
    st.markdown("### 🏛 Tax (Old Regime)")
    st.write(f"Base Tax: {format_inr(result['base_tax_old'])}")
    st.write(f"Surcharge: {format_inr(result['surcharge_old'])}")
    st.write(f"Cess (4%): {format_inr(result['cess_old'])}")
    st.success(f"Total Tax: {format_inr(result['tax_old'])}")

    if result['surcharge_old'] > 0:
        st.caption("⚠️ Surcharge applied (up to 37% above ₹5Cr)")

    # ---------- FINAL ----------
    st.markdown("### 💰 Final In-Hand")
    st.write(f"New Regime: {format_inr(result['new_inhand'])}")
    st.write(f"Old Regime: {format_inr(result['old_inhand'])}")
