import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_shadcn_ui as ui
from pygwalker.api.streamlit import StreamlitRenderer
import utils

def show():
    df = utils.load_dashboard_data()
    st.header("Revenue Analysis")
    st.markdown("Detailed breakdown of revenue streams and geographical performance.")

    # ── Modern Filters ──
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        countries = ['All'] + sorted(df['Country'].unique().tolist())
        sel_country = st.selectbox("Market Filter", countries, key="rev_country_modern")
    
    filtered = df.copy()
    if sel_country != 'All':
        filtered = filtered[filtered['Country'] == sel_country]

    # ── Shadcn Metrics ──
    t_rev = filtered['Ticket_Revenue'].sum()
    m_rev = filtered['Merchandise_Spend'].sum()
    d_rev = filtered['Drink_Spend'].sum()
    tot_rev = filtered['Total_Revenue'].sum()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        ui.metric_card(title="Ticket Sales", content=f"${t_rev:,.0f}", key="rev_m1")
    with m2:
        ui.metric_card(title="Merch Sales", content=f"${m_rev:,.0f}", key="rev_m2")
    with m3:
        ui.metric_card(title="Drink Sales", content=f"${d_rev:,.0f}", key="rev_m3")
    with m4:
        ui.metric_card(title="Combined Total", content=f"${tot_rev:,.0f}", key="rev_m4")

    st.divider()

    # ── Regional Analysis ──
    st.subheader("📍 Performance by Region & Country")
    c1, c2 = st.columns(2)

    with c1:
        monthly_rev = filtered.groupby(filtered['Visit_Date'].dt.to_period('M').dt.to_timestamp()).agg(
            Ticket=('Ticket_Revenue', 'sum'),
            Merchandise=('Merchandise_Spend', 'sum'),
            Drink=('Drink_Spend', 'sum')
        ).reset_index()
        monthly_rev.columns = ['Month', 'Ticket', 'Merchandise', 'Drink']
        
        fig_timeline = px.area(
            monthly_rev, x='Month', y=['Ticket', 'Merchandise', 'Drink'],
            color_discrete_sequence=['#E63946', '#FFD166', '#118AB2'],
            title='Revenue Trend'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

    with c2:
        country_rev = filtered.groupby('Country')['Total_Revenue'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_country = px.bar(
            country_rev, x='Total_Revenue', y='Country',
            orientation='h', color='Total_Revenue',
            color_continuous_scale='Viridis',
            title='Top 10 Markets'
        )
        st.plotly_chart(fig_country, use_container_width=True)

    st.divider()

    # ── Section 3: Revenue by Seating Region ──
    st.subheader("💺 Seating Region Performance")
    
    region_order = ['Economy', 'High Economy', 'Premium', 'VIP']
    region_rev = filtered.groupby('Seating_Region').agg(
        Ticket=('Ticket_Revenue', 'sum'),
        Merchandise=('Merchandise_Spend', 'sum'),
        Drink=('Drink_Spend', 'sum'),
        Total=('Total_Revenue', 'sum'),
        Avg_Spend=('Total_Revenue', 'mean')
    ).reindex(region_order).dropna(subset=['Total']).reset_index()

    cr1, cr2 = st.columns(2)
    with cr1:
        fig_region_stack = px.bar(
            region_rev, x='Seating_Region', y=['Ticket', 'Merchandise', 'Drink'],
            barmode='stack',
            color_discrete_sequence=['#E63946', '#FFD166', '#118AB2'],
            title='Revenue Split by Region'
        )
        st.plotly_chart(fig_region_stack, use_container_width=True)
    with cr2:
        fig_avg_spend = px.bar(
            region_rev, x='Seating_Region', y='Avg_Spend',
            color='Avg_Spend', color_continuous_scale='Bluered',
            title='Avg Spend per Customer'
        )
        st.plotly_chart(fig_avg_spend, use_container_width=True)

    st.divider()

    # ── Pygwalker Revenue Explorer ──
    st.subheader("🔍 Revenue Deep Dive Explorer")
    renderer = StreamlitRenderer(filtered)
    renderer.explorer()

    if st.session_state.get('advanced_mode'):
        st.divider()
        st.subheader("🔬 Advanced Revenue Statistics")
        from scipy import stats
        
        # ANOVA: Total Revenue by Seating Region
        regions = filtered['Seating_Region'].unique()
        groups = [filtered[filtered['Seating_Region'] == r]['Total_Revenue'] for r in regions]
        f_stat, p_val = stats.f_oneway(*groups)
        sig_text = "significant" if p_val < 0.05 else "not significant"
        
        col_adv1, col_adv2 = st.columns(2)
        with col_adv1:
            ui.card(
                title="Regional Spend ANOVA",
                content=f"F-Statistic: **{f_stat:.2f}** (p={p_val:.4e}). The variance in spend between seating regions is **{sig_text}**.",
                description="Testing if seating tier pricing affects total spend significantly.",
                key="rev_adv_1"
            ).render()
        with col_adv2:
            ui.card(
                title="Market Concentration",
                content=f"The filtered dataset contains {len(filtered['Country'].unique())} countries. Top 3 markets contribute { (filtered.groupby('Country')['Total_Revenue'].sum().nlargest(3).sum() / filtered['Total_Revenue'].sum() * 100):.1f}% of filtered revenue.",
                description="Market Share Analysis",
                key="rev_adv_2"
            ).render()
        