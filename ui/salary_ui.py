import streamlit as st
import pandas as pd
from services.salary_service import calculate_salary
from utils.formatter import format_inr, format_lpa, effective_tax_rate
from validators.input_validator import validate_ctc


def render():
    st.markdown("### 💼 Salary Calculator")
    st.caption("Enter your CTC to see exact in-hand salary under both tax regimes.")

    ctc = st.number_input(
        "Annual CTC (₹)",
        min_value=0,
        max_value=100_000_000,
        step=50_000,
        help="Cost To Company — your total annual package",
    )

    valid, msg = validate_ctc(ctc)

    if ctc > 0 and not valid:
        st.error(f"⚠️ {msg}")
        return

    if not valid:
        return

    result = calculate_salary(ctc)
    new = result["new_inhand"]
    old = result["old_inhand"]
    diff = new - old
    winner = "new" if new >= old else "old"

    # ── MONTHLY IN-HAND HERO ────────────────────────────────────
    st.markdown("---")
    hero_col1, hero_col2 = st.columns(2)
    with hero_col1:
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #1a1f2e, #252d40);
                        border-radius: 16px; padding: 24px; text-align: center;
                        border: 1px solid {"#4ade80" if winner == "new" else "#374151"}'>
                <p style='color:#9ca3af; font-size:13px; margin:0 0 6px;'>Monthly In-Hand · New Regime</p>
                <p style='color:{"#4ade80" if winner == "new" else "#e5e7eb"}; font-size:28px; font-weight:700; margin:0;'>{format_inr(round(new / 12))}</p>
                <p style='color:#6b7280; font-size:12px; margin:6px 0 0;'>{format_inr(new)} / year</p>
                {"<span style='background:#166534;color:#4ade80;font-size:11px;padding:3px 10px;border-radius:20px;'>✓ Recommended</span>" if winner == "new" else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with hero_col2:
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #1a1f2e, #252d40);
                        border-radius: 16px; padding: 24px; text-align: center;
                        border: 1px solid {"#4ade80" if winner == "old" else "#374151"}'>
                <p style='color:#9ca3af; font-size:13px; margin:0 0 6px;'>Monthly In-Hand · Old Regime</p>
                <p style='color:{"#4ade80" if winner == "old" else "#e5e7eb"}; font-size:28px; font-weight:700; margin:0;'>{format_inr(round(old / 12))}</p>
                <p style='color:#6b7280; font-size:12px; margin:6px 0 0;'>{format_inr(old)} / year</p>
                {"<span style='background:#166534;color:#4ade80;font-size:11px;padding:3px 10px;border-radius:20px;'>✓ Recommended</span>" if winner == "old" else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    # ── VERDICT BANNER ──────────────────────────────────────────
    if new == old:
        st.info("⚖️ Both regimes give the same in-hand salary for your CTC.")
    elif winner == "new":
        st.success(f"🏆 New Regime saves you **{format_inr(diff)}** per year ({format_inr(round(diff/12))}/month)")
    else:
        st.success(f"🏆 Old Regime saves you **{format_inr(abs(diff))}** per year ({format_inr(round(abs(diff)/12))}/month)")

    # ── QUICK STATS ─────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CTC", format_lpa(ctc))
    c2.metric("Gross Salary", format_inr(result["gross"]))
    c3.metric("Eff. Tax Rate (New)", f"{effective_tax_rate(result['tax_new'], result['gross'])}%")
    c4.metric("Eff. Tax Rate (Old)", f"{effective_tax_rate(result['tax_old'], result['gross'])}%")

    # ── BAR CHART ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📊 Salary Breakdown Comparison")

    chart_data = pd.DataFrame({
        "Component": ["In-Hand", "Income Tax", "Employee PF", "Professional Tax"],
        "New Regime (₹)": [
            result["new_inhand"],
            result["tax_new"],
            result["employee_pf"],
            2400,
        ],
        "Old Regime (₹)": [
            result["old_inhand"],
            result["tax_old"],
            result["employee_pf"],
            2400,
        ],
    }).set_index("Component")

    st.bar_chart(chart_data, height=280)

    # ── DETAILED BREAKDOWN ──────────────────────────────────────
    with st.expander("🔍 Full Breakdown"):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**💼 Salary Structure**")
            st.markdown(f"- CTC: `{format_inr(ctc)}`")
            st.markdown(f"- Basic (50%): `{format_inr(result['basic'])}`")
            st.markdown(f"- Employer PF: `{format_inr(result['employer_pf'])}`")
            st.markdown(f"- Gross: `{format_inr(result['gross'])}`")
            st.markdown(f"- Employee PF: `{format_inr(result['employee_pf'])}`")
            st.markdown(f"- Professional Tax: `₹2,400`")

        with col2:
            st.markdown("**🏛 New Regime Tax**")
            st.markdown(f"- Taxable Income: `{format_inr(result['taxable_new'])}`")
            st.markdown(f"- Base Tax: `{format_inr(result['base_tax_new'])}`")
            st.markdown(f"- Surcharge: `{format_inr(result['surcharge_new'])}`")
            st.markdown(f"- Cess (4%): `{format_inr(result['cess_new'])}`")
            st.markdown(f"- **Total Tax: `{format_inr(result['tax_new'])}`**")

            st.markdown("**🏛 Old Regime Tax**")
            st.markdown(f"- Taxable Income: `{format_inr(result['taxable_old'])}`")
            st.markdown(f"- Base Tax: `{format_inr(result['base_tax_old'])}`")
            st.markdown(f"- Surcharge: `{format_inr(result['surcharge_old'])}`")
            st.markdown(f"- Cess (4%): `{format_inr(result['cess_old'])}`")
            st.markdown(f"- **Total Tax: `{format_inr(result['tax_old'])}`**")

        if result["surcharge_new"] > 0:
            st.warning("⚠️ Surcharge applied — income exceeds ₹50L")
