import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    st.title("👥 Customer Analysis")
    st.markdown("Understand customer demographics, geographic distribution, spending patterns, and repeat visit behavior.")

    df = load_data()

    # ── Top KPIs ──
    k1, k2, k3, k4 = st.columns(4)
    total_customers = df['Customer_ID'].nunique()
    avg_tickets = df['Num_Tickets'].mean()
    repeat_rate = df['Repeat_Visit'].mean() * 100
    avg_age = df['Age'].mean()

    k1.metric("Total Customers", f"{total_customers:,}")
    k2.metric("Avg Tickets Purchased", f"{avg_tickets:.1f}")
    k3.metric("Repeat Visit Rate", f"{repeat_rate:.1f}%")
    k4.metric("Avg Customer Age", f"{avg_age:.0f} years")

    st.divider()

    # ── Section 1: Customers by Demographics ──
    st.subheader("📊 Customer Demographics")

    col_left, col_right = st.columns(2)

    with col_left:
        # Gender distribution
        gender_counts = df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig_gender = px.pie(
            gender_counts, values='Count', names='Gender',
            hole=0.4,
            title='Customers by Gender',
            color_discrete_sequence=['#3498db', '#e74c3c', '#2ecc71']
        )
        fig_gender.update_traces(textposition='inside', textinfo='percent+label+value')
        fig_gender.update_layout(showlegend=False, margin=dict(t=40, b=20))
        st.plotly_chart(fig_gender, use_container_width=True)

    with col_right:
        # Age group distribution
        age_counts = df['Age_Group'].value_counts().sort_index().reset_index()
        age_counts.columns = ['Age_Group', 'Count']
        fig_age = px.bar(
            age_counts, x='Age_Group', y='Count',
            color='Count',
            color_continuous_scale='Tealgrn',
            title='Customers by Age Group',
            text='Count'
        )
        fig_age.update_layout(showlegend=False, xaxis_title='Age Group', yaxis_title='Number of Customers')
        fig_age.update_traces(textposition='outside')
        st.plotly_chart(fig_age, use_container_width=True)

    st.divider()

    # ── Section 2: Customers by Geography ──
    st.subheader("🌍 Geographic Distribution")

    col_a, col_b = st.columns(2)

    with col_a:
        country_counts = df['Country'].value_counts().reset_index()
        country_counts.columns = ['Country', 'Count']
        fig_country = px.bar(
            country_counts.sort_values('Count', ascending=True),
            x='Count', y='Country',
            orientation='h',
            color='Count',
            color_continuous_scale='Blues',
            title='Customers by Country',
            text='Count'
        )
        fig_country.update_layout(showlegend=False, yaxis_title='', xaxis_title='Number of Customers')
        fig_country.update_traces(textposition='outside')
        st.plotly_chart(fig_country, use_container_width=True)

    with col_b:
        # Country + Seating Region breakdown
        country_region = df.groupby(['Country', 'Seating_Region'])['Customer_ID'].count().reset_index()
        country_region.columns = ['Country', 'Seating_Region', 'Count']
        region_order = ['Economy', 'High Economy', 'Premium', 'VIP']
        fig_cr = px.bar(
            country_region, x='Country', y='Count', color='Seating_Region',
            barmode='stack',
            category_orders={'Seating_Region': region_order},
            color_discrete_sequence=['#e74c3c', '#e67e22', '#3498db', '#2ecc71'],
            title='Customers by Country & Seating Region'
        )
        fig_cr.update_layout(
            xaxis_title='Country', yaxis_title='Number of Customers',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
        )
        st.plotly_chart(fig_cr, use_container_width=True)

    st.divider()

    # ── Section 3: Spending Patterns ──
    st.subheader("💰 Customer Spending Patterns")

    spend_by = st.selectbox(
        "Analyze spending by:",
        ['Age_Group', 'Gender', 'Country', 'Seating_Region'],
        key='cust_spend_by'
    )

    spend_stats = df.groupby(spend_by, observed=True).agg(
        Avg_Ticket_Spend=('Ticket_Revenue', 'mean'),
        Avg_Merch_Spend=('Merchandise_Spend', 'mean'),
        Avg_Drink_Spend=('Drink_Spend', 'mean'),
        Avg_Total_Spend=('Total_Revenue', 'mean')
    ).reset_index()

    fig_spend = px.bar(
        spend_stats, x=spend_by,
        y=['Avg_Ticket_Spend', 'Avg_Merch_Spend', 'Avg_Drink_Spend'],
        barmode='group',
        color_discrete_sequence=['#3498db', '#e67e22', '#9b59b6'],
        title=f'Average Spending Breakdown by {spend_by.replace("_", " ")}',
        labels={'value': 'Avg Spend (USD)', 'variable': 'Spend Type'}
    )
    fig_spend.update_layout(
        xaxis_title=spend_by.replace('_', ' '),
        yaxis_title='Avg Spend (USD)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_spend, use_container_width=True)

    st.divider()

    # ── Section 4: Tickets Purchased ──
    st.subheader("🎟️ Ticket Purchasing Behavior")

    col_c, col_d = st.columns(2)

    with col_c:
        ticket_dist = df['Num_Tickets'].value_counts().sort_index().reset_index()
        ticket_dist.columns = ['Tickets', 'Count']
        fig_tickets = px.bar(
            ticket_dist, x='Tickets', y='Count',
            color='Count',
            color_continuous_scale='Oranges',
            title='Distribution of Tickets Purchased per Transaction',
            text='Count'
        )
        fig_tickets.update_layout(showlegend=False, xaxis_title='Number of Tickets', yaxis_title='Transactions')
        fig_tickets.update_traces(textposition='outside')
        st.plotly_chart(fig_tickets, use_container_width=True)

    with col_d:
        avg_tickets_by_region = df.groupby('Seating_Region')['Num_Tickets'].mean().reindex(
            ['Economy', 'High Economy', 'Premium', 'VIP']
        ).reset_index()
        avg_tickets_by_region.columns = ['Seating_Region', 'Avg_Tickets']

        fig_avg_tick = px.bar(
            avg_tickets_by_region, x='Seating_Region', y='Avg_Tickets',
            color='Seating_Region',
            color_discrete_sequence=['#e74c3c', '#e67e22', '#3498db', '#2ecc71'],
            title='Avg Tickets per Transaction by Seating Region',
            text=avg_tickets_by_region['Avg_Tickets'].round(2)
        )
        fig_avg_tick.update_layout(showlegend=False, xaxis_title='Seating Region', yaxis_title='Avg Tickets')
        fig_avg_tick.update_traces(textposition='outside')
        st.plotly_chart(fig_avg_tick, use_container_width=True)

    st.divider()

    # ── Section 5: Repeat Visit Analysis ──
    st.subheader("🔄 Repeat Visit Rates")

    repeat_by = st.selectbox(
        "View repeat rate by:",
        ['Country', 'Seating_Region', 'Gender', 'Age_Group'],
        key='cust_repeat_by'
    )

    repeat_stats = df.groupby(repeat_by, observed=True).agg(
        Total=('Customer_ID', 'count'),
        Repeats=('Repeat_Visit', 'sum')
    ).reset_index()
    repeat_stats['Repeat_Rate'] = (repeat_stats['Repeats'] / repeat_stats['Total'] * 100).round(1)

    fig_repeat = px.bar(
        repeat_stats.sort_values('Repeat_Rate', ascending=False),
        x=repeat_by, y='Repeat_Rate',
        color='Repeat_Rate',
        color_continuous_scale='RdYlGn',
        title=f'Repeat Visit Rate by {repeat_by.replace("_", " ")}',
        text=repeat_stats.sort_values('Repeat_Rate', ascending=False)['Repeat_Rate'].apply(lambda x: f"{x}%")
    )
    fig_repeat.update_layout(showlegend=False, xaxis_title=repeat_by.replace('_', ' '), yaxis_title='Repeat Rate (%)', yaxis_range=[0, 100])
    fig_repeat.update_traces(textposition='outside')
    st.plotly_chart(fig_repeat, use_container_width=True)

    st.divider()

    # ── Section 6: Customer Spend Distribution (Box Plots) ──
    st.subheader("📦 Spend Distribution by Segment")

    box_segment = st.selectbox(
        "Segment:",
        ['Seating_Region', 'Gender', 'Country', 'Repeat_Label'],
        key='cust_box'
    )

    fig_box = px.box(
        df, x=box_segment, y='Total_Revenue',
        color=box_segment,
        title=f'Total Spend Distribution by {box_segment.replace("_", " ")}',
        points='outliers'
    )
    fig_box.update_layout(
        showlegend=False,
        xaxis_title=box_segment.replace('_', ' '),
        yaxis_title='Total Spend (USD)'
    )
    st.plotly_chart(fig_box, use_container_width=True)