import streamlit as st
from services.salary_service import calculate_salary
from utils.formatter import format_inr, effective_tax_rate


def render():
    header_html = """
    <div style='padding:20px 22px; border-radius:18px; margin-bottom:16px;
                border:1px solid #315189;
                background:linear-gradient(125deg, rgba(30,64,175,0.34), rgba(12,20,37,0.98));'>
        <p style='margin:0; color:#cde0ff; font-size:12px; letter-spacing:0.06em; text-transform:uppercase;'>Tax planning cockpit</p>
        <h3 style='margin:4px 0 7px;'>🎯 Tax Optimizer</h3>
        <p style='margin:0; color:#a8bbdd; font-size:13px;'>Model deductions quickly and pick the regime that leaves you with more in-hand salary.</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        ctc = st.number_input("Annual CTC (₹)", min_value=0, step=50_000)
        section_80c = st.number_input(
            "80C Investments (₹)",
            min_value=0,
            max_value=150_000,
            value=150_000,
            help="ELSS, PPF, LIC, EPF top-up etc. Max: ₹1,50,000",
        )
        section_80d = st.number_input(
            "80D Health Insurance (₹)",
            min_value=0,
            max_value=75_000,
            value=25_000,
            help="Self + family premium. Max ₹25,000 (₹50,000 for senior citizens)",
        )

    with col2:
        nps = st.number_input(
            "NPS 80CCD(1B) (₹)",
            min_value=0,
            max_value=50_000,
            value=50_000,
            help="Additional NPS contribution over 80C. Max: ₹50,000",
        )
        hra_deduction = st.number_input(
            "HRA Exemption (₹)",
            min_value=0,
            value=0,
            help="Annual HRA exemption (use HRA Calculator to find this)",
        )
        other = st.number_input("Other Deductions (₹)", min_value=0, value=0)

    if ctc < 120_000:
        if ctc > 0:
            st.error("⚠️ CTC should be minimum ₹1,20,000")
        return

    total_deductions = section_80c + section_80d + nps + hra_deduction + other
    result_with = calculate_salary(ctc, section_80c + section_80d + nps, hra_deduction, other)
    result_without = calculate_salary(ctc, 0, 0, 0)

    new_inhand = result_with["new_inhand"]
    old_inhand = result_with["old_inhand"]
    diff = old_inhand - new_inhand

    # ── REGIME COMPARISON ───────────────────────────────────────
    st.markdown("<div style='margin:2px 0 4px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    winner = "old" if old_inhand >= new_inhand else "new"

    for col, label, inhand, tax, regime in [
        (c1, "New Regime", new_inhand, result_with["tax_new"], "new"),
        (c2, f"Old Regime (with ₹{total_deductions/100000:.1f}L deductions)", old_inhand, result_with["tax_old"], "old"),
    ]:
        is_winner = regime == winner
        with col:
            st.markdown(
                f"""
                <div style='background:{"linear-gradient(135deg,#14532d,#166534)" if is_winner else "linear-gradient(135deg,#1a1f2e,#252d40)"};
                            border-radius:18px; padding:22px 18px; text-align:center;
                            border:1px solid {"#4ade80" if is_winner else "#3a4357"}; margin-bottom:8px;'>
                    <p style='color:{"#bbf7d0" if is_winner else "#9ca3af"}; font-size:12px; margin:0 0 6px;'>{label}</p>
                    <p style='color:{"#4ade80" if is_winner else "#e5e7eb"}; font-size:27px; font-weight:700; margin:0;'>{format_inr(round(inhand/12))}/mo</p>
                    <p style='color:{"#86efac" if is_winner else "#6b7280"}; font-size:12px; margin:4px 0 0;'>Tax: {format_inr(tax)} · Rate: {effective_tax_rate(tax, result_with["gross"])}%</p>
                    {"<span style='background:#052e16;color:#4ade80;font-size:11px;padding:2px 8px;border-radius:20px;'>✓ Better</span>" if is_winner else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

    if diff > 0:
        st.success(f"🏆 Strong result: old regime saves **{format_inr(diff)}/year** versus new regime.")
    elif diff < 0:
        st.info(f"💡 New regime is still ahead by **{format_inr(abs(diff))}/year** with current deductions.")
    else:
        st.info("⚖️ Both regimes give the same result with these deductions.")

    # ── OPTIMIZATION TIPS ────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 💡 Optimization Tips")

    tips = []
    if section_80c < 150_000:
        gap = 150_000 - section_80c
        tips.append(f"**80C:** Invest ₹{gap:,} more (ELSS/PPF) to max out the ₹1.5L limit")
    if nps < 50_000:
        gap = 50_000 - nps
        tips.append(f"**NPS 80CCD(1B):** Contribute ₹{gap:,} more to NPS for extra ₹50K deduction")
    if section_80d < 25_000:
        gap = 25_000 - section_80d
        tips.append(f"**80D:** Pay ₹{gap:,} more in health insurance premiums to reach ₹25K limit")
    if hra_deduction == 0:
        tips.append("**HRA:** If you pay rent, use the HRA Calculator to claim exemption")

    if tips:
        for tip in tips:
            st.markdown(f"- {tip}")
    else:
        st.success("✅ You've maxed out all major deductions!")

    # ── DEDUCTION SUMMARY ───────────────────────────────────────
    with st.expander("📊 Deduction Summary"):
        rows = {
            "Standard Deduction (auto)": "₹50,000",
            "Professional Tax (auto)": "₹2,400",
            "80C Investments": format_inr(section_80c),
            "80D Health Insurance": format_inr(section_80d),
            "NPS 80CCD(1B)": format_inr(nps),
            "HRA Exemption": format_inr(hra_deduction),
            "Other": format_inr(other),
            "Total": format_inr(total_deductions + 52_400),
        }
        for k, v in rows.items():
            st.markdown(f"- **{k}:** `{v}`")
