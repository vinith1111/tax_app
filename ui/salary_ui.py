import streamlit as st
import pandas as pd
import altair as alt
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
    # st.markdown("---")
    # st.markdown("#### 📊 Salary Breakdown Comparison")

    # chart_data = pd.DataFrame(
    #     {
    #         "Regime": ["New Regime", "Old Regime"],
    #         "In-Hand": [result["new_inhand"], result["old_inhand"]],
    #         "Income Tax": [result["tax_new"], result["tax_old"]],
    #         "Employee PF": [result["employee_pf"], result["employee_pf"]],
    #         "Professional Tax": [2400, 2400],
    #     }
    # )

    # chart_long = chart_data.melt(
    #     id_vars="Regime",
    #     var_name="Component",
    #     value_name="Amount",
    # )
    # component_order = ["In-Hand", "Income Tax", "Employee PF", "Professional Tax"]
    # chart_long["Component"] = pd.Categorical(
    #     chart_long["Component"],
    #     categories=component_order,
    #     ordered=True,
    # )

    # chart = (
    #     alt.Chart(chart_long)
    #     .mark_bar()
    #     .encode(
    #         x=alt.X("Amount:Q", title="Amount (₹)", stack="zero"),
    #         y=alt.Y("Regime:N", title=""),
    #         color=alt.Color(
    #             "Component:N",
    #             sort=component_order,
    #             scale=alt.Scale(
    #                 domain=component_order,
    #                 range=["#22c55e", "#ef4444", "#f59e0b", "#6b7280"],
    #             ),
    #         ),
    #         tooltip=[
    #             alt.Tooltip("Regime:N"),
    #             alt.Tooltip("Component:N"),
    #             alt.Tooltip("Amount:Q", format=","),
    #         ],
    #     )
    #     .properties(height=180)
    # )

    # st.altair_chart(chart, use_container_width=True)

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
            st.markdown(f"- Status: `{result['threshold_message']}`")
            st.markdown(f"- Base Tax: `{format_inr(result['base_tax_new'])}`")
            st.markdown(f"- Surcharge: `{format_inr(result['surcharge_new'])}`")
            st.markdown(f"- Cess (4%): `{format_inr(result['cess_new'])}`")
            st.markdown(f"- **Total Tax: `{format_inr(result['tax_new'])}`**")

            if result["marginal_relief_savings"] > 0:
                st.markdown(f"""
                <div style="
                    background:#1a1f2e;
                    border:1px solid #1f2937;
                    border-radius:12px;
                    padding:14px 16px;
                    margin-top:12px;
                ">
                    <div style="font-size:14px; color:#9ca3af; margin-bottom:6px;">
                        🧠 Marginal Relief Insight
                    </div>
                    <div style="font-size:16px; color:#e5e7eb; line-height:1.6;">
                        You crossed <b>₹12L</b> by 
                        <span style="color:#22c55e;">{format_inr(result['excess_income'])}</span><br>
                        Tax reduced by 
                        <span style="color:#22c55e;">{format_inr(result['marginal_relief_savings'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("**🏛 Old Regime Tax**")
            st.markdown(f"- Taxable Income: `{format_inr(result['taxable_old'])}`")
            st.markdown(f"- Base Tax: `{format_inr(result['base_tax_old'])}`")
            st.markdown(f"- Surcharge: `{format_inr(result['surcharge_old'])}`")
            st.markdown(f"- Cess (4%): `{format_inr(result['cess_old'])}`")
            st.markdown(f"- **Total Tax: `{format_inr(result['tax_old'])}`**")

    # Outside expander
    if result["surcharge_new"] > 0:
        st.warning("⚠️ Surcharge applied — income exceeds ₹50L")

    if result["pf_taxable_contribution_excess"] > 0:
        st.info(
            f"🧾 Employee PF contribution above ₹2.5L can create taxable interest. "
            f"Excess contribution: `{format_inr(result['pf_taxable_contribution_excess'])}` · "
            f"Estimated taxable interest (@8.25%): `{format_inr(result['taxable_pf_interest'])}` per year."
        )
