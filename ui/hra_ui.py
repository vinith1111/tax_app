import streamlit as st
from services.hra_service import calculate_hra
from utils.formatter import format_inr


def render():
    st.markdown("### 🏠 HRA Calculator")
    st.caption("Find how much of your HRA is tax-exempt based on your rent and salary.")

    period = st.radio(
        "Input Period",
        options=["Monthly", "Yearly"],
        horizontal=True,
        help="Choose whether you want to enter salary/rent values monthly or yearly.",
    )

    is_metro = st.toggle(
        "Metro city (Delhi, Mumbai, Chennai, Kolkata)",
        help="Metro cities get 50% of basic as HRA limit; non-metro gets 40%"
    )

    is_monthly = period == "Monthly"
    unit_short = "month" if is_monthly else "year"
    unit_label = "Monthly" if is_monthly else "Annual"

    col1, col2 = st.columns(2)
    with col1:
        basic_input = st.number_input(
            f"Basic Salary (₹/{unit_short})",
            min_value=0,
            step=1_000,
            help=f"{unit_label} basic salary component",
        )
        hra_input = st.number_input(
            f"HRA Received (₹/{unit_short})",
            min_value=0,
            step=500,
            help=f"{unit_label} HRA component in your salary slip",
        )

    with col2:
        rent_input = st.number_input(
            f"Rent Paid (₹/{unit_short})",
            min_value=0,
            step=500,
            help=f"Actual {unit_label.lower()} rent you pay",
        )

    if basic_input <= 0 or hra_input <= 0 or rent_input <= 0:
        st.info("👆 Enter basic salary, HRA received, and rent paid to calculate HRA exemption.")
        return

    factor = 12 if is_monthly else 1
    basic_annual = basic_input * factor
    hra_annual = hra_input * factor
    rent_annual = rent_input * factor

    result = calculate_hra(basic_annual, hra_annual, rent_annual, is_metro)

    # ── RESULT CARDS ────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3 = st.columns(3)

    exempt_display = result["exempt"]
    taxable_display = result["taxable"]

    with c1:
        st.markdown(
            f"""
            <div style='background:linear-gradient(135deg,#14532d,#166534);
                        border-radius:16px; padding:20px; text-align:center;
                        border:1px solid #4ade80;'>
                <p style='color:#bbf7d0; font-size:12px; margin:0 0 4px;'>✅ Exempt HRA</p>
                <p style='color:#4ade80; font-size:24px; font-weight:700; margin:0;'>{format_inr(exempt_display)}</p>
                <p style='color:#86efac; font-size:11px; margin:4px 0 0;'>Annual · Tax-free</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div style='background:{"linear-gradient(135deg,#7f1d1d,#991b1b)" if result["taxable"] > 0 else "linear-gradient(135deg,#1a1f2e,#252d40)"};
                        border-radius:16px; padding:20px; text-align:center;
                        border:1px solid {"#f87171" if result["taxable"] > 0 else "#374151"};'>
                <p style='color:{"#fecaca" if result["taxable"] > 0 else "#9ca3af"}; font-size:12px; margin:0 0 4px;'>{"⚠️ Taxable HRA" if result["taxable"] > 0 else "Taxable HRA"}</p>
                <p style='color:{"#f87171" if result["taxable"] > 0 else "#e5e7eb"}; font-size:24px; font-weight:700; margin:0;'>{format_inr(taxable_display)}</p>
                <p style='color:{"#fca5a5" if result["taxable"] > 0 else "#6b7280"}; font-size:11px; margin:4px 0 0;'>Annual · Added to income</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        pct = round((result["exempt"] / result["hra_received"] * 100) if result["hra_received"] > 0 else 0)
        st.markdown(
            f"""
            <div style='background:linear-gradient(135deg,#1e3a5f,#1e3a8a);
                        border-radius:16px; padding:20px; text-align:center;
                        border:1px solid #60a5fa;'>
                <p style='color:#bfdbfe; font-size:12px; margin:0 0 4px;'>Exemption %</p>
                <p style='color:#60a5fa; font-size:24px; font-weight:700; margin:0;'>{pct}%</p>
                <p style='color:#93c5fd; font-size:11px; margin:4px 0 0;'>of HRA received</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    if result["taxable"] == 0:
        st.success("🎉 Your entire HRA is exempt from tax!")
    elif result["exempt"] == 0:
        st.error("❌ No HRA exemption — you may not be paying enough rent or HRA is zero.")
    else:
        st.info(
            f"💡 {format_inr(exempt_display)} of your annual HRA is tax-free. "
            f"The remaining {format_inr(taxable_display)} is added to taxable income."
        )

    # ── CALCULATION BREAKDOWN ────────────────────────────────────
    with st.expander("🧮 How is this calculated?"):
        city_label = "Metro (50%)" if is_metro else "Non-Metro (40%)"

        st.markdown("HRA exemption = **minimum** of these 3 values:")

        rows = [
            ("1️⃣ Actual HRA received", format_inr(result["hra_received"])),
            ("2️⃣ Rent paid − 10% of Basic", format_inr(result["rent_minus_10"])),
            (f"3️⃣ {city_label} of Basic", format_inr(result["salary_limit"])),
        ]

        for label, value in rows:
            st.markdown(f"- {label}: `{value}`")

        # st.markdown("---")
        # st.markdown(f"**Minimum = Exempt HRA: `{format_inr(result['exempt'])}`**")

        # st.markdown(f"#### 📥 Inputs Used ({period} values)")
        # st.markdown(f"- Basic: `{format_inr(basic_input)}`")
        # st.markdown(f"- HRA Received: `{format_inr(hra_input)}`")
        # st.markdown(f"- Rent Paid: `{format_inr(rent_input)}`")

        # st.markdown("#### 📤 Annualized Values Used in Formula")
        # st.markdown(f"- Annual Basic: `{format_inr(result['salary'])}`")
        # st.markdown(f"- Annual HRA Received: `{format_inr(result['hra_received'])}`")
        # st.markdown(f"- Annual Rent Paid: `{format_inr(result['rent_annual'])}`")
