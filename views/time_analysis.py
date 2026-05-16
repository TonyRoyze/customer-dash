import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    df['Month_dt'] = df['Visit_Date'].dt.to_period('M').dt.to_timestamp()
    df['Day_of_Week'] = df['Visit_Date'].dt.day_name()
    return df

def show():
    df = load_data()
    st.header("Time-Based Analysis")
    st.markdown("Analyze temporal patterns, seasonality, and visit frequency trends.")

    # ── Monthly Aggregations ──
    monthly = df.groupby('Month_dt').agg(
        Total_Revenue=('Total_Revenue', 'sum'),
        Ticket_Revenue=('Ticket_Revenue', 'sum'),
        Merch_Revenue=('Merchandise_Spend', 'sum'),
        Drink_Revenue=('Drink_Spend', 'sum'),
        Visitors=('Customer_ID', 'count'),
        Repeat_Visitors=('Repeat_Visit', 'sum')
    ).reset_index().sort_values('Month_dt')

    # ── Shadcn KPIs ──
    total_rev = df['Total_Revenue'].sum()
    total_vis = len(df)
    avg_month_rev = monthly['Total_Revenue'].mean()
    peak_month = monthly.loc[monthly['Total_Revenue'].idxmax(), 'Month_dt'].strftime('%B %Y')

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        ui.metric_card(title="Total Revenue", content=f"${total_rev:,.0f}", key="time_m1")
    with m2:
        ui.metric_card(title="Total Footfall", content=f"{total_vis:,}", key="time_m2")
    with m3:
        ui.metric_card(title="Avg Monthly Rev", content=f"${avg_month_rev:,.0f}", key="time_m3")
    with m4:
        ui.metric_card(title="Peak Period", content=peak_month, key="time_m4")

    st.divider()

    # ── Monthly Trends ──
    st.subheader("📈 Temporal Trends")
    t1, t2 = st.columns(2)

    with t1:
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Scatter(
            x=monthly['Month_dt'], y=monthly['Total_Revenue'],
            mode='lines+markers', name='Total Revenue',
            line=dict(color='#E63946', width=3)
        ))
        fig_rev.update_layout(title='Monthly Revenue Breakdown', xaxis_title='Month', yaxis_title='USD')
        st.plotly_chart(fig_rev, use_container_width=True)

    with t2:
        monthly['First_Time'] = monthly['Visitors'] - monthly['Repeat_Visitors']
        fig_visitors = go.Figure()
        fig_visitors.add_trace(go.Bar(x=monthly['Month_dt'], y=monthly['First_Time'], name='First-Time', marker_color='#E63946'))
        fig_visitors.add_trace(go.Bar(x=monthly['Month_dt'], y=monthly['Repeat_Visitors'], name='Repeat', marker_color='#06D6A0'))
        fig_visitors.update_layout(barmode='stack', title='Visitor Composition', xaxis_title='Month')
        st.plotly_chart(fig_visitors, use_container_width=True)

    st.divider()

    # ── Day of Week Analysis ──
    st.subheader("🗓️ Day of Week Performance")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_stats = df.groupby('Day_of_Week').agg(
        Visits=('Customer_ID', 'count'),
        Avg_Revenue=('Total_Revenue', 'mean')
    ).reindex(day_order).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig_day_visits = px.bar(
            day_stats, x='Day_of_Week', y='Visits',
            color='Visits', color_continuous_scale='Blues',
            title='Visits by Day'
        )
        st.plotly_chart(fig_day_visits, use_container_width=True)
    with c2:
        fig_day_rev = px.bar(
            day_stats, x='Day_of_Week', y='Avg_Revenue',
            color='Avg_Revenue', color_continuous_scale='Oranges',
            title='Avg Revenue by Day'
        )
        st.plotly_chart(fig_day_rev, use_container_width=True)

    st.divider()

    # ── Pygwalker Temporal Explorer ──
    st.subheader("📅 Temporal Data Explorer")
    st.markdown("Use the explorer below to slice and dice the venue data dynamically.")
    renderer = StreamlitRenderer(df)
    renderer.explorer()

    if st.session_state.get('advanced_mode'):
        st.divider()
        st.subheader("🔬 Advanced Temporal Statistics")
        from scipy import stats
        
        # T-Test: Weekend vs. Weekday Spend
        weekend_days = ['Saturday', 'Sunday']
        weekend_spend = df[df['Day_of_Week'].isin(weekend_days)]['Total_Revenue']
        weekday_spend = df[~df['Day_of_Week'].isin(weekend_days)]['Total_Revenue']
        t_stat, p_val = stats.ttest_ind(weekend_spend, weekday_spend)
        sig_text = "significant" if p_val < 0.05 else "not significant"
        
        col_adv1, col_adv2 = st.columns(2)
        with col_adv1:
            ui.card(
                title="Weekend Surge (T-Test)",
                content=f"T-Stat: **{t_stat:.2f}** (p={p_val:.4f}). The revenue difference between weekends and weekdays is **{sig_text}**.",
                description="Comparing operational performance by day category.",
                key="time_adv_1"
            ).render()
        with col_adv2:
            growth = ((monthly['Total_Revenue'].iloc[-1] / monthly['Total_Revenue'].iloc[0]) - 1) * 100
            ui.card(
                title="Overall Period Growth",
                content=f"Total revenue has grown by **{growth:.1f}%** from the first month to the last recorded month in the dataset.",
                description="Longitudinal Trend Analysis",
                key="time_adv_2"
            ).render()
