import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_shadcn_ui as ui
from pygwalker.api.streamlit import StreamlitRenderer
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw.csv')

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df['Visit_Date'] = pd.to_datetime(df['Visit_Date'])
    df['Ticket_Revenue'] = df['Ticket_Price'] * df['Num_Tickets']
    df['Total_Revenue'] = df['Ticket_Revenue'] + df['Merchandise_Spend'] + df['Drink_Spend']
    df['Repeat_Label'] = df['Repeat_Visit'].map({1: 'Repeat', 0: 'First-Time'})
    bins = [0, 25, 35, 45, 55, 65, 100]
    labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
    df['Age_Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=True)
    return df

def show():
    df = load_data()
    st.header("Customer Analysis")
    st.markdown("In-depth look at demographics, spending behavior, and customer loyalty.")

    # ── Shadcn KPIs ──
    total_cust = df['Customer_ID'].nunique()
    avg_tickets = df['Num_Tickets'].mean()
    repeat_rate = df['Repeat_Visit'].mean() * 100
    avg_age = df['Age'].mean()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        ui.metric_card(title="Unique Customers", content=f"{total_cust:,}", key="cust_m1")
    with m2:
        ui.metric_card(title="Avg Tickets/Order", content=f"{avg_tickets:.1f}", key="cust_m2")
    with m3:
        ui.metric_card(title="Loyalty Rate", content=f"{repeat_rate:.1f}%", key="cust_m3")
    with m4:
        ui.metric_card(title="Median Age", content=f"{avg_age:.0f}", key="cust_m4")

    st.divider()

    # ── Section 1: Demographics ──
    st.subheader("👥 Customer Demographics")
    col_d1, col_d2 = st.columns(2)

    with col_d1:
        gender_counts = df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig_gender = px.pie(
            gender_counts, values='Count', names='Gender',
            hole=0.4, title='Gender Split',
            color_discrete_sequence=['#118AB2', '#E63946', '#06D6A0']
        )
        st.plotly_chart(fig_gender, use_container_width=True)

    with col_d2:
        age_counts = df['Age_Group'].value_counts().sort_index().reset_index()
        age_counts.columns = ['Age_Group', 'Count']
        fig_age = px.bar(
            age_counts, x='Age_Group', y='Count',
            color='Count', color_continuous_scale='Tealgrn',
            title='Age Group Distribution'
        )
        st.plotly_chart(fig_age, use_container_width=True)

    st.divider()

    # ── Section 2: Geography ──
    st.subheader("🌎 Market Distribution")
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        country_counts = df['Country'].value_counts().reset_index().head(10)
        country_counts.columns = ['Country', 'Count']
        fig_country = px.bar(
            country_counts.sort_values('Count', ascending=True),
            x='Count', y='Country',
            orientation='h', color='Count',
            color_continuous_scale='Blues',
            title='Top 10 Countries'
        )
        st.plotly_chart(fig_country, use_container_width=True)

    with col_g2:
        country_region = df.groupby(['Country', 'Seating_Region'])['Customer_ID'].count().reset_index().head(20)
        country_region.columns = ['Country', 'Seating_Region', 'Count']
        fig_cr = px.bar(
            country_region, x='Country', y='Count', color='Seating_Region',
            barmode='stack', title='Regional Volume by Country'
        )
        st.plotly_chart(fig_cr, use_container_width=True)

    st.divider()

    # ── Pygwalker Customer Explorer ──
    st.subheader("👥 Customer Segmentation Explorer")
    renderer = StreamlitRenderer(df)
    renderer.explorer()

    if st.session_state.get('advanced_mode'):
        st.divider()
        st.subheader("🔬 Advanced Behavioral Statistics")
        from scipy import stats
        
        # Chi-Square: Gender vs. Repeat Visit
        contingency = pd.crosstab(df['Gender'], df['Repeat_Visit'])
        chi2, p_val, dof, ex = stats.chi2_contingency(contingency)
        sig_text = "dependent (linked)" if p_val < 0.05 else "independent"
        
        col_adv1, col_adv2 = st.columns(2)
        with col_adv1:
            ui.card(
                title="Gender vs Loyalty (Chi2)",
                content=f"Chi2 Stat: **{chi2:.2f}** (p={p_val:.4f}). Gender and Loyalty are statistically **{sig_text}**.",
                description="Testing if one gender is more likely to be a repeat visitor.",
                key="cust_adv_1"
            ).render()
        with col_adv2:
            avg_age_repeat = df[df['Repeat_Visit'] == 1]['Age'].mean()
            avg_age_first = df[df['Repeat_Visit'] == 0]['Age'].mean()
            diff = avg_age_repeat - avg_age_first
            ui.card(
                title="Loyalty Age Delta",
                content=f"Repeat visitors are, on average, **{abs(diff):.1f} years {'older' if diff > 0 else 'younger'}** than first-time visitors.",
                description="Age-based Loyalty Analysis",
                key="cust_adv_2"
            ).render()