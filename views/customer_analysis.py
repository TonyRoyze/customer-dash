import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_shadcn_ui as ui
from pygwalker.api.streamlit import StreamlitRenderer
import utils

def show():
    df = utils.load_dashboard_data()
    results = utils.load_json_results(utils.CLUSTERING_RESULTS_PATH)
    st.header("Customer Analysis")
    st.markdown("In-depth look at demographics, spending behavior, and customer loyalty.")

    # ── Shadcn KPIs ──
    total_cust = df['Customer_ID'].nunique()
    avg_tickets = df['Num_Tickets'].mean()
    repeat_rate = df['Repeat_Visit'].mean() * 100
    avg_age = df['Age'].mean()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        ui.metric_card(title="Unique Customers", content=f"{total_cust:,}", key="cust_m1")
    with m2:
        ui.metric_card(title="Avg Tickets/Order", content=f"{avg_tickets:.1f}", key="cust_m2")
    with m3:
        ui.metric_card(title="Loyalty Rate", content=f"{repeat_rate:.1f}%", key="cust_m3")
    with m4:
        ui.metric_card(title="Median Age", content=f"{avg_age:.0f}", key="cust_m4")

    st.divider()

    # ── Section 1: Customers by Demographics ──
    st.subheader("👥 Customer Demographics")
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
        st.plotly_chart(fig_gender, use_container_width=True)

        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # Chi-Square Goodness of Fit (Gender)
            chi_stat, chi_p = stats.chisquare(gender_counts['Count'])
            chi_sig = "✅ Significant Bias" if chi_p < 0.05 else "❌ Balanced Distribution"
            st.table(pd.DataFrame({
                "Test": ["Chi-Square (Gender)"],
                "Stat": [f"{chi_stat:.2f}"],
                "P-Value": [f"{chi_p:.4e}"],
                "Result": [chi_sig]
            }))

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

        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # Chi-Square (Age Group)
            chi_stat, chi_p = stats.chisquare(age_counts['Count'])
            chi_sig = "✅ Significant Variation" if chi_p < 0.05 else "❌ Uniform Distribution"
            st.table(pd.DataFrame({
                "Test": ["Chi-Square (Age)"],
                "Stat": [f"{chi_stat:.2f}"],
                "P-Value": [f"{chi_p:.4e}"],
                "Result": [chi_sig]
            }))

    st.divider()

    # ── Section 2: Customers by Geography ──
    st.subheader("🌎 Market Distribution")
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

        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # Chi-Square (Country Distribution)
            chi_stat, chi_p = stats.chisquare(country_counts['Count'])
            chi_sig = "✅ Concentration" if chi_p < 0.05 else "❌ Broad Distribution"
            st.table(pd.DataFrame({
                "Test": ["Chi-Square (Market)"],
                "Stat": [f"{chi_stat:.2f}"],
                "P-Value": [f"{chi_p:.4e}"],
                "Result": [chi_sig]
            }))

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
        st.plotly_chart(fig_cr, use_container_width=True)

        if st.session_state.get('advanced_mode'):
            from scipy import stats
            # Chi-Square Independence (Country vs Seating Region)
            contingency = pd.crosstab(df['Country'], df['Seating_Region'])
            chi2, p, dof, ex = stats.chi2_contingency(contingency)
            chi_sig = "✅ Linked" if p < 0.05 else "❌ Independent"
            st.table(pd.DataFrame({
                "Test": ["Chi2 Independence"],
                "Stat": [f"{chi2:.2f}"],
                "P-Value": [f"{p:.4e}"],
                "Result": [chi_sig]
            }))

    st.divider()

    # ── Section 3: AI Segmentation ──
    st.subheader("🤖 AI-Driven Customer Segmentation")
    st.markdown("Customers grouped by behavioral patterns using KMeans clustering.")

    if results and 'cluster_profiles' in results:
        # Segment KPI cards
        cols = st.columns(len(results['cluster_profiles']))
        for i, profile in enumerate(results['cluster_profiles']):
            with cols[i]:
                ui.card(
                    title=profile['Business_Label'],
                    content=f"{profile['Pct']}% of Customers",
                    description=f"Avg Spend: ${profile['Total_Revenue']:.0f} | {profile['Top_Seating_Region']} Tier",
                    key=f"seg_card_{i}"
                ).render()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Segment Visualization
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            # PCA or behavioral split
            fig_seg = px.scatter(
                df, x='Total_Revenue', y='Satisfaction_Score', color='Business_Label',
                title="Revenue vs Satisfaction by Segment",
                labels={'Business_Label': 'Segment'},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig_seg, use_container_width=True)
        
        with col_s2:
            seg_counts = df['Business_Label'].value_counts().reset_index()
            fig_pie = px.pie(
                seg_counts, values='count', names='Business_Label',
                hole=0.4, title="Segment Distribution",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Clustering results not found. Please run the pipeline first.")

    st.divider()

    # ── Pygwalker Customer Explorer ──
    st.subheader("👥 Customer Segmentation Explorer")
    renderer = StreamlitRenderer(df)
    renderer.explorer()

    if st.session_state.get('advanced_mode'):
        st.divider()
        st.subheader("🔬 Advanced Behavioral Statistics")
        from scipy import stats
        
        # Chi-Square: Gender vs. Repeat Visit
        contingency = pd.crosstab(df['Gender'], df['Repeat_Visit'])
        chi2, p_val, dof, ex = stats.chi2_contingency(contingency)
        sig_text = "dependent (linked)" if p_val < 0.05 else "independent"
        
        col_adv1, col_adv2 = st.columns(2)
        with col_adv1:
            ui.card(
                title="Gender vs Loyalty (Chi2)",
                content=f"Chi2 Stat: **{chi2:.2f}** (p={p_val:.4f}). Gender and Loyalty are statistically **{sig_text}**.",
                description="Testing if one gender is more likely to be a repeat visitor.",
                key="cust_adv_1"
            ).render()
        with col_adv2:
            avg_age_repeat = df[df['Repeat_Visit'] == 1]['Age'].mean()
            avg_age_first = df[df['Repeat_Visit'] == 0]['Age'].mean()
            diff = avg_age_repeat - avg_age_first
            ui.card(
                title="Loyalty Age Delta",
                content=f"Repeat visitors are, on average, **{abs(diff):.1f} years {'older' if diff > 0 else 'younger'}** than first-time visitors.",
                description="Age-based Loyalty Analysis",
                key="cust_adv_2"
            ).render()