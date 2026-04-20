import streamlit as st

from ui.salary_ui import render as salary_page
from ui.offer_ui import render as offer_page
from ui.tax_ui import render as tax_page
from ui.hra_ui import render as hra_page

st.set_page_config(
    page_title="SaveTaxX",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL STYLES ────────────────────────────────────────────
st.markdown("""
<style>
    :root {
        --bg-main: #0b1020;
        --bg-elevated: #121a2e;
        --bg-card: #121a2e;
        --border: #26334f;
        --text-primary: #e8eefc;
        --text-muted: #9fb0d6;
        --accent: #60a5fa;
        --accent-soft: rgba(96, 165, 250, 0.18);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: radial-gradient(circle at top left, #18233f 0%, #0d1324 56%, #0b1120 100%);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 14px !important;
        padding: 8px 0;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }

    /* Main background */
    .stApp {
        background:
            radial-gradient(circle at 12% 0%, rgba(29, 78, 216, 0.22), transparent 36%),
            radial-gradient(circle at 88% 18%, rgba(56, 189, 248, 0.15), transparent 26%),
            var(--bg-main);
    }

    /* Cards and metric boxes */
    [data-testid="stMetric"] {
        background: linear-gradient(155deg, rgba(20, 29, 52, 0.95), rgba(15, 23, 42, 0.92));
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 20px;  /* slightly increased */
        box-shadow: 0 10px 30px rgba(2, 8, 23, 0.34);
    }

    /* FIX: Prevent text truncation in metrics */
    [data-testid="stMetricValue"] {
        font-size: 22px !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: linear-gradient(155deg, rgba(20, 29, 52, 0.9), rgba(15, 23, 42, 0.9));
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    /* Number inputs */
    input[type=number] {
        background: #0e172b !important;
        border: 1px solid #32446e !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
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
        color: var(--text-muted) !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        overflow: hidden;
    }

    h1, h2, h3, h4 {
        color: var(--text-primary) !important;
        letter-spacing: 0.2px;
    }

    .stMarkdown p, label {
        color: var(--text-primary);
    }

    /* Hide streamlit branding */
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; margin:8px 0 18px; border:1px solid #314469;
                border-radius:16px; padding:18px 14px;
                background:linear-gradient(145deg, rgba(30,64,175,0.28), rgba(14,23,43,0.95));'>
        <span style='font-size:34px;'>💰</span>
        <h2 style='color:#e5e7eb; margin:8px 0 4px; font-size:21px;'>SaveTaxX</h2>
        <p style='color:#9fb0d6; font-size:12px; margin:0;'>Real Salary. No Confusion.</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "📂 Menu",
        ["Salary Calculator", "Offer Comparison", "Tax Optimizer", "HRA Calculator"],
        label_visibility="visible",
    )

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
