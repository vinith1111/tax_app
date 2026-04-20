import streamlit as st

from ui.salary_ui import render as salary_page
from ui.offer_ui import render as offer_page
from ui.tax_ui import render as tax_page
from ui.hra_ui import render as hra_page

MENU_OPTIONS = ["Salary Calculator", "Offer Comparison", "Tax Optimizer", "HRA Calculator"]

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
        --bg-main: #070b16;
        --bg-layer: #0f172a;
        --bg-card: #121b31;
        --bg-card-soft: #15213b;
        --border: #2a3d64;
        --border-soft: #334977;
        --text-primary: #edf2ff;
        --text-muted: #a8b8d9;
        --text-soft: #88a0cd;
        --accent: #69b6ff;
        --accent-2: #7c8cff;
        --success: #4ade80;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 0% 0%, rgba(107, 114, 255, 0.22), transparent 46%),
            radial-gradient(circle at 100% 20%, rgba(56, 189, 248, 0.18), transparent 34%),
            linear-gradient(170deg, #0f172a 0%, #0b1428 55%, #0a1324 100%);
        border-right: 1px solid var(--border-soft);
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 14px !important;
        padding: 9px 0;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* Main background */
    .stApp {
        background:
            radial-gradient(circle at 12% 0%, rgba(59, 130, 246, 0.2), transparent 36%),
            radial-gradient(circle at 92% 16%, rgba(129, 140, 248, 0.14), transparent 30%),
            radial-gradient(circle at 44% 100%, rgba(14, 165, 233, 0.12), transparent 34%),
            var(--bg-main);
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 1.4rem;
    }

    /* Cards and metric boxes */
    [data-testid="stMetric"] {
        background: linear-gradient(155deg, rgba(22, 32, 56, 0.94), rgba(16, 24, 45, 0.96));
        border: 1px solid var(--border-soft);
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 18px 34px rgba(2, 8, 23, 0.34);
    }

    /* FIX: Prevent text truncation in metrics */
    [data-testid="stMetricValue"] {
        font-size: 22px !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: linear-gradient(155deg, rgba(19, 29, 52, 0.9), rgba(13, 21, 39, 0.9));
        border: 1px solid var(--border-soft);
        border-radius: 14px;
    }

    /* Number inputs */
    input[type=number] {
        background: #0f1a33 !important;
        border: 1px solid #37558f !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }
    input[type=number]:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px rgba(105, 182, 255, 0.28) !important;
    }

    [data-testid="stTextInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #0f1a33 !important;
        border: 1px solid #37558f !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }

    button[kind="primary"] {
        background: linear-gradient(120deg, #2563eb, #4f46e5) !important;
        border: none !important;
        border-radius: 10px !important;
    }
    button[kind="primary"]:hover {
        filter: brightness(1.06);
    }

    /* Success / info / warning banners */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Divider */
    hr {
        border-color: #24334f !important;
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

    .shell-card {
        border-radius: 20px;
        border: 1px solid var(--border-soft);
        background: linear-gradient(160deg, rgba(22, 35, 62, 0.96), rgba(13, 24, 46, 0.98));
        box-shadow: 0 24px 42px rgba(2, 8, 23, 0.38);
    }

    /* Hide streamlit branding */
    #MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='shell-card' style='text-align:left; margin:6px 0 20px; padding:16px 14px;'>
        <div style='display:flex; align-items:center; gap:10px; margin-bottom:8px;'>
            <span style='font-size:30px;'>💰</span>
            <div>
                <h2 style='color:#e8eeff; margin:0; font-size:20px; line-height:1.2;'>SaveTaxX</h2>
                <p style='color:#a9badc; font-size:11px; margin:2px 0 0;'>Tax Planning Workspace</p>
            </div>
        </div>
        <p style='color:#90a7d2; font-size:12px; margin:0; line-height:1.5;'>
            One place to compare salary, optimize taxes, and maximize monthly in-hand.
        </p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "📂 Menu",
        MENU_OPTIONS,
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
<div style='text-align:center; color:#7183aa; font-size:12px; padding:8px 0 24px; letter-spacing:0.2px;'>
    💰 SaveTaxX · Smart tax decisions, clearer take-home outcomes.
</div>
""", unsafe_allow_html=True)
