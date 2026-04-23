import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile
from services.salary_service import calculate_salary
from utils.formatter import format_inr, format_lpa, effective_tax_rate
from validators.input_validator import validate_ctc


def _salary_breakdown_df(ctc, result):
    return pd.DataFrame(
        [
            ["CTC", format_inr(ctc), format_inr(ctc)],
            ["Basic (50%)", format_inr(result["basic"]), format_inr(result["basic"])],
            ["Employer PF", format_inr(result["employer_pf"]), format_inr(result["employer_pf"])],
            ["Gross Salary", format_inr(result["gross"]), format_inr(result["gross"])],
            ["Employee PF", format_inr(result["employee_pf"]), format_inr(result["employee_pf"])],
            ["Professional Tax", "₹2,400", "₹2,400"],
            ["Taxable Income", format_inr(result["taxable_new"]), format_inr(result["taxable_old"])],
            ["Base Tax", format_inr(result["base_tax_new"]), format_inr(result["base_tax_old"])],
            ["Surcharge", format_inr(result["surcharge_new"]), format_inr(result["surcharge_old"])],
            ["Cess (4%)", format_inr(result["cess_new"]), format_inr(result["cess_old"])],
            ["Total Tax", format_inr(result["tax_new"]), format_inr(result["tax_old"])],
            ["Annual In-Hand", format_inr(result["new_inhand"]), format_inr(result["old_inhand"])],
            ["Monthly In-Hand", format_inr(round(result["new_inhand"] / 12)), format_inr(round(result["old_inhand"] / 12))],
        ],
        columns=["Component", "New Regime", "Old Regime"],
    )


def _payslip_data(ctc, result):
    gross_monthly = round(result["gross"] / 12)
    basic_monthly = round(result["basic"] / 12)
    allowances_monthly = max(gross_monthly - basic_monthly, 0)
    employee_pf_monthly = round(result["employee_pf"] / 12)
    professional_tax_monthly = 200
    tds_new_monthly = round(result["tax_new"] / 12)
    tds_old_monthly = round(result["tax_old"] / 12)
    deductions_new = employee_pf_monthly + professional_tax_monthly + tds_new_monthly
    deductions_old = employee_pf_monthly + professional_tax_monthly + tds_old_monthly
    net_pay_new = gross_monthly - deductions_new
    net_pay_old = gross_monthly - deductions_old

    return {
        "gross_monthly": gross_monthly,
        "annual_ctc": ctc,
        "earnings": [
            ("Basic Pay", basic_monthly, basic_monthly),
            ("Other Allowances", allowances_monthly, allowances_monthly),
        ],
        "deductions": [
            ("Employee PF", employee_pf_monthly, employee_pf_monthly),
            ("Professional Tax", professional_tax_monthly, professional_tax_monthly),
            ("TDS", tds_new_monthly, tds_old_monthly),
        ],
        "summary": [
            ("Gross Earnings", gross_monthly, gross_monthly),
            ("Total Deductions", deductions_new, deductions_old),
            ("Net Pay", net_pay_new, net_pay_old),
        ],
        "net_pay_new": net_pay_new,
        "net_pay_old": net_pay_old,
    }


def _text_pdf_bytes(title, payslip, comparison_rows, earnings_rows, deduction_rows, summary_rows):
    def _escape_pdf_text(value):
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def _pdf_safe(value):
        return value.replace("₹", "Rs. ")

    def _draw_text(commands, text, x, y, size=10):
        safe_text = _escape_pdf_text(_pdf_safe(str(text)))
        commands.extend(
            [
                "BT",
                f"/F1 {size} Tf",
                f"{x} {y} Td",
                f"({safe_text}) Tj",
                "ET",
            ]
        )

    def _draw_table(commands, headers, rows, x, y_top, col_widths, row_height=16):
        total_width = sum(col_widths)
        table_rows = [headers] + rows
        total_height = row_height * len(table_rows)
        y_bottom = y_top - total_height

        commands.extend(["0.6 w", f"{x} {y_bottom} {total_width} {total_height} re S"])

        x_cursor = x
        for width in col_widths[:-1]:
            x_cursor += width
            commands.extend([f"{x_cursor} {y_bottom} m", f"{x_cursor} {y_top} l", "S"])

        for i in range(1, len(table_rows)):
            y_line = y_top - i * row_height
            commands.extend([f"{x} {y_line} m", f"{x + total_width} {y_line} l", "S"])

        for row_index, row in enumerate(table_rows):
            y_text = y_top - (row_index + 1) * row_height + 5
            for col_index, cell in enumerate(row):
                left = x + sum(col_widths[:col_index])
                right = left + col_widths[col_index]
                cell_text = _pdf_safe(str(cell))
                if row_index == 0:
                    text_x = left + 6
                elif col_index == 0:
                    text_x = left + 6
                else:
                    approx_text_width = len(cell_text) * 5.2
                    text_x = max(left + 6, right - approx_text_width - 6)
                _draw_text(commands, cell_text, text_x, y_text, size=9)

        return y_bottom

    content_lines = []
    y_cursor = 768
    left_margin = 40

    _draw_text(content_lines, title, left_margin, y_cursor, size=12)
    y_cursor -= 20
    _draw_text(content_lines, "SaveTaxX", left_margin, y_cursor)
    y_cursor -= 16
    _draw_text(content_lines, f"Annual CTC: {format_inr(payslip['annual_ctc'])}", left_margin, y_cursor)
    y_cursor -= 14
    _draw_text(content_lines, f"Monthly Gross Pay: {format_inr(payslip['gross_monthly'])}", left_margin, y_cursor)
    y_cursor -= 14
    _draw_text(content_lines, f"Monthly Net Pay (New): {format_inr(payslip['net_pay_new'])}", left_margin, y_cursor)
    y_cursor -= 14
    _draw_text(content_lines, f"Monthly Net Pay (Old): {format_inr(payslip['net_pay_old'])}", left_margin, y_cursor)
    y_cursor -= 22

    _draw_text(content_lines, "TAX COMPARISON (NEW VS OLD)", left_margin, y_cursor, size=10)
    y_cursor -= 10
    y_cursor = _draw_table(
        content_lines,
        ("Component", "New Regime", "Old Regime"),
        comparison_rows,
        left_margin,
        y_cursor,
        col_widths=(230, 150, 150),
    ) - 18

    _draw_text(content_lines, "EARNINGS", left_margin, y_cursor, size=10)
    y_cursor -= 10
    y_cursor = _draw_table(
        content_lines,
        ("Component", "New Regime", "Old Regime"),
        earnings_rows,
        left_margin,
        y_cursor,
        col_widths=(230, 150, 150),
    ) - 16

    _draw_text(content_lines, "DEDUCTIONS", left_margin, y_cursor, size=10)
    y_cursor -= 10
    y_cursor = _draw_table(
        content_lines,
        ("Component", "New Regime", "Old Regime"),
        deduction_rows,
        left_margin,
        y_cursor,
        col_widths=(230, 150, 150),
    ) - 16

    _draw_text(content_lines, "SUMMARY", left_margin, y_cursor, size=10)
    y_cursor -= 10
    _draw_table(
        content_lines,
        ("Component", "New Regime", "Old Regime"),
        summary_rows,
        left_margin,
        y_cursor,
        col_widths=(230, 150, 150),
    )

    content = "\n".join(content_lines).encode("latin-1", "replace")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
    )
    objects.append(f"4 0 obj << /Length {len(content)} >> stream\n".encode("ascii") + content + b"\nendstream endobj\n")
    objects.append(b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Courier >> endobj\n")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    pdf.extend(
        f"trailer << /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("ascii")
    )
    return bytes(pdf)


def _build_docx_table(rows):
    table_rows = []
    for row_index, row in enumerate(rows):
        row_cells = "".join(
            (
                "<w:tc>"
                "<w:tcPr>"
                "<w:tcW w:w=\"0\" w:type=\"auto\"/>"
                "</w:tcPr>"
                "<w:p><w:r>"
                f"{'<w:rPr><w:b/></w:rPr>' if row_index == 0 else ''}"
                f"<w:t>{escape(str(cell))}</w:t>"
                "</w:r></w:p>"
                "</w:tc>"
            )
            for cell in row
        )
        table_rows.append(f"<w:tr>{row_cells}</w:tr>")
    return (
        "<w:tbl>"
        "<w:tblPr>"
        "<w:tblW w:w=\"0\" w:type=\"auto\"/>"
        "<w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:left w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:right w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "</w:tblBorders>"
        "<w:tblCellMar>"
        "<w:top w:w=\"80\" w:type=\"dxa\"/>"
        "<w:left w:w=\"80\" w:type=\"dxa\"/>"
        "<w:bottom w:w=\"80\" w:type=\"dxa\"/>"
        "<w:right w:w=\"80\" w:type=\"dxa\"/>"
        "</w:tblCellMar>"
        "</w:tblPr>"
        "<w:tblGrid><w:gridCol w:w=\"4200\"/><w:gridCol w:w=\"2100\"/><w:gridCol w:w=\"2100\"/></w:tblGrid>"
        f"{''.join(table_rows)}"
        "</w:tbl>"
    )


def _docx_bytes(title, payslip, comparison_rows):
    brand_name = "SaveTaxX"
    comparison_table_rows = [("Component", "New Regime", "Old Regime")] + comparison_rows
    earnings_rows = [("Earnings", "New Regime", "Old Regime")] + [
        (name, format_inr(new_amount), format_inr(old_amount)) for name, new_amount, old_amount in payslip["earnings"]
    ]
    deduction_rows = [("Deductions", "New Regime", "Old Regime")] + [
        (name, format_inr(new_amount), format_inr(old_amount)) for name, new_amount, old_amount in payslip["deductions"]
    ]
    summary_rows = [("Summary", "New Regime", "Old Regime")] + [
        (name, format_inr(new_amount), format_inr(old_amount)) for name, new_amount, old_amount in payslip["summary"]
    ]

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 wp14">
  <w:body>
    <w:p><w:r><w:rPr><w:b/></w:rPr><w:t>{escape(brand_name)}</w:t></w:r></w:p>
    <w:p><w:r><w:t>{escape(title)}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Annual CTC: {escape(format_inr(payslip['annual_ctc']))}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Monthly Gross Pay: {escape(format_inr(payslip['gross_monthly']))}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Monthly Net Pay (New): {escape(format_inr(payslip['net_pay_new']))}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Monthly Net Pay (Old): {escape(format_inr(payslip['net_pay_old']))}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Tax Comparison (New vs Old)</w:t></w:r></w:p>
    {_build_docx_table(comparison_table_rows)}
    <w:p><w:r><w:t> </w:t></w:r></w:p>
    {_build_docx_table(earnings_rows)}
    <w:p><w:r><w:t> </w:t></w:r></w:p>
    {_build_docx_table(deduction_rows)}
    <w:p><w:r><w:t> </w:t></w:r></w:p>
    {_build_docx_table(summary_rows)}
    <w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>
  </w:body>
</w:document>
"""

    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""
    rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml)
        archive.writestr("_rels/.rels", rels_xml)
        archive.writestr("word/document.xml", document_xml)

    return buffer.getvalue()


def render():
    st.markdown("### Salary Calculator")
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
        st.error(f"{msg}")
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
                {"<span style='background:#166534;color:#4ade80;font-size:11px;padding:3px 10px;border-radius:20px;'>Recommended</span>" if winner == "new" else ""}
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
                {"<span style='background:#166534;color:#4ade80;font-size:11px;padding:3px 10px;border-radius:20px;'>Recommended</span>" if winner == "old" else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    # ── VERDICT BANNER ──────────────────────────────────────────
    if new == old:
        st.info("Both regimes give the same in-hand salary for your CTC.")
    elif winner == "new":
        st.success(f"New Regime saves you **{format_inr(diff)}** per year ({format_inr(round(diff/12))}/month)")
    else:
        st.success(f"Old Regime saves you **{format_inr(abs(diff))}** per year ({format_inr(round(abs(diff)/12))}/month)")

    # ── TAX INSIGHTS ───────────────────────────────────────────
    marginal_relief_message = (
        f"""You crossed <b>₹12L</b> by
        <span style="color:#22c55e;">{format_inr(result['excess_income'])}</span><br>
        Tax reduced by
        <span style="color:#22c55e;">{format_inr(result['marginal_relief_savings'])}</span>"""
        if result["marginal_relief_savings"] > 0
        else "No marginal relief applicable at this CTC."
    )
    st.markdown(f"""
    <div style="
        background:#1a1f2e;
        border:1px solid #1f2937;
        border-radius:12px;
        padding:14px 16px;
        margin-top:12px;
        margin-bottom:4px;
    ">
        <div style="font-size:14px; color:#9ca3af; margin-bottom:6px;">
            Marginal Relief Tax Insight
        </div>
        <div style="font-size:16px; color:#e5e7eb; line-height:1.6;">
            {marginal_relief_message}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── QUICK STATS ─────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CTC", format_lpa(ctc))
    c2.metric("Gross Salary", format_inr(result["gross"]))
    c3.metric("Eff. Tax Rate (New)", f"{effective_tax_rate(result['tax_new'], result['gross'])}%")
    c4.metric("Eff. Tax Rate (Old)", f"{effective_tax_rate(result['tax_old'], result['gross'])}%")

    breakdown_df = _salary_breakdown_df(ctc, result)

    payslip = _payslip_data(ctc, result)
    comparison_rows = [tuple(row) for row in breakdown_df[["Component", "New Regime", "Old Regime"]].values.tolist()]
    document_title = f"Salary Payslip (New vs Old) - CTC {format_inr(ctc)}"
    pdf_filename = f"salary_breakdown_{int(ctc)}.pdf"
    earnings_rows = [(name, format_inr(new_amount), format_inr(old_amount)) for name, new_amount, old_amount in payslip["earnings"]]
    deduction_rows = [
        (name, format_inr(new_amount), format_inr(old_amount)) for name, new_amount, old_amount in payslip["deductions"]
    ]
    summary_rows = [(name, format_inr(new_amount), format_inr(old_amount)) for name, new_amount, old_amount in payslip["summary"]]
    pdf_payload = _text_pdf_bytes(document_title, payslip, comparison_rows, earnings_rows, deduction_rows, summary_rows)

    pdf_b64 = base64.b64encode(pdf_payload).decode("ascii")
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:0;margin:0;padding:0;">
            <h4 style="margin:0;padding:0;">Salary Breakdown</h4>
            <a href="data:application/pdf;base64,{pdf_b64}" download="{pdf_filename}" title="Download payslip PDF"
               style="display:inline-flex;align-items:center;justify-content:center;text-decoration:none;margin:0;padding:0;">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none"
                     stroke="#E5E7EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    compact_rows = [
        "CTC",
        "Gross Salary",
        "Taxable Income",
        "Total Tax",
        "Annual In-Hand",
        "Monthly In-Hand",
    ]
    compact_df = breakdown_df[breakdown_df["Component"].isin(compact_rows)].reset_index(drop=True)
    st.table(compact_df)

    if result["surcharge_new"] > 0:
        st.warning("Surcharge applied — income exceeds ₹50L")

    if result["pf_taxable_contribution_excess"] > 0:
        st.info(
            f"Employee PF contribution above ₹2.5L can create taxable interest. "
            f"Excess contribution: `{format_inr(result['pf_taxable_contribution_excess'])}` · "
            f"Estimated taxable interest (@8.25%): `{format_inr(result['taxable_pf_interest'])}` per year."
        )
