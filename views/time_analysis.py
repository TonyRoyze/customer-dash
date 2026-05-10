import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw.csv')

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df['Visit_Date'] = pd.to_datetime(df['Visit_Date'])
    df['Ticket_Revenue'] = df['Ticket_Price'] * df['Num_Tickets']
    df['Total_Revenue'] = df['Ticket_Revenue'] + df['Merchandise_Spend'] + df['Drink_Spend']
    df['Month'] = df['Visit_Date'].dt.to_period('M').astype(str)
    df['Month_dt'] = df['Visit_Date'].dt.to_period('M').dt.to_timestamp()
    df['Week'] = df['Visit_Date'].dt.isocalendar().week.astype(int)
    df['Day_of_Week'] = df['Visit_Date'].dt.day_name()
    df['Repeat_Label'] = df['Repeat_Visit'].map({1: 'Repeat', 0: 'First-Time'})
    return df


def show():
    st.title("📅 Time-Based Analysis")
    st.markdown("Explore revenue trends, visit patterns, and customer behavior over time.")

    df = load_data()

    # ── Monthly KPI Summary ──
    monthly = df.groupby('Month_dt').agg(
        Total_Revenue=('Total_Revenue', 'sum'),
        Ticket_Revenue=('Ticket_Revenue', 'sum'),
        Merch_Revenue=('Merchandise_Spend', 'sum'),
        Drink_Revenue=('Drink_Spend', 'sum'),
        Visitors=('Customer_ID', 'count'),
        Avg_Satisfaction=('Satisfaction_Score', 'mean'),
        Repeat_Visitors=('Repeat_Visit', 'sum')
    ).reset_index().sort_values('Month_dt')

    # Top-level KPIs
    col1, col2, col3, col4 = st.columns(4)
    total_rev = df['Total_Revenue'].sum()
    total_visitors = len(df)
    avg_monthly_rev = monthly['Total_Revenue'].mean()
    peak_month = monthly.loc[monthly['Total_Revenue'].idxmax(), 'Month_dt'].strftime('%B %Y')

    col1.metric("Total Revenue", f"${total_rev:,.0f}")
    col2.metric("Total Visitors", f"{total_visitors:,}")
    col3.metric("Avg Monthly Revenue", f"${avg_monthly_rev:,.0f}")
    col4.metric("Peak Revenue Month", peak_month)

    st.divider()

    # ── Section 1: Monthly Revenue Trend ──
    st.subheader("📈 Monthly Revenue Trend")

    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Total_Revenue'],
        mode='lines+markers', name='Total Revenue',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8)
    ))
    fig_rev.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Ticket_Revenue'],
        mode='lines+markers', name='Ticket Revenue',
        line=dict(color='#2ecc71', width=2, dash='dot'),
        marker=dict(size=6)
    ))
    fig_rev.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Merch_Revenue'],
        mode='lines+markers', name='Merchandise Revenue',
        line=dict(color='#e67e22', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    fig_rev.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Drink_Revenue'],
        mode='lines+markers', name='Drink Revenue',
        line=dict(color='#9b59b6', width=2, dash='dashdot'),
        marker=dict(size=6)
    ))
    fig_rev.update_layout(
        title='Monthly Revenue Breakdown',
        xaxis_title='Month',
        yaxis_title='Revenue (USD)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_rev, use_container_width=True)

    st.divider()

    # ── Section 2: Revenue Composition (Stacked Area) ──
    st.subheader("🧩 Revenue Composition Over Time")

    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Ticket_Revenue'],
        mode='lines', name='Ticket Revenue',
        stackgroup='one', line=dict(color='#3498db')
    ))
    fig_area.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Merch_Revenue'],
        mode='lines', name='Merchandise Revenue',
        stackgroup='one', line=dict(color='#e67e22')
    ))
    fig_area.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Drink_Revenue'],
        mode='lines', name='Drink Revenue',
        stackgroup='one', line=dict(color='#9b59b6')
    ))
    fig_area.update_layout(
        title='Revenue Composition (Stacked)',
        xaxis_title='Month',
        yaxis_title='Revenue (USD)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_area, use_container_width=True)

    st.divider()

    # ── Section 3: Monthly Visitor Count & Repeat Rate ──
    st.subheader("👥 Monthly Visitors & Repeat Visit Rate")

    monthly['Repeat_Rate'] = (monthly['Repeat_Visitors'] / monthly['Visitors'] * 100).round(1)

    fig_visitors = go.Figure()
    fig_visitors.add_trace(go.Bar(
        x=monthly['Month_dt'], y=monthly['Visitors'],
        name='Total Visitors',
        marker_color='#3498db',
        text=monthly['Visitors'],
        textposition='outside'
    ))
    fig_visitors.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Repeat_Rate'],
        name='Repeat Rate (%)',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8)
    ))
    fig_visitors.update_layout(
        title='Monthly Visitors with Repeat Rate Overlay',
        xaxis_title='Month',
        yaxis=dict(title='Number of Visitors'),
        yaxis2=dict(
            title='Repeat Rate (%)',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_visitors, use_container_width=True)

    st.divider()

    # ── Section 4: Day-of-Week Patterns ──
    st.subheader("📆 Visit & Revenue Patterns by Day of Week")

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_stats = df.groupby('Day_of_Week').agg(
        Visits=('Customer_ID', 'count'),
        Avg_Revenue=('Total_Revenue', 'mean'),
        Avg_Satisfaction=('Satisfaction_Score', 'mean')
    ).reindex(day_order).reset_index()

    col_left, col_right = st.columns(2)

    with col_left:
        fig_day_visits = px.bar(
            day_stats, x='Day_of_Week', y='Visits',
            color='Visits',
            color_continuous_scale='Blues',
            title='Visit Count by Day of Week',
            text='Visits'
        )
        fig_day_visits.update_layout(showlegend=False)
        fig_day_visits.update_traces(textposition='outside')
        st.plotly_chart(fig_day_visits, use_container_width=True)

    with col_right:
        fig_day_rev = px.bar(
            day_stats, x='Day_of_Week', y='Avg_Revenue',
            color='Avg_Revenue',
            color_continuous_scale='Oranges',
            title='Avg Revenue per Customer by Day',
            text=day_stats['Avg_Revenue'].round(0)
        )
        fig_day_rev.update_layout(showlegend=False, yaxis_title='Avg Revenue (USD)')
        fig_day_rev.update_traces(textposition='outside')
        st.plotly_chart(fig_day_rev, use_container_width=True)

    st.divider()

    # ── Section 5: Monthly Revenue by Seating Region ──
    st.subheader("🎭 Monthly Revenue by Seating Region")

    monthly_region = df.groupby([df['Visit_Date'].dt.to_period('M').dt.to_timestamp(), 'Seating_Region']).agg(
        Revenue=('Total_Revenue', 'sum')
    ).reset_index()
    monthly_region.columns = ['Month', 'Seating_Region', 'Revenue']

    region_order = ['Economy', 'High Economy', 'Premium', 'VIP']
    fig_region = px.line(
        monthly_region, x='Month', y='Revenue',
        color='Seating_Region',
        markers=True,
        title='Revenue Over Time by Seating Region',
        category_orders={'Seating_Region': region_order},
        color_discrete_sequence=['#e74c3c', '#e67e22', '#3498db', '#2ecc71']
    )
    fig_region.update_layout(
        xaxis_title='Month',
        yaxis_title='Revenue (USD)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_region, use_container_width=True)

    st.divider()

    # ── Section 6: Monthly Satisfaction Trend ──
    st.subheader("😊 Monthly Satisfaction & Recommendation Trend")

    fig_sat_trend = go.Figure()
    fig_sat_trend.add_trace(go.Scatter(
        x=monthly['Month_dt'], y=monthly['Avg_Satisfaction'].round(2),
        mode='lines+markers', name='Avg Satisfaction',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=8)
    ))

    monthly_rec = df.groupby('Month_dt')['Recommendation_Likelihood'].mean().reset_index()
    monthly_rec = monthly_rec.sort_values('Month_dt')

    fig_sat_trend.add_trace(go.Scatter(
        x=monthly_rec['Month_dt'], y=monthly_rec['Recommendation_Likelihood'].round(2),
        mode='lines+markers', name='Avg Recommendation',
        line=dict(color='#9b59b6', width=3),
        marker=dict(size=8)
    ))
    fig_sat_trend.update_layout(
        title='Monthly Average Satisfaction & Recommendation',
        xaxis_title='Month',
        yaxis_title='Score',
        yaxis_range=[0, 10],
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_sat_trend, use_container_width=True)
