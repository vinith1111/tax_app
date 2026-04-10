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
            st.write(f"CTC: {format_inr(ctc)}")
            st.write(f"Basic: {format_inr(result['basic'])}")
            st.write(f"Employer PF: {format_inr(result['employer_pf'])}")
            st.write(f"Gross: {format_inr(result['gross'])}")
            st.write(f"Employee PF: {format_inr(result['employee_pf'])}")
            st.write(f"Tax (New): {format_inr(result['tax_new'])}")
            st.write(f"Tax (Old): {format_inr(result['tax_old'])}")
