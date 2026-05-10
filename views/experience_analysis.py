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
    df['Total_Spend'] = (df['Ticket_Price'] * df['Num_Tickets']) + df['Merchandise_Spend'] + df['Drink_Spend']
    df['Repeat_Label'] = df['Repeat_Visit'].map({1: 'Repeat', 0: 'First-Time'})
    # Age groups for segmentation
    bins = [0, 25, 35, 45, 55, 65, 100]
    labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
    df['Age_Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=True)
    return df


def show():
    st.markdown("<h1><i class='bi bi-star'></i> Experience Analysis</h1>", unsafe_allow_html=True)
    st.markdown("Explore customer satisfaction and recommendation patterns across different segments.")

    df = load_data()

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

    # ── Section 1: Satisfaction & Recommendation by Segment ──
    st.markdown("### <i class='bi bi-graph-up'></i> Satisfaction & Recommendation by Segment", unsafe_allow_html=True)

    segment_col = st.selectbox(
        "Segment by:",
        ["Seating_Region", "Gender", "Country", "Age_Group", "Repeat_Label"],
        key="exp_segment"
    )

    seg_stats = df.groupby(segment_col).agg(
        Avg_Satisfaction=('Satisfaction_Score', 'mean'),
        Avg_Recommendation=('Recommendation_Likelihood', 'mean'),
        Count=('Customer_ID', 'count')
    ).reset_index().sort_values('Avg_Satisfaction', ascending=False)

    col_left, col_right = st.columns(2)

    with col_left:
        fig_sat = px.bar(
            seg_stats, x=segment_col, y='Avg_Satisfaction',
            color='Avg_Satisfaction',
            color_continuous_scale='Tealgrn',
            title=f'Avg Satisfaction Score by {segment_col}',
            text=seg_stats['Avg_Satisfaction'].round(1)
        )
        fig_sat.update_layout(showlegend=False, yaxis_range=[0, 10])
        fig_sat.update_traces(textposition='outside')
        st.plotly_chart(fig_sat, width="stretch")

    with col_right:
        fig_rec = px.bar(
            seg_stats, x=segment_col, y='Avg_Recommendation',
            color='Avg_Recommendation',
            color_continuous_scale='Purp',
            title=f'Avg Recommendation Likelihood by {segment_col}',
            text=seg_stats['Avg_Recommendation'].round(1)
        )
        fig_rec.update_layout(showlegend=False, yaxis_range=[0, 10])
        fig_rec.update_traces(textposition='outside')
        st.plotly_chart(fig_rec, width="stretch")

    st.divider()

    # ── Section 3: Repeat vs. First-Time Visitor Comparison ──
    st.markdown("### <i class='bi bi-arrow-repeat'></i> Repeat vs. First-Time Visitor Experience", unsafe_allow_html=True)

    repeat_stats = df.groupby('Repeat_Label').agg(
        Avg_Satisfaction=('Satisfaction_Score', 'mean'),
        Avg_Recommendation=('Recommendation_Likelihood', 'mean'),
        Avg_Total_Spend=('Total_Spend', 'mean'),
        Avg_Merch_Spend=('Merchandise_Spend', 'mean'),
        Avg_Drink_Spend=('Drink_Spend', 'mean'),
        Customer_Count=('Customer_ID', 'count')
    ).reset_index()

    col_a, col_b = st.columns(2)

    with col_a:
        fig_repeat = go.Figure()
        fig_repeat.add_trace(go.Bar(
            name='Satisfaction',
            x=repeat_stats['Repeat_Label'],
            y=repeat_stats['Avg_Satisfaction'],
            marker_color='#06D6A0',
            text=repeat_stats['Avg_Satisfaction'].round(2)
        ))
        fig_repeat.add_trace(go.Bar(
            name='Recommendation',
            x=repeat_stats['Repeat_Label'],
            y=repeat_stats['Avg_Recommendation'],
            marker_color='#9b59b6',
            text=repeat_stats['Avg_Recommendation'].round(2)
        ))
        fig_repeat.update_layout(
            barmode='group',
            title='Experience Scores: Repeat vs First-Time',
            yaxis_range=[0, 10]
        )
        fig_repeat.update_traces(textposition='outside')
        st.plotly_chart(fig_repeat, width="stretch")

    with col_b:
        fig_spend_repeat = go.Figure()
        fig_spend_repeat.add_trace(go.Bar(
            name='Avg Total Spend',
            x=repeat_stats['Repeat_Label'],
            y=repeat_stats['Avg_Total_Spend'],
            marker_color='#3498db',
            text=repeat_stats['Avg_Total_Spend'].round(2)
        ))
        fig_spend_repeat.update_layout(
            title='Avg Total Spend: Repeat vs First-Time',
            yaxis_title='USD'
        )
        fig_spend_repeat.update_traces(textposition='outside')
        st.plotly_chart(fig_spend_repeat, width="stretch")

    st.divider()

    # ── Section 4: Satisfaction Distribution ──
    st.markdown("### <i class='bi bi-bar-chart-line'></i> Score Distributions", unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_hist_sat = px.histogram(
            df, x='Satisfaction_Score', nbins=20,
            color='Repeat_Label',
            barmode='overlay',
            title='Satisfaction Score Distribution',
            color_discrete_map={'Repeat': '#06D6A0', 'First-Time': '#E63946'},
            opacity=0.7
        )
        fig_hist_sat.update_layout(xaxis_title='Satisfaction Score', yaxis_title='Count')
        st.plotly_chart(fig_hist_sat, width="stretch")

    with col_d2:
        fig_hist_rec = px.histogram(
            df, x='Recommendation_Likelihood', nbins=11,
            color='Repeat_Label',
            barmode='overlay',
            title='Recommendation Likelihood Distribution',
            color_discrete_map={'Repeat': '#118AB2', 'First-Time': '#FFD166'},
            opacity=0.7
        )
        fig_hist_rec.update_layout(xaxis_title='Recommendation Likelihood', yaxis_title='Count')
        st.plotly_chart(fig_hist_rec, width="stretch")

    st.divider()

    # ── Section 5: Heatmap – Satisfaction by Country & Seating Region ──
    st.markdown("### <i class='bi bi-grid-3x3'></i> Satisfaction Heatmap: Country × Seating Region", unsafe_allow_html=True)

    pivot = df.pivot_table(
        values='Satisfaction_Score',
        index='Country',
        columns='Seating_Region',
        aggfunc='mean'
    )
    # Order seating regions logically
    region_order = ['Economy', 'High Economy', 'Premium', 'VIP']
    pivot = pivot.reindex(columns=[c for c in region_order if c in pivot.columns])

    fig_heat = px.imshow(
        pivot.round(1),
        text_auto=True,
        color_continuous_scale='RdYlGn',
        title='Avg Satisfaction Score by Country & Seating Region',
        aspect='auto'
    )
    fig_heat.update_layout(xaxis_title='Seating Region', yaxis_title='Country')
    st.plotly_chart(fig_heat, width="stretch")