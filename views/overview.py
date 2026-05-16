import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import plotly.express as px
import plotly.graph_objects as go
from pygwalker.api.streamlit import StreamlitRenderer
import utils

def show():
    df = utils.load_dashboard_data()
    model_results = utils.get_model_results()
    
    st.header("Executive Overview")
    st.markdown("A modern summary of venue performance and customer metrics.")

    # ── Shadcn Metric Cards ──
    total_ticket_rev = df['Ticket_Revenue'].sum()
    total_merch_rev = df['Merchandise_Spend'].sum()
    total_drink_rev = df['Drink_Spend'].sum()
    total_rev = df['Total_Revenue'].sum()
    
    avg_spend = df['Total_Revenue'].mean()
    repeat_rate = df['Repeat_Visit'].mean() * 100
    avg_sat = df['Satisfaction_Score'].mean()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        ui.metric_card(title="Total Revenue", content=f"${total_rev:,.0f}", description="Cumulative venue earnings", key="m1")
    with m2:
        ui.metric_card(title="Avg Customer Spend", content=f"${avg_spend:,.2f}", description="Per transaction average", key="m2")
    with m3:
        ui.metric_card(title="Repeat Visit Rate", content=f"{repeat_rate:.1f}%", description="Loyalty metric", key="m3")
    with m4:
        ui.metric_card(title="Avg Satisfaction", content=f"{avg_sat:.1f}/10", description="Customer feedback score", key="m4")

    st.divider()

    # ── Row 2: Revenue Breakdown Donut + Top Countries Bar ──
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### <i class='bi bi-cash-stack'></i> Revenue Breakdown", unsafe_allow_html=True)
        rev_data = pd.DataFrame({
            'Category': ['Ticket Revenue', 'Merchandise Revenue', 'Drink Revenue'],
            'Amount': [total_ticket_rev, total_merch_rev, total_drink_rev]
        })
        fig_donut = px.pie(
            rev_data, values='Amount', names='Category',
            hole=0.45,
            color_discrete_sequence=['#E63946', '#FFD166', '#118AB2']
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig_donut, use_container_width=True)
        
        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # Chi-Square Goodness of Fit (Is there a significant difference between revenue streams?)
            chi_stat, chi_p = stats.chisquare(rev_data['Amount'])
            chi_sig = "✅ Significant" if chi_p < 0.05 else "❌ Not Significant"
            
            st.table(pd.DataFrame({
                "Statistical Test": ["Chi-Square Goodness of Fit"],
                "Statistic": [f"{chi_stat:.2f}"],
                "P-Value": [f"{chi_p:.4e}"],
                "Significance": [chi_sig]
            }))

    with col_right:
        st.markdown("### <i class='bi bi-globe'></i> Revenue by Country", unsafe_allow_html=True)
        country_rev = df.groupby('Country')['Total_Revenue'].sum().sort_values(ascending=True).reset_index()
        fig_country = px.bar(
            country_rev, x='Total_Revenue', y='Country',
            orientation='h',
            color='Total_Revenue',
            color_continuous_scale='Tealgrn',
            text=country_rev['Total_Revenue'].apply(lambda x: f"${x:,.0f}")
        )
        fig_country.update_layout(showlegend=False, margin=dict(t=20, b=20), yaxis_title='', xaxis_title='Revenue (USD)')
        fig_country.update_traces(textposition='outside')
        st.plotly_chart(fig_country, use_container_width=True)
        
        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # ANOVA (Is there a significant difference in revenue across countries?)
            country_groups = [df[df['Country'] == c]['Total_Revenue'] for c in df['Country'].unique()]
            f_stat, f_p = stats.f_oneway(*country_groups)
            f_sig = "✅ Significant" if f_p < 0.05 else "❌ Not Significant"
            
            st.table(pd.DataFrame({
                "Statistical Test": ["One-Way ANOVA (Country)"],
                "Statistic": [f"{f_stat:.2f}"],
                "P-Value": [f"{f_p:.4e}"],
                "Significance": [f_sig]
            }))
    st.divider()

    st.markdown("### <i class='bi bi-graph-up-arrow'></i> Monthly Revenue Trend", unsafe_allow_html=True)
    monthly = df.groupby('Month_dt').agg(
        Total_Revenue=('Total_Revenue', 'sum'),
        Ticket_Revenue=('Ticket_Revenue', 'sum'),
        Merch_Revenue=('Merchandise_Spend', 'sum'),
        Drink_Revenue=('Drink_Spend', 'sum')
    ).reset_index().sort_values('Month_dt')

    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Total_Revenue'],
        mode='lines+markers', name='Total Revenue',
        line=dict(color='#E63946', width=3),
        marker=dict(size=8)
    ))
    fig_rev.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Ticket_Revenue'],
        mode='lines+markers', name='Ticket Revenue',
        line=dict(color='#06D6A0', width=2, dash='dot'),
        marker=dict(size=6)
    ))
    fig_rev.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Merch_Revenue'],
        mode='lines+markers', name='Merchandise Revenue',
        line=dict(color='#FFD166', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    fig_rev.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Drink_Revenue'],
        mode='lines+markers', name='Drink Revenue',
        line=dict(color='#118AB2', width=2, dash='dashdot'),
        marker=dict(size=6)
    ))
    fig_rev.update_layout(
        title='Monthly Revenue Breakdown',
        xaxis_title='Month',
        yaxis_title='Revenue (USD)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, title_text='')
    )
    st.plotly_chart(fig_rev, use_container_width=True)

    if st.session_state.get('advanced_mode'):
        from scipy import stats
        import numpy as np
        
        # Time Series Metrics
        monthly['MoM_Growth'] = monthly['Total_Revenue'].pct_change() * 100
        avg_mom = monthly['MoM_Growth'].mean()
        volatility = (monthly['Total_Revenue'].std() / monthly['Total_Revenue'].mean()) * 100
        
        # Trend Test
        x_vals = np.arange(len(monthly))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, monthly['Total_Revenue'])
        reg_sig = "✅ Significant" if p_value < 0.05 else "❌ Not Significant"
        
        st.table(pd.DataFrame({
            "Metric": ["Avg MoM Growth", "Revenue Volatility (CV)", "Trend Slope", "Trend Significance (p)"],
            "Value": [f"{avg_mom:+.1f}%", f"{volatility:.1f}%", f"${slope:,.2f}/mo", f"{p_value:.4e}"],
            "Status": ["-", "Higher = Less Stable", reg_sig, "p < 0.05 is significant"]
        }))

    st.divider()

    # ── Pygwalker for Interactive Exploration ──
    # Filter for overview-relevant columns
    ov_cols = ['Visit_Date', 'Country', 'Total_Revenue', 'Ticket_Revenue', 'Merchandise_Spend', 
               'Drink_Spend', 'Satisfaction_Score', 'Repeat_Visit', 'Seating_Region']
    renderer = StreamlitRenderer(df[ov_cols], theme='streamlit')
    renderer.explorer()

    # ── Advanced Insights (Shadcn Alert/Card-like) ──
    if st.session_state.get('advanced_mode'):
        st.subheader("🔬 Advanced Statistical Insights")
        from scipy import stats
        
        col_s1, col_s2 = st.columns(2)
        
        # 1. Correlation Test: Satisfaction vs. Spend
        corr, p_val = stats.pearsonr(df['Satisfaction_Score'], df['Total_Revenue'])
        sig_text = "statistically significant" if p_val < 0.05 else "not statistically significant"
        
        with col_s1:
            ui.card(
                title="Satisfaction-Spend Correlation",
                content=f"Pearson Correlation: **{corr:.3f}** (p={p_val:.4f}). This relationship is **{sig_text}**.",
                description="Analysis of how customer feedback relates to monetary value.",
                key="c1"
            ).render()
            
        # 2. T-Test: Repeat vs First-Time Spend
        repeat_spend = df[df['Repeat_Visit'] == 1]['Total_Revenue']
        first_spend = df[df['Repeat_Visit'] == 0]['Total_Revenue']
        t_stat, t_p = stats.ttest_ind(repeat_spend, first_spend)
        t_sig = "significant difference" if t_p < 0.05 else "no significant difference"
        
        with col_s2:
            ui.card(
                title="Loyalty Spend Variance",
                content=f"T-Statistic: **{t_stat:.2f}** (p={t_p:.4f}). There is **{t_sig}** in spending between repeat and first-time guests.",
                description="Comparing the economic impact of customer retention.",
                key="c2"
            ).render()

    st.divider()

    # ── Searchable Data (Shadcn Table-like) ──
    st.subheader("📑 Transactional Deep Dive")
    search_query = st.text_input("Search transactions...", placeholder="Customer ID, Country, Seating...", key="overview_search")
    
    table_data = df.sort_values(by="Visit_Date", ascending=False)
    if search_query:
        mask = table_data.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False).any(), axis=1)
        table_data = table_data[mask]

    st.dataframe(table_data, use_container_width=True, hide_index=True)