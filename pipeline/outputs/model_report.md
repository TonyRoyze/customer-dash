# 📊 Customer Analytics — Model Report

*Generated on 2026-05-16 18:19:34*

---

## 1. Churn Prediction (Classification)

**Objective:** Predict whether a customer will churn (not return). Optimised for **F1 score**.

**Target variable:** `Repeat_Visit` (0 = churned, 1 = retained)

**Feature Selection:** Manually selected 3 features (based on permutation importance):
> Num_Tickets, Visit_DayOfWeek, Country_Japan

### Model Comparison

| Model | CV F1 | Test F1 | Test Precision | Test Recall |
|---|---|---|---|---|
| LogisticRegression | 0.4409 | 0.4219 | 0.6175 | 0.5375 |
| RandomForestClassifier ✅ | 0.3897 | 0.4426 | 0.6385 | 0.5750 |
| GradientBoostingClassifier | 0.5234 | 0.4298 | 0.6298 | 0.5687 |

### Best Model: `RandomForestClassifier`

**Best Hyperparameters:**
```json
{
  "class_weight": "balanced",
  "max_depth": 5,
  "min_samples_leaf": 2,
  "min_samples_split": 2,
  "n_estimators": 200
}
```

**Per-Class Metrics:**

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Churned (0) | 0.7558 | 0.5804 | 0.6566 | 112 |
| Retained (1) | 0.3649 | 0.5625 | 0.4426 | 48 |

**Confusion Matrix:**

| | Predicted Churned (0) | Predicted Retained (1) |
|---|---|---|
| **Actual Churned (0)** | 65 | 47 |
| **Actual Retained (1)** | 21 | 27 |

**Permutation Importances (Test Set):**

| Feature | Importance |
|---|---|
| Visit_DayOfWeek | 0.0558 |
| Num_Tickets | 0.0383 |
| Country_Japan | 0.0070 |

---

## 2. Revenue Prediction (Regression)

**Objective:** Predict total customer revenue per visit.

**Target variable:** `Total_Revenue` (Ticket Revenue + Merchandise + Drinks)

### Model Comparison

| Model | CV MAE | Test MAE | Test RMSE | Test R² |
|---|---|---|---|---|
| LinearRegression | 60.2686 | 58.1107 | 71.1512 | 0.8484 |
| Ridge | 60.1238 | 57.9347 | 71.2151 | 0.8481 |
| RandomForestRegressor ✅ | 35.4011 | 35.5813 | 45.7216 | 0.9374 |
| GradientBoostingRegressor | 35.3995 | 36.6535 | 46.0502 | 0.9365 |

### Best Model: `RandomForestRegressor`

**Best Hyperparameters:**
```json
{
  "max_depth": 5,
  "min_samples_leaf": 4,
  "min_samples_split": 10,
  "n_estimators": 300
}
```

**Residual Bias by Seating Region (Actual - Predicted):**

| Region | Mean Residual |
|---|---|

**Top Feature Importances / Coefficients:**

| Feature | Importance |
|---|---|
| Num_Tickets | 0.5013 |
| Ticket_Price | 0.4359 |
| Seating_Region_Premium | 0.0186 |
| Seating_Region_High Economy | 0.0185 |
| Seating_Region_VIP | 0.0145 |
| Visit_Month | 0.0024 |
| Age | 0.0022 |
| Visit_DayOfWeek | 0.0016 |
| Age_Group_36-45 | 0.0011 |
| Country_France | 0.0009 |
| Age_Group_26-35 | 0.0007 |
| Age_Group_56-65 | 0.0004 |
| Age_Group_46-55 | 0.0003 |
| Country_Sweden | 0.0003 |
| Gender_Male | 0.0003 |

---

## 3. Customer Clustering (Segmentation)

**Objective:** Segment customers into distinct behavioural groups.

**Selected Algorithm:** KMeans (K=2)

**Final Silhouette Score:** 0.1685

### Enriched Cluster Profiles

| Business_Label | Cluster | Size | Pct | Retention_Rate | Age | Ticket_Price | Num_Tickets | Merchandise_Spend | Drink_Spend | Repeat_Visit | Satisfaction_Score | Recommendation_Likelihood | Ticket_Revenue | Total_Revenue | Spend_Per_Ticket | Ancillary_Ratio | Sat_x_Rec | Spend_x_Tickets | Visit_Month | Visit_DayOfWeek | Visit_Quarter | Top_3_Countries | Top_Seating_Region |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Low-Value Churn-Risk | 0 | 450 | 56.2 | 0.2689 | 44.82 | 109.49 | 1.66 | 55.84 | 19.51 | 0.27 | 7.88 | 7.95 | 170.27 | 245.62 | 164.39 | 0.32 | 62.67 | 245.62 | 4.62 | 3.1 | 1.92 | Sweden, France, Australia | Economy |
| High-Value Occasional | 1 | 350 | 43.8 | 0.3457 | 42.93 | 125.83 | 3.54 | 64.68 | 20.07 | 0.35 | 8.14 | 8.07 | 438.63 | 523.38 | 151.29 | 0.18 | 65.54 | 523.38 | 4.74 | 2.9 | 1.95 | USA, France, Sweden | Premium |

### PCA Projection

- PC1 explains **24.6%** of variance
- PC2 explains **15.7%** of variance
- Total explained: **40.3%**

---

## 4. Executive Summary

| Task | Best Model | Key Metric |
|---|---|---|
| Churn Prediction | RandomForestClassifier | F1 = 0.4426 |
| Revenue Prediction | RandomForestRegressor | R² = 0.9374, MAE = 35.58 |
| Customer Clustering | KMeans | Silhouette = 0.1685 |
