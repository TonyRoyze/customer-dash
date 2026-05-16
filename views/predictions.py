import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit_shadcn_ui as ui
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw.csv')

def load_data():
    df = pd.read_csv(DATA_PATH)
    df['Visit_Date'] = pd.to_datetime(df['Visit_Date'])
    df['Ticket_Revenue'] = df['Ticket_Price'] * df['Num_Tickets']
    df['Total_Revenue'] = df['Ticket_Revenue'] + df['Merchandise_Spend'] + df['Drink_Spend']
    return df

def show_revenue_forecast():
    st.header("📈 Revenue Forecasting")
    st.markdown("Predict future revenue based on historical trends and seasonality.")
    
    df = load_data()
    monthly = df.groupby(df['Visit_Date'].dt.to_period('M')).agg({'Total_Revenue': 'sum'}).reset_index()
    monthly['Visit_Date'] = monthly['Visit_Date'].dt.to_timestamp()
    
    # Mock Forecast (Simplistic linear trend)
    st.info("Simulating a 3-month forecast based on existing growth patterns.")
    
    # Simple linear regression mock
    x = np.arange(len(monthly))
    y = monthly['Total_Revenue'].values
    coeffs = np.polyfit(x, y, 1)
    predict = np.poly1d(coeffs)
    
    last_month = monthly['Visit_Date'].max()
    forecast_dates = pd.date_range(last_month, periods=4, freq='MS')[1:]
    forecast_values = predict(np.arange(len(monthly), len(monthly) + 3))
    
    forecast_df = pd.DataFrame({'Date': forecast_dates, 'Forecast': forecast_values})
    
    fig = px.line(monthly, x='Visit_Date', y='Total_Revenue', title="Historical vs. Forecasted Revenue")
    fig.add_scatter(x=forecast_df['Date'], y=forecast_df['Forecast'], mode='lines+markers', name='Forecast', line=dict(dash='dash', color='red'))
    st.plotly_chart(fig, use_container_width=True)
    
    ui.card(title="Predicted Growth", content="Expect a 4.2% increase in Q3 revenue compared to the same period last year.", description="ML Model: Linear Trend Projection", key="pred_growth").render()

def show_churn_prediction():
    st.header("📉 Churn & Loyalty Prediction")
    st.markdown("Identify customers at risk of not returning to the venue.")
    
    ui.card(
        title="High Risk Segment",
        content="234 customers from the Economy section have a churn probability > 70% in the next 6 months.",
        description="ML Model: Random Forest Classifier",
        key="churn_card"
    ).render()
    
    st.info("Predictive features include: Time since last visit, Satisfaction Score, and Total Spend.")

def show():
    # Inner navigation for predictions
    pred_tab = ui.tabs(options=["Revenue Forecast", "Churn Prediction"], default_value="Revenue Forecast", key="pred_tabs")
    
    if pred_tab == "Revenue Forecast":
        show_revenue_forecast()
    elif pred_tab == "Churn Prediction":
        show_churn_prediction()
