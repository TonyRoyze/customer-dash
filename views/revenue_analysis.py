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
        # ── Section 1: Revenue by Visit Date ──
        st.markdown("### <i class='bi bi-calendar3'></i> Revenue Over Time", unsafe_allow_html=True)

        monthly_rev = filtered.groupby(filtered['Visit_Date'].dt.to_period('M').dt.to_timestamp()).agg(
            Ticket=('Ticket_Revenue', 'sum'),
            Merchandise=('Merchandise_Spend', 'sum'),
            Drink=('Drink_Spend', 'sum')
        ).reset_index()
        monthly_rev.columns = ['Month', 'Ticket', 'Merchandise', 'Drink']

        fig_timeline = px.area(
            monthly_rev, x='Month', y=['Ticket', 'Merchandise', 'Drink'],
            color_discrete_sequence=['#E63946', '#FFD166', '#118AB2'],
            title='Monthly Revenue Breakdown (Stacked Area)'
        )
        fig_timeline.update_layout(
            xaxis_title='Month', yaxis_title='Revenue (USD)',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, title_text='')
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        if st.session_state.get('advanced_mode'):
            from scipy import stats
            import numpy as np
            
            # Time Series Metrics
            monthly_rev['Total'] = monthly_rev['Ticket'] + monthly_rev['Merchandise'] + monthly_rev['Drink']
            monthly_rev['MoM_Growth'] = monthly_rev['Total'].pct_change() * 100
            avg_mom = monthly_rev['MoM_Growth'].mean()
            volatility = (monthly_rev['Total'].std() / monthly_rev['Total'].mean()) * 100
            
            # Trend Test
            x_vals = np.arange(len(monthly_rev))
            y_vals = monthly_rev['Total']
            slope, intercept, r_val, p_val, stderr = stats.linregress(x_vals, y_vals)
            reg_sig = "✅ Significant" if p_val < 0.05 else "❌ Not Significant"
            
            st.table(pd.DataFrame({
                "Metric": ["Avg MoM Growth", "Revenue Volatility (CV)", "Trend Slope", "Trend Significance (p)"],
                "Value": [f"{avg_mom:+.1f}%", f"{volatility:.1f}%", f"${slope:,.2f}/mo", f"{p_val:.4e}"],
                "Status": ["-", "Higher = Less Stable", reg_sig, "p < 0.05 is significant"]
            }))

    with c2:
        # ── Section 2: Revenue by Country ──
        st.markdown("### <i class='bi bi-globe'></i> Revenue by Country", unsafe_allow_html=True)
        country_rev = filtered.groupby('Country').agg(
            Ticket=('Ticket_Revenue', 'sum'),
            Merchandise=('Merchandise_Spend', 'sum'),
            Drink=('Drink_Spend', 'sum'),
            Total=('Total_Revenue', 'sum')
        ).sort_values('Total', ascending=False).reset_index()

        fig_country = px.bar(
            country_rev, x='Country', y=['Ticket', 'Merchandise', 'Drink'],
            barmode='stack',
            color_discrete_sequence=['#E63946', '#FFD166', '#118AB2'],
            title='Revenue Breakdown by Country',
            labels={'value': 'Revenue (USD)', 'variable': ''}
        )
        fig_country.update_layout(
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, title_text='')
        )
        st.plotly_chart(fig_country, use_container_width=True)

        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # ANOVA (Country)
            country_groups = [filtered[filtered['Country'] == c]['Total_Revenue'] for c in filtered['Country'].unique()]
            if len(country_groups) > 1:
                f_stat, f_p = stats.f_oneway(*country_groups)
                f_sig = "✅ Significant" if f_p < 0.05 else "❌ Not Significant"
                st.table(pd.DataFrame({
                    "Statistical Test": ["One-Way ANOVA (Market)"],
                    "F-Stat": [f"{f_stat:.2f}"],
                    "P-Value": [f"{f_p:.4e}"],
                    "Significance": [f_sig]
                }))

    st.divider()

    # ── Section 3: Revenue by Seating Region ──
    st.subheader("💺 Seating Region Performance")
    
    region_order = ['Economy', 'High Economy', 'Premium', 'VIP']
    region_rev = filtered.groupby('Seating_Region').agg(
        Ticket=('Ticket_Revenue', 'sum'),
        Merchandise=('Merchandise_Spend', 'sum'),
        Drink=('Drink_Spend', 'sum'),
        Total=('Total_Revenue', 'sum'),
        Customers=('Customer_ID', 'count'),
        Avg_Spend=('Total_Revenue', 'mean')
    ).reindex(region_order).dropna(subset=['Total']).reset_index()

    cr1, cr2 = st.columns(2)
    with cr1:
        fig_region_stack = px.bar(
            region_rev, x='Seating_Region', y=['Ticket', 'Merchandise', 'Drink'],
            barmode='stack',
            color_discrete_sequence=['#E63946', '#FFD166', '#118AB2'],
            title='Stacked Revenue by Seating Region'
        )
        fig_region_stack.update_layout(
            xaxis_title='Seating Region', yaxis_title='Revenue (USD)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, title_text='')
        )
        st.plotly_chart(fig_region_stack, use_container_width=True)
        
    with cr2:
        fig_avg_spend = px.bar(
            region_rev, x='Seating_Region', y='Avg_Spend',
            color='Avg_Spend',
            color_continuous_scale='Bluered',
            title='Avg Spend per Customer by Seating Region',
            text=region_rev['Avg_Spend'].round(0).fillna(0).astype(int)
        )
        fig_avg_spend.update_layout(showlegend=False, yaxis_title='Avg Spend (USD)')
        fig_avg_spend.update_traces(textposition='outside')
        st.plotly_chart(fig_avg_spend, use_container_width=True)

        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # ANOVA (Seating Region Total Spend)
            region_groups = [filtered[filtered['Seating_Region'] == r]['Total_Revenue'] for r in filtered['Seating_Region'].unique()]
            f_stat, f_p = stats.f_oneway(*region_groups)
            f_sig = "✅ Significant" if f_p < 0.05 else "❌ Not Significant"
            
            # Chi-Square Independence (Revenue Mix vs Seating Region)
            # We aggregate the sums of each category by region
            mix_data = region_rev[['Seating_Region', 'Ticket', 'Merchandise', 'Drink']].set_index('Seating_Region')
            chi2_mix, p_mix, dof_mix, ex_mix = stats.chi2_contingency(mix_data)
            mix_sig = "✅ Mix Varies by Tier" if p_mix < 0.05 else "❌ Uniform Mix"
            
            st.table(pd.DataFrame({
                "Test": ["ANOVA (Total Spend)", "Chi2 (Revenue Mix)"],
                "Stat": [f"F={f_stat:.2f}", f"Chi2={chi2_mix:.2f}"],
                "P-Value": [f"{f_p:.4e}", f"{p_mix:.4e}"],
                "Result": [f_sig, mix_sig]
            }))

    st.divider()

    # Filter for revenue-relevant columns
    rev_cols = ['Visit_Date', 'Country', 'Seating_Region', 'Total_Revenue', 'Ticket_Revenue', 
                'Merchandise_Spend', 'Drink_Spend', 'Repeat_Label']
    renderer = StreamlitRenderer(filtered[rev_cols])
    renderer.explorer()
