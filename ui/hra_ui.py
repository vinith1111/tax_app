import streamlit as st
from services.hra_service import calculate_hra
from utils.formatter import format_inr


def render():
    st.markdown("### 🏠 HRA Calculator")
    st.caption("Find how much of your HRA is tax-exempt based on your rent and salary.")

    is_metro = st.toggle(
        "Metro city (Delhi, Mumbai, Chennai, Kolkata)",
        help="Metro cities get 50% of basic as HRA limit; non-metro gets 40%"
    )

    col1, col2 = st.columns(2)
    with col1:
        basic_monthly = st.number_input(
            "Basic Salary (₹/month)",
            min_value=0,
            step=1_000,
            help="Monthly basic salary component",
        )
        hra_monthly = st.number_input(
            "HRA Received (₹/month)",
            min_value=0,
            step=500,
            help="Monthly HRA component in your salary slip",
        )

    with col2:
        rent_monthly = st.number_input(
            "Rent Paid (₹/month)",
            min_value=0,
            step=500,
            help="Actual monthly rent you pay",
        )

    if basic_monthly <= 0:
        st.info("👆 Enter your basic salary to calculate HRA exemption.")
        return

    # Annualize for calculation
    basic_annual = basic_monthly * 12
    hra_annual = hra_monthly * 12

    result = calculate_hra(basic_annual, hra_annual, rent_monthly, is_metro)

    # ── RESULT CARDS ────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div style='background:linear-gradient(135deg,#14532d,#166534);
                        border-radius:16px; padding:20px; text-align:center;
                        border:1px solid #4ade80;'>
                <p style='color:#bbf7d0; font-size:12px; margin:0 0 4px;'>✅ Exempt HRA</p>
                <p style='color:#4ade80; font-size:24px; font-weight:700; margin:0;'>{format_inr(result["exempt"])}</p>
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
                <p style='color:{"#f87171" if result["taxable"] > 0 else "#e5e7eb"}; font-size:24px; font-weight:700; margin:0;'>{format_inr(result["taxable"])}</p>
                <p style='color:{"#fca5a5" if result["taxable"] > 0 else "#6b7280"}; font-size:11px; margin:4px 0 0;'>Annual · Added to income</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        pct = round((result["exempt"] / hra_annual * 100) if hra_annual > 0 else 0)
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
        st.info(f"💡 {format_inr(result['exempt'])} of your annual HRA is tax-free. The remaining {format_inr(result['taxable'])} is added to taxable income.")

    # ── CALCULATION BREAKDOWN ────────────────────────────────────
    with st.expander("🧮 How is this calculated?"):
        city_label = "Metro (50%)" if is_metro else "Non-Metro (40%)"

        st.markdown("HRA exemption = **minimum** of these three values:")

        rows = [
            ("1️⃣ Actual HRA received", format_inr(result["hra_received"])),
            (f"2️⃣ Rent paid − 10% of Basic", format_inr(result["rent_minus_10"])),
            (f"3️⃣ {city_label} of Annual Basic", format_inr(result["salary_limit"])),
        ]

        for label, value in rows:
            st.markdown(f"- {label}: `{value}`")

        st.markdown("---")
        st.markdown(f"**→ Minimum = Exempt HRA: `{format_inr(result['exempt'])}`**")

        st.markdown("#### 📥 Annualized Inputs Used")
        st.markdown(f"- Annual Basic: `{format_inr(result['salary'])}`")
        st.markdown(f"- Annual HRA Received: `{format_inr(result['hra_received'])}`")
        st.markdown(f"- Annual Rent Paid: `{format_inr(result['rent_annual'])}`")

        st.caption("Note: Basic salary and HRA are annualized from monthly values entered above.")
