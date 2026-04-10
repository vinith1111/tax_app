import streamlit as st

from ui.salary_ui import render as salary_page
from ui.offer_ui import render as offer_page
from ui.tax_ui import render as tax_page
from ui.hra_ui import render as hra_page

st.set_page_config(page_title="SaveTaxX", page_icon="💰")

st.title("💰 SaveTaxX")
st.caption("Real Salary. No Confusion.")

page = st.sidebar.radio(
    "📂 Menu",
    ["Salary Calculator", "Offer Comparison", "Tax Optimizer", "HRA Calculator"]
)

if page == "Salary Calculator":
    salary_page()

elif page == "Offer Comparison":
    offer_page()

elif page == "Tax Optimizer":
    tax_page()

elif page == "HRA Calculator":
    hra_page()


# ---------------- FOOTER ----------------
st.markdown("""
<hr style="border:0.5px solid #2a2f36; margin-top:30px;">

<div style='text-align:center; color:#9DA5B4; font-size:13px;'>
🔒 No data stored. Private & secure.<br>
💰 SaveTaxX — Real Salary. No Confusion.
</div>
""", unsafe_allow_html=True)
