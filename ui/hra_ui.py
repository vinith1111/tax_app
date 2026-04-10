import streamlit as st
from services.hra_service import calculate_hra
from utils.formatter import format_inr

def render():

    st.subheader("HRA Calculator")

    is_metro = st.checkbox("Metro city (Delhi, Mumbai, Chennai, Kolkata)")

    salary = st.number_input("Basic Salary (₹)", 0)
    hra_received = st.number_input("HRA Received (₹)", 0)
    rent = st.number_input("Monthly Rent (₹)", 0)

    if salary > 0:

        result = calculate_hra(salary, hra_received, rent, is_metro)

        st.success(f"Exempt HRA: {format_inr(result['exempt'])}")
        st.error(f"Taxable HRA: {format_inr(result['taxable'])}")

        with st.expander("📊 View HRA Breakdown"):

            st.markdown("### 📥 Inputs")
            st.write(f"Basic Salary: {format_inr(result['salary'])}")
            st.write(f"HRA Received: {format_inr(result['hra_received'])}")
            st.write(f"Annual Rent: {format_inr(result['rent_annual'])}")

            st.markdown("### 🧮 Calculation Rules")

            st.write(f"1️⃣ Actual HRA: {format_inr(result['hra_received'])}")
            st.write(f"2️⃣ Rent - 10% Salary: {format_inr(result['rent_minus_10'])}")

            if is_metro:
                st.write(f"3️⃣ 50% of Salary (Metro): {format_inr(result['salary_limit'])}")
            else:
                st.write(f"3️⃣ 40% of Salary (Non-Metro): {format_inr(result['salary_limit'])}")

            st.markdown("### 🏆 Final Result")

            st.success(f"Exempt HRA: {format_inr(result['exempt'])}")
            st.error(f"Taxable HRA: {format_inr(result['taxable'])}")

            st.caption("HRA exemption = Minimum of (HRA, Rent-10% salary, 40%/50% salary)")
