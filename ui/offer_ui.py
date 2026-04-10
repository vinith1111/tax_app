import streamlit as st
from services.salary_service import calculate_salary
from utils.formatter import format_inr

def render():

    ctc1 = st.number_input("Offer 1 CTC (₹)", 0, step=50000)
    ctc2 = st.number_input("Offer 2 CTC (₹)", 0, step=50000)

    if ctc1 >= 100000 and ctc2 >= 100000:

        result1 = calculate_salary(ctc1)
        result2 = calculate_salary(ctc2)

        new1 = result1["new_inhand"]
        new2 = result2["new_inhand"]

        col1, col2 = st.columns(2)
        col1.metric("Offer 1", format_inr(round(new1 / 12)))
        col2.metric("Offer 2", format_inr(round(new2 / 12)))

        diff = new2 - new1

        if diff > 0:
            st.success(f"Offer 2 better by {format_inr(round(diff / 12))}/month")
        else:
            st.success(f"Offer 1 better by {format_inr(round(abs(diff) / 12))}/month")
