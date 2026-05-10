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
    st.title("💵 Revenue Analysis")
    st.markdown("Analyze total ticket revenue, merchandise revenue, drink revenue, and overall revenue across segments.")

    df = load_data()

    # ── Filters ──
    with st.expander("🔍 Filters", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            countries = ['All'] + sorted(df['Country'].unique().tolist())
            sel_country = st.selectbox("Country", countries, key="rev_country")
        with fc2:
            regions = ['All'] + sorted(df['Seating_Region'].unique().tolist())
            sel_region = st.selectbox("Seating Region", regions, key="rev_region")
        with fc3:
            visitor_types = ['All', 'Repeat', 'First-Time']
            sel_visitor = st.selectbox("Visitor Type", visitor_types, key="rev_visitor")

    # Apply filters
    filtered = df.copy()
    if sel_country != 'All':
        filtered = filtered[filtered['Country'] == sel_country]
    if sel_region != 'All':
        filtered = filtered[filtered['Seating_Region'] == sel_region]
    if sel_visitor != 'All':
        filtered = filtered[filtered['Repeat_Label'] == sel_visitor]

    st.caption(f"Showing **{len(filtered):,}** of {len(df):,} records")

    # ── KPIs for filtered data ──
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ticket Revenue", f"${filtered['Ticket_Revenue'].sum():,.0f}")
    k2.metric("Merchandise Revenue", f"${filtered['Merchandise_Spend'].sum():,.0f}")
    k3.metric("Drink Revenue", f"${filtered['Drink_Spend'].sum():,.0f}")
    k4.metric("Total Revenue", f"${filtered['Total_Revenue'].sum():,.0f}")

    st.divider()

    # ── Section 1: Revenue by Country ──
    st.subheader("🌍 Revenue by Country")
    country_rev = filtered.groupby('Country').agg(
        Ticket=('Ticket_Revenue', 'sum'),
        Merchandise=('Merchandise_Spend', 'sum'),
        Drink=('Drink_Spend', 'sum'),
        Total=('Total_Revenue', 'sum')
    ).sort_values('Total', ascending=False).reset_index()

    fig_country = px.bar(
        country_rev, x='Country', y=['Ticket', 'Merchandise', 'Drink'],
        barmode='stack',
        color_discrete_sequence=['#3498db', '#e67e22', '#9b59b6'],
        title='Revenue Breakdown by Country',
        labels={'value': 'Revenue (USD)', 'variable': 'Revenue Type'}
    )
    fig_country.update_layout(
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_country, use_container_width=True)

    st.divider()

    # ── Section 2: Revenue by Seating Region ──
    st.subheader("🎭 Revenue by Seating Region")

    region_order = ['Economy', 'High Economy', 'Premium', 'VIP']
    region_rev = filtered.groupby('Seating_Region').agg(
        Ticket=('Ticket_Revenue', 'sum'),
        Merchandise=('Merchandise_Spend', 'sum'),
        Drink=('Drink_Spend', 'sum'),
        Total=('Total_Revenue', 'sum'),
        Customers=('Customer_ID', 'count'),
        Avg_Spend=('Total_Revenue', 'mean')
    ).reindex(region_order).dropna(subset=['Total']).reset_index()

    col_left, col_right = st.columns(2)

    with col_left:
        fig_region_stack = px.bar(
            region_rev, x='Seating_Region', y=['Ticket', 'Merchandise', 'Drink'],
            barmode='stack',
            color_discrete_sequence=['#3498db', '#e67e22', '#9b59b6'],
            title='Stacked Revenue by Seating Region'
        )
        fig_region_stack.update_layout(
            xaxis_title='Seating Region', yaxis_title='Revenue (USD)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
        )
        st.plotly_chart(fig_region_stack, use_container_width=True)

    with col_right:
        fig_avg_spend = px.bar(
            region_rev, x='Seating_Region', y='Avg_Spend',
            color='Avg_Spend',
            color_continuous_scale='Bluered',
            title='Avg Spend per Customer by Region',
            text=region_rev['Avg_Spend'].round(0).fillna(0).astype(int)
        )
        fig_avg_spend.update_layout(showlegend=False, yaxis_title='Avg Spend (USD)')
        fig_avg_spend.update_traces(textposition='outside')
        st.plotly_chart(fig_avg_spend, use_container_width=True)

    st.divider()

    # ── Section 3: Revenue by Age Group ──
    st.subheader("👤 Revenue by Customer Age Group")

    age_rev = filtered.groupby('Age_Group', observed=True).agg(
        Total_Revenue=('Total_Revenue', 'sum'),
        Avg_Spend=('Total_Revenue', 'mean'),
        Customers=('Customer_ID', 'count')
    ).reset_index()

    col_c, col_d = st.columns(2)
    with col_c:
        fig_age_rev = px.bar(
            age_rev, x='Age_Group', y='Total_Revenue',
            color='Total_Revenue',
            color_continuous_scale='Tealgrn',
            title='Total Revenue by Age Group',
            text=age_rev['Total_Revenue'].apply(lambda x: f"${x:,.0f}")
        )
        fig_age_rev.update_layout(showlegend=False, xaxis_title='Age Group', yaxis_title='Revenue (USD)')
        fig_age_rev.update_traces(textposition='outside')
        st.plotly_chart(fig_age_rev, use_container_width=True)

    with col_d:
        fig_age_avg = px.bar(
            age_rev, x='Age_Group', y='Avg_Spend',
            color='Avg_Spend',
            color_continuous_scale='Purp',
            title='Avg Spend per Customer by Age Group',
            text=age_rev['Avg_Spend'].apply(lambda x: f"${x:,.0f}")
        )
        fig_age_avg.update_layout(showlegend=False, xaxis_title='Age Group', yaxis_title='Avg Spend (USD)')
        fig_age_avg.update_traces(textposition='outside')
        st.plotly_chart(fig_age_avg, use_container_width=True)

    st.divider()

    # ── Section 4: Repeat vs First-Time Revenue ──
    st.subheader("🔄 Revenue: Repeat vs First-Time Visitors")

    repeat_rev = filtered.groupby('Repeat_Label').agg(
        Total_Revenue=('Total_Revenue', 'sum'),
        Avg_Spend=('Total_Revenue', 'mean'),
        Customers=('Customer_ID', 'count')
    ).reset_index()

    col_e, col_f = st.columns(2)
    with col_e:
        fig_repeat_rev = px.pie(
            repeat_rev, values='Total_Revenue', names='Repeat_Label',
            hole=0.4,
            title='Revenue Share: Repeat vs First-Time',
            color_discrete_map={'Repeat': '#2ecc71', 'First-Time': '#e74c3c'}
        )
        fig_repeat_rev.update_traces(textposition='inside', textinfo='percent+label+value')
        st.plotly_chart(fig_repeat_rev, use_container_width=True)

    with col_f:
        fig_repeat_avg = go.Figure()
        fig_repeat_avg.add_trace(go.Bar(
            x=repeat_rev['Repeat_Label'], y=repeat_rev['Avg_Spend'],
            marker_color=['#e74c3c', '#2ecc71'],
            text=repeat_rev['Avg_Spend'].round(2),
            textposition='outside'
        ))
        fig_repeat_avg.update_layout(
            title='Avg Spend per Customer: Repeat vs First-Time',
            yaxis_title='Avg Spend (USD)'
        )
        st.plotly_chart(fig_repeat_avg, use_container_width=True)

    st.divider()

    # ── Section 5: Revenue by Visit Date ──
    st.subheader("📅 Revenue Over Time")

    monthly_rev = filtered.groupby(filtered['Visit_Date'].dt.to_period('M').dt.to_timestamp()).agg(
        Ticket=('Ticket_Revenue', 'sum'),
        Merchandise=('Merchandise_Spend', 'sum'),
        Drink=('Drink_Spend', 'sum')
    ).reset_index()
    monthly_rev.columns = ['Month', 'Ticket', 'Merchandise', 'Drink']

    fig_timeline = px.area(
        monthly_rev, x='Month', y=['Ticket', 'Merchandise', 'Drink'],
        color_discrete_sequence=['#3498db', '#e67e22', '#9b59b6'],
        title='Monthly Revenue Breakdown (Stacked Area)'
    )
    fig_timeline.update_layout(
        xaxis_title='Month', yaxis_title='Revenue (USD)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_timeline, use_container_width=True)