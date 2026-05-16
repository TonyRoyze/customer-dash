import streamlit as st
import streamlit_shadcn_ui as ui
from views import overview, revenue_analysis, customer_analysis, time_analysis, predictions

st.set_page_config(page_title="Venue Analytics Dashboard", layout="wide")

if "advanced_mode" not in st.session_state:
    st.session_state.advanced_mode = False

# ── Sidebar Navigation ──
with st.sidebar:
    st.image("https://img.icons8.com/color/96/stadium.png", width=80)
    st.title("Venue Hub")
    st.divider()
    
    main_page = st.sidebar.radio(
        "Main Menu",
        options=["Analytics", "Predictions"],
        index=0
    )
    
    st.sidebar.divider()
    st.sidebar.caption("System Status: Online")

# ── Header ──
col_title, col_toggle = st.columns([4, 1])

with col_title:
    st.title("🏟️ Venue Dashboard" if main_page == "Analytics" else "🔮 Predictive Modeling")

with col_toggle:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    adv_mode = ui.switch(label="Advanced Mode", default_checked=st.session_state.advanced_mode, key="adv_toggle")
    st.session_state.advanced_mode = adv_mode

st.divider()

# ── Page Routing ──
if main_page == "Analytics":
    # Shadcn UI Tabs for Analytics Navigation
    selected = ui.tabs(
        options=["Overview", "Revenue", "Customer Analysis", "Time Analysis"],
        default_value="Overview",
        key="main_nav"
    )
    
    if selected == "Overview":
        overview.show()
    elif selected == "Revenue":
        revenue_analysis.show()
    elif selected == "Customer Analysis":
        customer_analysis.show()
    elif selected == "Time Analysis":
        time_analysis.show()
else:
    predictions.show()