"""
config.py — Centralised pipeline configuration.
Paths, feature lists, random seed, and hyperparameter grids.
"""

import os

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw.csv")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")

# Create output directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# ─── Random seed ──────────────────────────────────────────────────────────────
RANDOM_SEED = 42

# ─── Test split ratio ────────────────────────────────────────────────────────
TEST_SIZE = 0.20

# ─── Feature lists ───────────────────────────────────────────────────────────

# Columns dropped before any modelling (identifiers / raw date)
DROP_COLS = ["Customer_ID", "Visit_Date"]

# Target columns
CHURN_TARGET = "Repeat_Visit"         # 0 = churned, 1 = retained
REVENUE_TARGET = "Total_Revenue"      # continuous

# Categorical columns to one-hot encode
CATEGORICAL_COLS = ["Gender", "Country", "Seating_Region"]

# Numeric columns used for clustering (pre-encoding)
CLUSTER_FEATURES = [
    "Age",
    "Total_Revenue",
    "Merchandise_Spend",
    "Drink_Spend",
    "Num_Tickets",
    "Satisfaction_Score",
    "Recommendation_Likelihood",
]

# Columns to drop for revenue prediction (post-visit data leakage)
REVENUE_DROP_COLS = [
    "Ticket_Revenue", "Merchandise_Spend", "Drink_Spend", 
    "Spend_Per_Ticket", "Ancillary_Ratio", 
    "Satisfaction_Score", "Recommendation_Likelihood",
    "Repeat_Visit", "Sat_x_Rec", "Spend_x_Tickets"
]

# ─── Hyperparameter grids ────────────────────────────────────────────────────

# Churn (classification) — optimised for F1
CHURN_PARAM_GRIDS = {
    "LogisticRegression": {
        "class_weight": ["balanced"],
        "C": [0.01, 0.1, 1, 10],
        "penalty": ["l1"],
        "solver": ["liblinear"],
        "max_iter": [1000],
    },
    "RandomForestClassifier": {
        "class_weight": ["balanced"],
        "n_estimators": [100, 200, 300],
        "max_depth": [5, 10, 15, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
    },
    "GradientBoostingClassifier": {
        "n_estimators": [100, 200, 300],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "max_depth": [3, 5, 7],
        "subsample": [0.8, 1.0],
    },
}

# Revenue (regression)
REVENUE_PARAM_GRIDS = {
    "LinearRegression": {
        "fit_intercept": [True],
    },
    "Ridge": {
        "alpha": [0.01, 0.1, 1, 10, 100],
    },
    "RandomForestRegressor": {
        "n_estimators": [100, 200, 300],
        "max_depth": [5, 10, 15, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
    },
    "GradientBoostingRegressor": {
        "n_estimators": [100, 200, 300],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "max_depth": [3, 5, 7],
        "subsample": [0.8, 1.0],
    },
}
