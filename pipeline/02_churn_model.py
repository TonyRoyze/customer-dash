import json
import os
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
import joblib

from config import (
    CHURN_PARAM_GRIDS,
    CHURN_TARGET,
    MODELS_DIR,
    OUTPUT_DIR,
    RANDOM_SEED,
    REVENUE_TARGET,
)

warnings.filterwarnings("ignore")


def load_splits():
    train = pd.read_csv(os.path.join(OUTPUT_DIR, "train.csv"))
    test = pd.read_csv(os.path.join(OUTPUT_DIR, "test.csv"))
    return train, test


def prepare_xy(train, test):
    drop_cols = [CHURN_TARGET, REVENUE_TARGET]

    X_train = train.drop(columns=[c for c in drop_cols if c in train.columns])
    y_train = train[CHURN_TARGET]
    X_test = test.drop(columns=[c for c in drop_cols if c in test.columns])
    y_test = test[CHURN_TARGET]

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


from sklearn.feature_selection import RFECV
from sklearn.inspection import permutation_importance

def train_and_tune(X_train, y_train):
    models = {
        "LogisticRegression": LogisticRegression(random_state=RANDOM_SEED),
        "RandomForestClassifier": RandomForestClassifier(random_state=RANDOM_SEED),
        "GradientBoostingClassifier": GradientBoostingClassifier(random_state=RANDOM_SEED),
    }

    # Compute sample weights for models that don't support class_weight directly (GBM)
    from sklearn.utils.class_weight import compute_sample_weight
    sample_weights = compute_sample_weight(class_weight='balanced', y=y_train)

    results = {}
    for name, estimator in models.items():
        print(f"  ▸ Tuning {name} ...")
        grid = GridSearchCV(
            estimator=estimator,
            param_grid=CHURN_PARAM_GRIDS[name],
            scoring="f1",          
            cv=5,
            n_jobs=-1,
            refit=True,
            verbose=0,
        )
        
        if name == "GradientBoostingClassifier":
            grid.fit(X_train, y_train, **{'sample_weight': sample_weights})
        else:
            grid.fit(X_train, y_train)
            
        results[name] = {
            "best_estimator": grid.best_estimator_,
            "best_params": grid.best_params_,
            "best_cv_f1": grid.best_score_,
        }
        print(f"    Best CV F1 = {grid.best_score_:.4f}  |  Params: {grid.best_params_}")

    return results


def evaluate_best(results, X_test, y_test):
    best_name = None
    best_f1 = -1
    eval_results = {}

    for name, res in results.items():
        model = res["best_estimator"]
        y_pred = model.predict(X_test)

        test_f1 = f1_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred).tolist()

        eval_results[name] = {
            "test_f1": round(test_f1, 4),
            "best_cv_f1": round(res["best_cv_f1"], 4),
            "best_params": res["best_params"],
            "classification_report": report,
            "confusion_matrix": cm,
        }

        if test_f1 > best_f1:
            best_f1 = test_f1
            best_name = name

        print(f"  ▸ {name}  →  Test F1 = {test_f1:.4f}")


    best_model = results[best_name]["best_estimator"]
    print(f"\n[CHURN] Computing permutation importance for best model ({best_name}) ...")
    perm_res = permutation_importance(best_model, X_test, y_test, scoring='f1', n_repeats=10, random_state=RANDOM_SEED)
    importances = dict(
        sorted(
            zip(X_test.columns, perm_res.importances_mean),
            key=lambda x: x[1],
            reverse=True,
        )[:15]
    )
    eval_results[best_name]["feature_importances"] = {
        k: round(v, 4) for k, v in importances.items()
    }

    return best_name, eval_results


def main():
    print("=" * 60)
    print("STAGE 2 : CHURN PREDICTION (F1-OPTIMISED & FEATURE SELECTED)")
    print("=" * 60)

    train, test = load_splits()
    X_train, y_train, X_test, y_test = prepare_xy(train, test)
    X_train_s, X_test_s, scaler = scale_features(X_train, X_test)

    
    selected_features = ['Num_Tickets', 'Visit_DayOfWeek', 'Country_Japan']
    print(f"[CHURN] Using manually selected features (Importance > 0.01 & non-leaky): {selected_features}")

   
    X_train_sel = X_train_s[selected_features]
    X_test_sel = X_test_s[selected_features]

    print("\n[CHURN] Training & hyperparameter tuning on selected features ...")
    results = train_and_tune(X_train_sel, y_train)

    print("\n[CHURN] Evaluating on test set ...")
    best_name, eval_results = evaluate_best(results, X_test_sel, y_test)

    
    best_model = results[best_name]["best_estimator"]
    model_path = os.path.join(MODELS_DIR, "churn_best_model.joblib")
    joblib.dump(best_model, model_path)

   
    scaler_path = os.path.join(MODELS_DIR, "churn_scaler.joblib")
    joblib.dump(scaler, scaler_path)

    
    output = {
        "best_model": best_name,
        "selected_features": selected_features,
        "all_models": eval_results,
    }
    results_path = os.path.join(OUTPUT_DIR, "churn_results.json")
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n[CHURN] ✓ Best model: {best_name} (Test F1 = {eval_results[best_name]['test_f1']:.4f})")
    print(f"[CHURN] Saved model → {model_path}")
    print(f"[CHURN] Saved results → {results_path}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
