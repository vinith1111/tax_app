import streamlit as st
import pandas as pd
from services.salary_service import calculate_salary
from utils.formatter import format_inr, format_lpa, effective_tax_rate


def render():
    st.markdown("### 🤝 Offer Comparison")
    st.caption("Compare two job offers by actual monthly in-hand — not just CTC.")

    col1, col2 = st.columns(2)
    with col1:
        ctc1 = st.number_input("Offer A — CTC (₹)", min_value=0, step=50_000)
    with col2:
        ctc2 = st.number_input("Offer B — CTC (₹)", min_value=0, step=50_000)

    # ── VALIDATION ─────────────────────────────────────────────
    if ctc1 == 0 and ctc2 == 0:
        st.info("💡 Enter both CTCs above to compare offers.")
        return

    if ctc1 > 0 and ctc2 == 0:
        st.info("👉 Enter Offer B CTC to compare.")
        return

    if ctc2 > 0 and ctc1 == 0:
        st.info("👉 Enter Offer A CTC to compare.")
        return

    if (0 < ctc1 < 120_000) or (0 < ctc2 < 120_000):
        st.error("⚠️ CTC should be minimum ₹1,20,000")
        return

    result1 = calculate_salary(ctc1)
    result2 = calculate_salary(ctc2)

    new1, new2 = result1["new_inhand"], result2["new_inhand"]
    diff = new2 - new1
    winner = "B" if diff > 0 else "A"
    winner_inhand = new2 if diff > 0 else new1

    # ── HERO CARDS ──────────────────────────────────────────────
    st.markdown("---")
    c1, c2 = st.columns(2)

    for col, label, res, ctc in [(c1, "A", result1, ctc1), (c2, "B", result2, ctc2)]:
        is_winner = (label == winner)
        with col:
            st.markdown(
                f"""
                <div style='background:{"linear-gradient(135deg,#14532d,#166534)" if is_winner else "linear-gradient(135deg,#1a1f2e,#252d40)"};
                            border-radius:16px; padding:24px; text-align:center;
                            border:1px solid {"#4ade80" if is_winner else "#374151"}'>
                    <p style='color:{"#bbf7d0" if is_winner else "#9ca3af"}; font-size:13px; margin:0 0 4px;'>Offer {label} · {format_lpa(ctc)}</p>
                    <p style='color:{"#4ade80" if is_winner else "#e5e7eb"}; font-size:30px; font-weight:700; margin:0;'>{format_inr(round(res["new_inhand"]/12))}</p>
                    <p style='color:{"#86efac" if is_winner else "#6b7280"}; font-size:12px; margin:6px 0 0;'>per month · {format_inr(res["new_inhand"])} / yr</p>
                    {"<span style='background:#052e16;color:#4ade80;font-size:11px;padding:3px 10px;border-radius:20px;'>🏆 Better Offer</span>" if is_winner else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    # ── VERDICT ─────────────────────────────────────────────────
    if diff == 0:
        st.info("⚖️ Both offers give identical in-hand salary.")
    else:
        st.success(
            f"🏆 **Offer {winner}** puts **{format_inr(round(abs(diff)/12))}/month** more in your pocket "
            f"({format_inr(abs(diff))}/year)"
        )

    # ── BREAKDOWN TABLE ─────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📊 Side-by-Side Breakdown")

    breakdown = pd.DataFrame({
        "": ["CTC", "Gross Salary", "Income Tax", "Employee PF", "Monthly In-Hand", "Eff. Tax Rate"],
        "Offer A": [
            format_inr(ctc1),
            format_inr(result1["gross"]),
            format_inr(result1["tax_new"]),
            format_inr(result1["employee_pf"]),
            format_inr(round(new1 / 12)),
            f"{effective_tax_rate(result1['tax_new'], result1['gross'])}%",
        ],
        "Offer B": [
            format_inr(ctc2),
            format_inr(result2["gross"]),
            format_inr(result2["tax_new"]),
            format_inr(result2["employee_pf"]),
            format_inr(round(new2 / 12)),
            f"{effective_tax_rate(result2['tax_new'], result2['gross'])}%",
        ],
    }).set_index("")

    st.dataframe(breakdown, use_container_width=True)

    # ── NET GAIN BREAKDOWN ──────────────────────────────────────
    st.markdown("#### 🧮 Where Does the Difference Come From?")

    pf_diff = result2["employee_pf"] - result1["employee_pf"]
    tax_diff = result2["tax_new"] - result1["tax_new"]
    gross_diff = result2["gross"] - result1["gross"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CTC Difference", format_inr(ctc2 - ctc1))
    c2.metric("Gross Difference", format_inr(gross_diff))
    c3.metric("Extra Tax", format_inr(tax_diff), delta=f"-{format_inr(tax_diff)}", delta_color="inverse")
    c4.metric("Net Gain", format_inr(diff), delta=format_inr(round(diff / 12)) + "/mo")

    # ── TAX INSIGHT ─────────────────────────────────────────────
    excess2 = result2.get("excess_income", 0)
    tax1, tax2 = result1["tax_new"], result2["tax_new"]

    if tax1 == 0 and tax2 == 0:
        st.info("✅ Both offers fall under ₹12L taxable limit — zero tax for both.")
    elif tax1 == 0 and tax2 > 0:
        st.warning("⚠️ Offer B crosses the ₹12L taxable limit — tax kicks in.")
        if 0 < excess2 < 100_000:
            st.caption(f"💡 Offer B exceeds ₹12L by only {format_inr(excess2)} — the tax impact is relatively small.")
    else:
        st.info("ℹ️ Both offers are taxable. Higher CTC = higher tax, but Offer B still nets more.")
