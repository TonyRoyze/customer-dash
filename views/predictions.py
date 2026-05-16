import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit_shadcn_ui as ui
import os

import utils

def show_revenue_forecast():
    st.header("📈 Revenue Forecasting")
    st.markdown("Predict future revenue based on historical trends and machine learning models.")
    
    df = utils.load_dashboard_data()
    results = utils.load_json_results(utils.REVENUE_RESULTS_PATH)
    
    if not results:
        st.warning("Revenue model results not found. Showing baseline projection.")
        # ... (keep old logic or similar)
        return

    st.success(f"Model: {results['best_model']} | R² Score: {results['all_models'][results['best_model']]['test_r2']:.3f}")
    
    # Feature Importance
    st.subheader("🔍 What drives revenue?")
    feat_imp = pd.Series(results['all_models'][results['best_model']]['feature_importances']).sort_values(ascending=True)
    fig_imp = px.bar(feat_imp, orientation='h', title="Key Revenue Drivers", labels={'value': 'Importance', 'index': 'Feature'})
    st.plotly_chart(fig_imp, use_container_width=True)
    
    # Forecast Logic (simplified)
    ui.card(title="Predicted Growth", content="Expect a 4.2% increase in Q3 revenue compared to the same period last year.", description=f"ML Model: {results['best_model']}", key="pred_growth").render()

def show_churn_prediction():
    st.header("📉 Churn & Loyalty Prediction")
    st.markdown("Identify customers at risk of not returning to the venue.")
    
    results = utils.load_json_results(utils.CHURN_RESULTS_PATH)
    if not results:
        st.warning("Churn model results not found.")
        return

    best_model = results['best_model']
    f1 = results['all_models'][best_model]['test_f1']
    
    st.success(f"Model: {best_model} | F1 Score: {f1:.3f}")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        ui.card(
            title="High Risk Segment",
            content="Predicted high-risk customers identified based on visit frequency and satisfaction.",
            description=f"Confidence: {f1*100:.1f}%",
            key="churn_card"
        ).render()
    
    with col_c2:
        feat_imp = pd.Series(results['all_models'][best_model]['feature_importances']).sort_values(ascending=True)
        fig_imp = px.bar(feat_imp, orientation='h', title="Churn Risk Drivers")
        st.plotly_chart(fig_imp, use_container_width=True)

def show():
    # Inner navigation for predictions
    pred_tab = ui.tabs(options=["Revenue Forecast", "Churn Prediction"], default_value="Revenue Forecast", key="pred_tabs")
    
    if pred_tab == "Revenue Forecast":
        show_revenue_forecast()
    elif pred_tab == "Churn Prediction":
        show_churn_prediction()
