import json
import os
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
import joblib

from config import (
    CHURN_TARGET,
    MODELS_DIR,
    OUTPUT_DIR,
    RANDOM_SEED,
    REVENUE_PARAM_GRIDS,
    REVENUE_TARGET,
    REVENUE_DROP_COLS,
)

warnings.filterwarnings("ignore")


def load_splits():
    train = pd.read_csv(os.path.join(OUTPUT_DIR, "train.csv"))
    test = pd.read_csv(os.path.join(OUTPUT_DIR, "test.csv"))
    return train, test


def prepare_xy(train, test):
    drop_cols = [CHURN_TARGET, REVENUE_TARGET] + REVENUE_DROP_COLS

    X_train = train.drop(columns=[c for c in drop_cols if c in train.columns])
    y_train = train[REVENUE_TARGET]
    X_test = test.drop(columns=[c for c in drop_cols if c in test.columns])
    y_test = test[REVENUE_TARGET]

    return X_train, y_train, X_test, y_test


def scale_features(X_train, X_test):
    scaler = StandardScaler()
    X_train_s = pd.DataFrame(
        scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index
    )
    X_test_s = pd.DataFrame(
        scaler.transform(X_test), columns=X_test.columns, index=X_test.index
    )
    return X_train_s, X_test_s, scaler

def train_and_tune(X_train, y_train):
    models = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(random_state=RANDOM_SEED),
        "RandomForestRegressor": RandomForestRegressor(random_state=RANDOM_SEED),
        "GradientBoostingRegressor": GradientBoostingRegressor(random_state=RANDOM_SEED),
    }

    results = {}
    for name, estimator in models.items():
        print(f"  ▸ Tuning {name} ...")
        grid = GridSearchCV(
            estimator=estimator,
            param_grid=REVENUE_PARAM_GRIDS[name],
            scoring="neg_mean_absolute_error",
            cv=5,
            n_jobs=-1,
            refit=True,
            verbose=0,
        )
        grid.fit(X_train, y_train)
        results[name] = {
            "best_estimator": grid.best_estimator_,
            "best_params": grid.best_params_,
            "best_cv_neg_mae": grid.best_score_,
        }
        print(f"    Best CV MAE = {-grid.best_score_:.4f}  |  Params: {grid.best_params_}")

    return results


def evaluate_best(results, X_test, y_test):
    best_name = None
    best_mae = float("inf")
    eval_results = {}

    for name, res in results.items():
        model = res["best_estimator"]
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        residuals = y_test - y_pred
        
        seating_cols = [c for c in X_test.columns if "Seating_Region" in c]
        bias_by_region = {}
        for col in seating_cols:
            mask = X_test[col] == 1
            if mask.sum() > 0:
                bias_by_region[col.replace("Seating_Region_", "")] = round(float(residuals[mask].mean()), 4)
        
        if len(seating_cols) > 0:
            mask_ref = (X_test[seating_cols] == 0).all(axis=1)
            if mask_ref.sum() > 0:
                bias_by_region["Reference_Region"] = round(float(residuals[mask_ref].mean()), 4)

        eval_results[name] = {
            "test_mae": round(mae, 4),
            "test_rmse": round(rmse, 4),
            "test_r2": round(r2, 4),
            "best_cv_mae": round(-res["best_cv_neg_mae"], 4),
            "best_params": res["best_params"],
            "residual_bias": bias_by_region
        }

        if hasattr(model, "feature_importances_"):
            importances = dict(
                sorted(
                    zip(X_test.columns, model.feature_importances_),
                    key=lambda x: x[1],
                    reverse=True,
                )[:15]
            )
            eval_results[name]["feature_importances"] = {
                k: round(v, 4) for k, v in importances.items()
            }
        elif hasattr(model, "coef_"):
            coefs = model.coef_
            if coefs.ndim > 1: coefs = coefs[0]
            importances = dict(
                sorted(
                    zip(X_test.columns, np.abs(coefs)),
                    key=lambda x: x[1],
                    reverse=True,
                )[:15]
            )
            eval_results[name]["feature_importances"] = {
                k: round(v, 4) for k, v in importances.items()
            }


        eval_results[name]["actual_vs_predicted"] = {
            "actual": y_test.tolist(),
            "predicted": y_pred.tolist(),
        }

        if mae < best_mae:
            best_mae = mae
            best_name = name

        print(f"  ▸ {name}  →  MAE = {mae:.4f}  |  RMSE = {rmse:.4f}  |  R² = {r2:.4f}")

    return best_name, eval_results


def main():
    print("=" * 60)
    print("STAGE 3 : REVENUE PREDICTION")
    print("=" * 60)

    train, test = load_splits()
    X_train, y_train, X_test, y_test = prepare_xy(train, test)
    X_train_s, X_test_s, scaler = scale_features(X_train, X_test)

    print("[REVENUE] Training & hyperparameter tuning ...")
    results = train_and_tune(X_train_s, y_train)

    print("\n[REVENUE] Evaluating on test set ...")
    best_name, eval_results = evaluate_best(results, X_test_s, y_test)

    # Save best model
    best_model = results[best_name]["best_estimator"]
    model_path = os.path.join(MODELS_DIR, "revenue_best_model.joblib")
    joblib.dump(best_model, model_path)

    # Save scaler
    scaler_path = os.path.join(MODELS_DIR, "revenue_scaler.joblib")
    joblib.dump(scaler, scaler_path)

    # Save results JSON
    output = {
        "best_model": best_name,
        "all_models": eval_results,
    }
    results_path = os.path.join(OUTPUT_DIR, "revenue_results.json")
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n[REVENUE] ✓ Best model: {best_name} (Test MAE = {eval_results[best_name]['test_mae']:.4f})")
    print(f"[REVENUE] Saved model → {model_path}")
    print(f"[REVENUE] Saved results → {results_path}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
