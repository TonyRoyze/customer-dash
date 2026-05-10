import streamlit as st
from streamlit_option_menu import option_menu

from views import overview, revenue_analysis, customer_analysis, time_analysis

st.set_page_config(page_title="Venue Analytics Dashboard", layout="wide")

# ── Inject custom CSS based on index.css design tokens ──
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
    /* ── Typography (--font-sans: DM Sans) ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
    }
    code, pre, .stCode {
        font-family: 'Space Mono', monospace !important;
    }

    /* ── Brutalist card shadows on metric containers ── */
    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 2px solid #000000;
        border-radius: 0px;
        padding: 16px 20px;
        box-shadow: 4px 4px 0px 0px rgba(0, 0, 0, 1);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0px 0px rgba(0, 0, 0, 1);
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        color: #555;
    }
    [data-testid="stMetricValue"] {
        font-weight: 700;
        font-size: 1.6rem;
        color: #000;
    }

    /* ── Chart containers / expanders ── */
    [data-testid="stExpander"] {
        border: 2px solid #000;
        border-radius: 0px;
        box-shadow: 4px 4px 0px 0px rgba(0, 0, 0, 1);
    }

    /* ── Dataframe containers ── */
    [data-testid="stDataFrame"] {
        border: 2px solid #000;
        border-radius: 0px;
        box-shadow: 4px 4px 0px 0px rgba(0, 0, 0, 0.5);
    }

    /* ── Inputs (selectbox, text input) ── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stTextInput"] > div > div > input,
    [data-testid="stNumberInput"] > div > div > input,
    [data-testid="stTextArea"] > div > div > textarea,
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        border: 2px solid #000 !important;
        border-radius: 0px !important;
        box-shadow: 3px 3px 0px 0px rgba(0, 0, 0, 0.8) !important;
    }

    /* ── Table / Dataframe specific ── */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border-radius: 0px !important;
    }
    [data-testid="stDataFrame"] > div {
        border-radius: 0px !important;
    }

    /* ── Expander (Filters container) ── */
    [data-testid="stExpander"], [data-testid="stExpander"] > details {
        border-radius: 0px !important;
    }
    [data-testid="stExpander"] summary {
        border-radius: 0px !important;
    }

    /* ── Dividers ── */
    [data-testid="stDivider"] {
        border-color: #000 !important;
    }

    /* ── Page title styling ── */
    h1 {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    h2, h3 {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
    }

    /* ── Main container subtle background ── */
    .main .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Navigation (themed to match index.css primary/accent) ──
selected = option_menu(
    menu_title=None,
    options=["Overview", "Revenue","Customer Analysis",  "Time Analysis"],
    icons=["house", "currency-dollar", "people", "calendar3"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0!important",
            "background-color": "#000000",
            "border-radius": "0px",
            "border": "2px solid #000",
            "box-shadow": "4px 4px 0px 0px rgba(0,0,0,1)",
            "margin-bottom": "1.5rem",
        },
        "icon": {
            "color": "#FFD166",
            "font-size": "18px",
        },
        "nav-link": {
            "font-size": "14px",
            "text-align": "center",
            "margin": "0px",
            "padding": "12px 16px",
            "color": "#FFFFFF",
            "font-family": "'DM Sans', sans-serif",
            "font-weight": "600",
            "text-transform": "uppercase",
            "letter-spacing": "0.05em",
            "border-radius": "0px",
            "--hover-color": "#E63A46",
        },
        "nav-link-selected": {
            "background-color": "#118AB2",
            "border-radius": "0px",
            "font-weight": "700",
        },
    }
)

if selected == "Overview":
    overview.show()
elif selected == "Revenue":
    revenue_analysis.show()
elif selected == "Customer Analysis":
    customer_analysis.show()
elif selected == "Time Analysis":
    time_analysis.show()