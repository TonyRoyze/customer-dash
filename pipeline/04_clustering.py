import json
import os
import warnings

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from config import CLUSTER_FEATURES, OUTPUT_DIR, RANDOM_SEED

warnings.filterwarnings("ignore")


def load_data():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "full_processed.csv"))
    print(f"[CLUSTER] Loaded {len(df)} rows")
    return df


def prepare_features(df):
    X = df[CLUSTER_FEATURES].dropna().copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X, X_scaled, scaler


def assign_business_labels(profiles):
    labels = []
    for idx, row in profiles.iterrows():
        if "Total_Revenue" in profiles.columns:
            if row["Total_Revenue"] >= profiles["Total_Revenue"].median():
                labels.append("High-Value Loyalist" if row.get("Retention_Rate", 0) > 0.5 else "High-Value Occasional")
            else:
                labels.append("Casual Visitor" if row.get("Retention_Rate", 0) > 0.5 else "Low-Value Churn-Risk")
        else:
            labels.append(f"Segment {idx}")
    profiles["Business_Label"] = labels
    return profiles


def compute_enriched_profiles(df, labels, x_index):
    df_profile = df.iloc[x_index].copy()
    df_profile["Cluster"] = labels
    
    num_cols = df_profile.select_dtypes(include=[np.number]).columns.tolist()
    if "Cluster" not in num_cols:
        num_cols.append("Cluster")
        
    profiles = df_profile[num_cols].groupby("Cluster").mean().round(2)
    
    counts = df_profile["Cluster"].value_counts().sort_index()
    profiles["Size"] = counts.values
    profiles["Pct"] = (counts.values / len(df_profile) * 100).round(1)
    
    if "Repeat_Visit" in df_profile.columns:
        profiles["Retention_Rate"] = df_profile.groupby("Cluster")["Repeat_Visit"].mean().round(4)
        
    if "Country" in df_profile.columns:
        def top_3_countries(series):
            return ", ".join(series.value_counts().head(3).index.tolist())
        profiles["Top_3_Countries"] = df_profile.groupby("Cluster")["Country"].apply(top_3_countries)
        
    if "Seating_Region" in df_profile.columns:
        def mode_seating(series):
            return series.mode()[0]
        profiles["Top_Seating_Region"] = df_profile.groupby("Cluster")["Seating_Region"].apply(mode_seating)

    profiles = assign_business_labels(profiles)
    
    return profiles


def pca_projection(X_scaled, labels):
    """2D PCA projection for visualization data."""
    pca = PCA(n_components=2, random_state=RANDOM_SEED)
    coords = pca.fit_transform(X_scaled)
    explained = pca.explained_variance_ratio_
    return coords, explained


def main():
    print("=" * 60)
    print("STAGE 4 : CUSTOMER CLUSTERING (KMeans K=2)")
    print("=" * 60)

    df = load_data()
    X_raw, X_scaled, scaler = prepare_features(df)

    print("[CLUSTER] Fitting final KMeans model (K=2) ...")
    km = KMeans(n_clusters=2, random_state=RANDOM_SEED, n_init=10)
    labels = km.fit_predict(X_scaled)
    final_sil = silhouette_score(X_scaled, labels)
    print(f"[CLUSTER] Final silhouette score = {final_sil:.4f}")

    # Cluster profiles
    profiles = compute_enriched_profiles(df, labels, X_raw.index)
    print("\n[CLUSTER] Enriched Cluster Profiles:")
    print(profiles[["Business_Label", "Size", "Pct", "Retention_Rate", "Total_Revenue"]].to_string())

    # PCA projection
    coords, explained_var = pca_projection(X_scaled, labels)

    # Save cluster labels
    labels_df = df[["Customer_ID"]].iloc[X_raw.index].copy()
    labels_df["Cluster"] = labels
    labels_path = os.path.join(OUTPUT_DIR, "cluster_labels.csv")
    labels_df.to_csv(labels_path, index=False)

    # Save results JSON
    output = {
        "chosen_algo": "KMeans",
        "best_k": 2,
        "final_silhouette": round(float(final_sil), 4),
        "cluster_profiles": profiles.reset_index().to_dict(orient="records"),
        "pca_explained_variance": [round(float(v), 4) for v in explained_var],
        "pca_coordinates": {
            "x": coords[:, 0].tolist(),
            "y": coords[:, 1].tolist(),
            "labels": [int(l) for l in labels],
        },
    }
    results_path = os.path.join(OUTPUT_DIR, "clustering_results.json")
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n[CLUSTER] ✓ Saved cluster labels → {labels_path}")
    print(f"[CLUSTER] ✓ Saved results → {results_path}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
