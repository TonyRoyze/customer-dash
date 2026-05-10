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
    df['Month_dt'] = df['Visit_Date'].dt.to_period('M').dt.to_timestamp()
    df['Repeat_Label'] = df['Repeat_Visit'].map({1: 'Repeat', 0: 'First-Time'})
    return df


def show():
    st.markdown("<h1><i class='bi bi-speedometer2'></i> Executive Overview</h1>", unsafe_allow_html=True)
    st.markdown("A high-level summary of venue performance, revenue, and customer experience.")

    df = load_data()
    
    # Calculate monthly trends for the overview chart
    monthly = df.groupby('Month_dt').agg(
        Total_Revenue=('Total_Revenue', 'sum'),
        Ticket_Revenue=('Ticket_Revenue', 'sum'),
        Merch_Revenue=('Merchandise_Spend', 'sum'),
        Drink_Revenue=('Drink_Spend', 'sum')
    ).reset_index().sort_values('Month_dt')

    # ── Row 1: Core KPIs (from challenge C. Measures and KPIs) ──
    st.markdown("### <i class='bi bi-key'></i> Key Performance Indicators", unsafe_allow_html=True)
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
        st.plotly_chart(fig_donut, width="stretch")

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
        st.plotly_chart(fig_country, width="stretch")

    st.divider()

    st.markdown("### <i class='bi bi-graph-up-arrow'></i> Monthly Revenue Trend", unsafe_allow_html=True)
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
    st.plotly_chart(fig_rev, width="stretch")

    st.divider()


    # ── Row 3: Searchable Data Table ──
    st.markdown("### <i class='bi bi-list-ul'></i> Transactions", unsafe_allow_html=True)
    search_query = st.text_input("Search across all columns", placeholder="e.g. CUST_0001, VIP, Australia...", key="overview_search")

    table_data = df.sort_values(by="Visit_Date", ascending=False)
    if search_query:
        mask = table_data.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False).any(), axis=1)
        table_data = table_data[mask]

    st.caption(f"Showing **{len(table_data):,}** of {len(df):,} records")
    st.dataframe(table_data, width="stretch", hide_index=True)