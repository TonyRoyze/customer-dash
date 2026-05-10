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
    return df


def show():
    st.title("📊 Executive Overview")
    st.markdown("A high-level summary of venue performance, revenue, and customer experience.")

    df = load_data()

    # ── Row 1: Core KPIs (from challenge C. Measures and KPIs) ──
    st.subheader("🔑 Key Performance Indicators")
    k1, k2, k3, k4 = st.columns(4)

    total_ticket_rev = df['Ticket_Revenue'].sum()
    total_merch_rev = df['Merchandise_Spend'].sum()
    total_drink_rev = df['Drink_Spend'].sum()
    total_revenue = df['Total_Revenue'].sum()

    k1.metric("Total Ticket Revenue", f"${total_ticket_rev:,.0f}")
    k2.metric("Total Merchandise Revenue", f"${total_merch_rev:,.0f}")
    k3.metric("Total Drink Revenue", f"${total_drink_rev:,.0f}")
    k4.metric("Total Revenue", f"${total_revenue:,.0f}")

    k5, k6, k7, k8 = st.columns(4)

    avg_spend = df['Total_Revenue'].mean()
    repeat_rate = df['Repeat_Visit'].mean() * 100
    avg_satisfaction = df['Satisfaction_Score'].mean()
    avg_recommendation = df['Recommendation_Likelihood'].mean()

    k5.metric("Avg Spend per Customer", f"${avg_spend:,.2f}")
    k6.metric("Repeat Visit Rate", f"{repeat_rate:.1f}%")
    k7.metric("Avg Satisfaction Score", f"{avg_satisfaction:.1f} / 10")
    k8.metric("Avg Recommendation", f"{avg_recommendation:.1f} / 10")

    st.divider()

    # ── Row 2: Revenue Breakdown Donut + Top Countries Bar ──
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("💰 Revenue Breakdown")
        rev_data = pd.DataFrame({
            'Category': ['Ticket Revenue', 'Merchandise Revenue', 'Drink Revenue'],
            'Amount': [total_ticket_rev, total_merch_rev, total_drink_rev]
        })
        fig_donut = px.pie(
            rev_data, values='Amount', names='Category',
            hole=0.45,
            color_discrete_sequence=['#3498db', '#e67e22', '#9b59b6']
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_right:
        st.subheader("🌍 Revenue by Country")
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

    st.divider()

    # ── Row 3: Revenue by Seating Region + Repeat vs First-Time ──
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🎭 Revenue by Seating Region")
        region_order = ['Economy', 'High Economy', 'Premium', 'VIP']
        region_rev = df.groupby('Seating_Region')['Total_Revenue'].sum().reindex(region_order).reset_index()
        fig_region = px.bar(
            region_rev, x='Seating_Region', y='Total_Revenue',
            color='Seating_Region',
            color_discrete_sequence=['#e74c3c', '#e67e22', '#3498db', '#2ecc71'],
            text=region_rev['Total_Revenue'].apply(lambda x: f"${x:,.0f}")
        )
        fig_region.update_layout(showlegend=False, xaxis_title='Seating Region', yaxis_title='Revenue (USD)')
        fig_region.update_traces(textposition='outside')
        st.plotly_chart(fig_region, use_container_width=True)

    with col_b:
        st.subheader("🔄 Repeat vs First-Time Visitors")
        repeat_counts = df['Repeat_Label'].value_counts().reset_index()
        repeat_counts.columns = ['Visitor Type', 'Count']
        fig_repeat = px.pie(
            repeat_counts, values='Count', names='Visitor Type',
            hole=0.4,
            color_discrete_map={'Repeat': '#2ecc71', 'First-Time': '#e74c3c'}
        )
        fig_repeat.update_traces(textposition='inside', textinfo='percent+label+value')
        fig_repeat.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig_repeat, use_container_width=True)

    st.divider()

    # ── Row 4: Searchable Data Table ──
    st.subheader("📋 Transactions")
    search_query = st.text_input("🔍 Search across all columns", placeholder="e.g. CUST_0001, VIP, Australia...", key="overview_search")

    table_data = df.sort_values(by="Visit_Date", ascending=False)
    if search_query:
        mask = table_data.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False).any(), axis=1)
        table_data = table_data[mask]

    st.caption(f"Showing **{len(table_data):,}** of {len(df):,} records")
    st.dataframe(table_data, use_container_width=True, hide_index=True)