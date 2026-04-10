import streamlit as st
from services.salary_service import calculate_salary
from utils.formatter import format_inr


def render():

    st.subheader("Compare Offers")

    # -------- INPUT --------
    ctc1 = st.number_input("Offer 1 CTC (₹)", 0, step=50000)
    ctc2 = st.number_input("Offer 2 CTC (₹)", 0, step=50000)

    # -------- VALIDATION --------
    if (0 < ctc1 < 100000) or (0 < ctc2 < 100000):
        st.error("CTC should be minimum ₹1,00,000")
        return

    if ctc1 >= 100000 and ctc2 >= 100000:

        # -------- CALCULATION --------
        result1 = calculate_salary(ctc1)
        result2 = calculate_salary(ctc2)

        new1 = result1["new_inhand"]
        new2 = result2["new_inhand"]

        # -------- MAIN METRICS --------
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Offer 1",
                format_inr(round(new1 / 12)),
                f"{format_inr(new1)} yearly"
            )

        with col2:
            st.metric(
                "Offer 2",
                format_inr(round(new2 / 12)),
                f"{format_inr(new2)} yearly"
            )

        # -------- DIFFERENCE --------
        diff = new2 - new1

        if diff > 0:
            st.success(f"Offer 2 gives {format_inr(round(diff / 12))}/month more")
        else:
            st.success(f"Offer 1 gives {format_inr(round(abs(diff) / 12))}/month more")

        # -------- TAX INSIGHT --------
        st.markdown("### 🧠 Tax Insight")

        tax1 = result1["tax_new"]
        tax2 = result2["tax_new"]

        if tax1 == 0 and tax2 == 0:
            st.info("✅ Both offers fall under ₹12L taxable limit — no tax applied")

        elif tax1 == 0 and tax2 > 0:
            st.warning("⚠️ Offer 2 crosses ₹12L taxable limit — tax starts applying")

        else:
            st.info("ℹ️ Both offers are taxable — higher CTC → higher tax impact")

        # Small excess insight
        excess2 = result2.get("excess_income", 0)

        if 0 < excess2 < 100000:
            st.caption(
                f"💡 Offer 2 exceeds ₹12L by only {format_inr(excess2)} — tax impact is small"
            )

        # -------- DIFFERENCE BREAKDOWN --------
        st.markdown("### 📊 Difference Breakdown")

        pf_diff = result2["employee_pf"] - result1["employee_pf"]
        tax_diff = result2["tax_new"] - result1["tax_new"]
        gross_diff = ctc2 - ctc1

        st.write(f"💰 CTC Increase: {format_inr(gross_diff)}")
        st.write(f"📉 PF Increase: {format_inr(pf_diff)}")
        st.write(f"🏛 Tax Increase: {format_inr(tax_diff)}")
        st.success(f"💵 Net Gain: {format_inr(diff)}")

        # -------- DETAILED BREAKDOWN --------
        with st.expander("📊 View Detailed Breakdown"):

            st.markdown("### Offer 1")
            st.write(f"CTC: {format_inr(ctc1)}")
            st.write(f"Gross: {format_inr(result1['gross'])}")
            st.write(f"Tax: {format_inr(result1['tax_new'])}")
            st.write(f"In-hand: {format_inr(result1['new_inhand'])}")

            st.markdown("### Offer 2")
            st.write(f"CTC: {format_inr(ctc2)}")
            st.write(f"Gross: {format_inr(result2['gross'])}")
            st.write(f"Tax: {format_inr(result2['tax_new'])}")
            st.write(f"In-hand: {format_inr(result2['new_inhand'])}")
