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

    # ── Row 1: Monthly Revenue Trends ──
    st.subheader("📈 Temporal Trends")
    col_a, col_b = st.columns(2)

    with col_a:
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
            slope, intercept, r_val, p_val, std_err = stats.linregress(x_vals, monthly['Total_Revenue'])
            reg_sig = "✅ Significant" if p_val < 0.05 else "❌ Not Significant"
            
            st.table(pd.DataFrame({
                "Metric": ["Avg MoM Growth", "Revenue Volatility (CV)", "Trend Slope", "Trend Significance (p)"],
                "Value": [f"{avg_mom:+.1f}%", f"{volatility:.1f}%", f"${slope:,.2f}/mo", f"{p_val:.4e}"],
                "Status": ["-", "Higher = Less Stable", reg_sig, "p < 0.05 is significant"]
            }))
        
    with col_b:
        st.markdown("### <i class='bi bi-people'></i> Monthly Visitor Composition", unsafe_allow_html=True)

        monthly['First_Time_Visitors'] = monthly['Visitors'] - monthly['Repeat_Visitors']
        monthly['Repeat_Rate'] = (monthly['Repeat_Visitors'] / monthly['Visitors'] * 100).round(1)

        fig_visitors = go.Figure()
        # First-Time Visitors (Base)
        fig_visitors.add_trace(go.Bar(
            x=monthly['Month_dt'], y=monthly['First_Time_Visitors'],
            name='First-Time Visitors',
            marker_color='#E63946',
            text=monthly['First_Time_Visitors'],
            textposition='inside'
        ))
        # Repeat Visitors (Stacked)
        fig_visitors.add_trace(go.Bar(
            x=monthly['Month_dt'], y=monthly['Repeat_Visitors'],
            name='Repeat Visitors',
            marker_color='#06D6A0',
            text=monthly['Repeat_Visitors'],
            textposition='inside'
        ))

        fig_visitors.update_layout(
            barmode='stack',
            title='Monthly Visitor Volume (Repeat vs. First-Time)',
            xaxis_title='Month',
            yaxis_title='Number of Visitors',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, title_text='')
        )
        st.plotly_chart(fig_visitors, use_container_width=True)

        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # Chi-Square Independence (Month vs Loyalty)
            # Create contingency table
            contingency = pd.crosstab(df['Month_dt'], df['Repeat_Visit'])
            chi2, p, dof, ex = stats.chi2_contingency(contingency)
            chi_sig = "✅ Significant Shift" if p < 0.05 else "❌ Stable Composition"
            st.table(pd.DataFrame({
                "Test": ["Chi2 (Visitor Mix)"],
                "Stat": [f"{chi2:.2f}"],
                "P-Value": [f"{p:.4e}"],
                "Result": [chi_sig]
            }))

    st.divider()

    # ── Section 4: Day-of-Week Patterns ──
    st.subheader("🗓️ Day of Week Performance")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_stats = df.groupby('Day_of_Week').agg(
        Visits=('Customer_ID', 'count'),
        Avg_Revenue=('Total_Revenue', 'mean')
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

        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # Chi-Square Goodness of Fit (Daily Volume)
            chi_stat, chi_p = stats.chisquare(day_stats['Visits'])
            chi_sig = "✅ Significant Busy Days" if chi_p < 0.05 else "❌ Uniform Footfall"
            st.table(pd.DataFrame({
                "Test": ["Chi2 (Daily Volume)"],
                "Stat": [f"{chi_stat:.2f}"],
                "P-Value": [f"{chi_p:.4e}"],
                "Result": [chi_sig]
            }))

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

        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # ANOVA (Daily Revenue Variance)
            day_groups = [df[df['Day_of_Week'] == d]['Total_Revenue'] for d in day_order]
            f_stat, f_p = stats.f_oneway(*day_groups)
            f_sig = "✅ Significant" if f_p < 0.05 else "❌ Not Significant"
            st.table(pd.DataFrame({
                "Test": ["ANOVA (Daily Rev)"],
                "F-Stat": [f"{f_stat:.2f}"],
                "P-Value": [f"{f_p:.4e}"],
                "Result": [f_sig]
            }))

    st.divider()

    # ── Pygwalker Temporal Explorer ──
    st.subheader("📅 Temporal Data Explorer")
    st.markdown("Use the explorer below to slice and dice the venue data dynamically.")
    # Filter for relevant columns to simplify the explorer
    time_cols = ['Visit_Date', 'Month_dt', 'Day_of_Week', 'Total_Revenue', 'Ticket_Revenue', 
                 'Merchandise_Spend', 'Drink_Spend', 'Repeat_Visit', 'Seating_Region', 'Customer_ID']
    renderer = StreamlitRenderer(df[time_cols])
    renderer.explorer()
