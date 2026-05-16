import streamlit as st
import pandas as pd
import json
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw.csv')
CLUSTER_LABELS_PATH = os.path.join(BASE_DIR, 'pipeline', 'outputs', 'cluster_labels.csv')
CLUSTERING_RESULTS_PATH = os.path.join(BASE_DIR, 'pipeline', 'outputs', 'clustering_results.json')
CHURN_RESULTS_PATH = os.path.join(BASE_DIR, 'pipeline', 'outputs', 'churn_results.json')
REVENUE_RESULTS_PATH = os.path.join(BASE_DIR, 'pipeline', 'outputs', 'revenue_results.json')

@st.cache_data
def load_dashboard_data():
    """Loads raw data and merges with cluster labels."""
    df = pd.read_csv(DATA_PATH)
    df['Visit_Date'] = pd.to_datetime(df['Visit_Date'])
    df['Ticket_Revenue'] = df['Ticket_Price'] * df['Num_Tickets']
    df['Total_Revenue'] = df['Ticket_Revenue'] + df['Merchandise_Spend'] + df['Drink_Spend']
    df['Repeat_Label'] = df['Repeat_Visit'].map({1: 'Repeat', 0: 'First-Time'})
    
    # Merge Clustering Results
    if os.path.exists(CLUSTER_LABELS_PATH):
        clusters = pd.read_csv(CLUSTER_LABELS_PATH)
        df = df.merge(clusters, on='Customer_ID', how='left')
        
        # Add Business Labels
        results = load_json_results(CLUSTERING_RESULTS_PATH)
        if results and 'cluster_profiles' in results:
            mapping = {p['Cluster']: p['Business_Label'] for p in results['cluster_profiles']}
            df['Business_Label'] = df['Cluster'].map(mapping)
    
    # Preprocessing for demographics
    bins = [0, 25, 35, 45, 55, 65, 100]
    labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
    df['Age_Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=True)
    df['Month_dt'] = df['Visit_Date'].dt.to_period('M').dt.to_timestamp()
    
    return df

def load_json_results(path):
    """Utility to load JSON results from pipeline."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def get_model_results():
    """Returns a dictionary of all model results."""
    return {
        'clustering': load_json_results(CLUSTERING_RESULTS_PATH),
        'churn': load_json_results(CHURN_RESULTS_PATH),
        'revenue': load_json_results(REVENUE_RESULTS_PATH)
    }
