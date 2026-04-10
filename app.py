import streamlit as st

from ui.salary_ui import render as salary_page
from ui.offer_ui import render as offer_page
from ui.tax_ui import render as tax_page
from ui.hra_ui import render as hra_page

st.set_page_config(
    page_title="SaveTaxX",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── GLOBAL STYLES ────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0f1117;
        border-right: 1px solid #1f2937;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 14px !important;
        padding: 6px 0;
    }

    /* Main background */
    .stApp {
        background: #0f1117;
    }

    /* Cards and metric boxes */
    [data-testid="stMetric"] {
        background: #1a1f2e;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 12px 16px;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: #1a1f2e;
        border: 1px solid #1f2937;
        border-radius: 12px;
    }

    /* Number inputs */
    input[type=number] {
        background: #1a1f2e !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        color: #e5e7eb !important;
    }

    /* Success / info / warning banners */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Divider */
    hr {
        border-color: #1f2937 !important;
    }

    /* Caption text */
    .stCaption {
        color: #6b7280 !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        # border-radius: 12px;
        overflow: hidden;
    }

    /* Hide streamlit branding */
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 24px;'>
        <span style='font-size:40px;'>💰</span>
        <h2 style='color:#e5e7eb; margin:8px 0 4px; font-size:22px;'>SaveTaxX</h2>
        <p style='color:#6b7280; font-size:13px; margin:0;'>Real Salary. No Confusion.</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "📂 Menu",
        ["Salary Calculator", "Offer Comparison", "Tax Optimizer", "HRA Calculator"],
        label_visibility="visible",
    )

    # st.markdown("---")
    # st.markdown("""
    # <div style='font-size:12px; color:#4b5563; padding:8px 0;'>
        # <p>📅 FY 2024–25 | AY 2025–26</p>
        # <p>🏛 New & Old regime comparison</p>
        # <p>✅ Surcharge & cess included</p>
        # <p>🔒 No data stored. Private & secure.</p>
    # </div>
    # """, unsafe_allow_html=True)

# ── PAGE ROUTING ─────────────────────────────────────────────
if page == "Salary Calculator":
    salary_page()
elif page == "Offer Comparison":
    offer_page()
elif page == "Tax Optimizer":
    tax_page()
elif page == "HRA Calculator":
    hra_page()

# ── FOOTER ───────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:#4b5563; font-size:12px; padding:8px 0 24px;'>
    💰 SaveTaxX — Real Salary. No Confusion.
</div>
""", unsafe_allow_html=True)
