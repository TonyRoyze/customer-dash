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
    st.markdown("<h1><i class='bi bi-people'></i> Customer Analysis</h1>", unsafe_allow_html=True)
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

     # ── Top-level Experience KPIs ──
    col1, col2, col3, col4 = st.columns(4)
    avg_sat = df['Satisfaction_Score'].mean()
    avg_rec = df['Recommendation_Likelihood'].mean()
    high_sat_pct = (df['Satisfaction_Score'] >= 8).mean() * 100
    promoter_pct = (df['Recommendation_Likelihood'] >= 8).mean() * 100

    col1.metric("Avg Satisfaction", f"{avg_sat:.1f} / 10")
    col2.metric("Avg Recommendation", f"{avg_rec:.1f} / 10")
    col3.metric("High Satisfaction (≥8)", f"{high_sat_pct:.1f}%")
    col4.metric("Promoters (≥8)", f"{promoter_pct:.1f}%")

    st.divider()

    # ── Section 1: Customers by Demographics ──
    st.markdown("### <i class='bi bi-pie-chart'></i> Customer Demographics", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        # Gender distribution
        gender_counts = df['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig_gender = px.pie(
            gender_counts, values='Count', names='Gender',
            hole=0.4,
            title='Customers by Gender',
            color_discrete_sequence=['#118AB2', '#E63946', '#06D6A0']
        )
        fig_gender.update_traces(textposition='inside', textinfo='percent+label+value')
        fig_gender.update_layout(showlegend=False, margin=dict(t=40, b=20))
        st.plotly_chart(fig_gender, width="stretch")

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
        st.plotly_chart(fig_age, width="stretch")

    st.divider()

    # ── Section 2: Customers by Geography ──
    st.markdown("### <i class='bi bi-geo-alt'></i> Geographic Distribution", unsafe_allow_html=True)

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
        st.plotly_chart(fig_country, width="stretch")

    with col_b:
        # Country + Seating Region breakdown
        country_region = df.groupby(['Country', 'Seating_Region'])['Customer_ID'].count().reset_index()
        country_region.columns = ['Country', 'Seating_Region', 'Count']
        region_order = ['Economy', 'High Economy', 'Premium', 'VIP']
        fig_cr = px.bar(
            country_region, x='Country', y='Count', color='Seating_Region',
            barmode='stack',
            category_orders={'Seating_Region': region_order},
            color_discrete_sequence=['#073B4C', '#118AB2', '#FFD166', '#E63946'],
            title='Customers by Country & Seating Region'
        )
        fig_cr.update_layout(
            xaxis_title='Country', yaxis_title='Number of Customers',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, title_text='')
        )
        st.plotly_chart(fig_cr, width="stretch")

    st.divider()

    # ── Section 3: Spending Patterns ──
    st.markdown("### <i class='bi bi-wallet2'></i> Customer Spending Patterns", unsafe_allow_html=True)

    spend_by = st.selectbox(
        "Analyze spending by:",
        ['Seating_Region', 'Age_Group', 'Gender', 'Country'],
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
        color_discrete_sequence=['#E63946', '#FFD166', '#118AB2'],
        title=f'Average Spending Breakdown by {spend_by.replace("_", " ")}',
        labels={'value': 'Avg Spend (USD)', 'variable': ''}
    )
    fig_spend.update_layout(
        xaxis_title=spend_by.replace('_', ' '),
        yaxis_title='Avg Spend (USD)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    st.plotly_chart(fig_spend, width="stretch")

    st.divider()

    # ── Row 4: Repeat Rates & Spend Distribution ──
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown("### <i class='bi bi-arrow-repeat'></i> Repeat Visit Rates", unsafe_allow_html=True)
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
        st.plotly_chart(fig_repeat, width="stretch")

    with col_f:
        st.markdown("### <i class='bi bi-box-seam'></i> Spend Distribution by Segment", unsafe_allow_html=True)
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
        st.plotly_chart(fig_box, width="stretch")



    