import streamlit as st
from services.salary_service import calculate_salary
from utils.formatter import format_inr

def render():

    col1, col2 = st.columns(2)

    with col1:
        ctc = st.number_input("CTC (₹)", 0, step=50000)
        section_80c = st.number_input("80C", value=150000)

    with col2:
        hra = st.number_input("HRA", value=0)
        other = st.number_input("Other deductions", value=0)

    if ctc >= 100000:

        result = calculate_salary(ctc, section_80c, hra, other)

        new = result["new_inhand"]
        old = result["old_inhand"]

        col1, col2 = st.columns(2)
        col1.metric("New Regime", format_inr(new))
        col2.metric("Old Regime", format_inr(old))

        diff = abs(new - old)

        if new > old:
            st.success(f"New better by {format_inr(diff)}")
        else:
            st.success(f"Old better by {format_inr(diff)}")
