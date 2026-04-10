import streamlit as st
from services.hra_service import calculate_hra
from utils.formatter import format_inr

def render():

    is_metro = st.checkbox("Metro city")

    salary = st.number_input("Basic Salary (₹)", 0)
    hra_received = st.number_input("HRA Received (₹)", 0)
    rent = st.number_input("Monthly Rent (₹)", 0)

    if salary > 0:

        result = calculate_hra(salary, hra_received, rent, is_metro)

        st.success(f"Exempt HRA: {format_inr(result['exempt'])}")
        st.error(f"Taxable HRA: {format_inr(result['taxable'])}")
