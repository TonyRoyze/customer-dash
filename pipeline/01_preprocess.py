import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from config import (
    DATA_PATH, OUTPUT_DIR, RANDOM_SEED, TEST_SIZE,
    DROP_COLS, CATEGORICAL_COLS, CHURN_TARGET,
)
import os
import warnings

warnings.filterwarnings("ignore")


def load_raw_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    print(f"[PREPROCESS] Loaded {len(df)} rows from {DATA_PATH}")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Revenue features
    df["Ticket_Revenue"] = df["Ticket_Price"] * df["Num_Tickets"]
    df["Total_Revenue"] = (
        df["Ticket_Revenue"] + df["Merchandise_Spend"] + df["Drink_Spend"]
    )
    df["Spend_Per_Ticket"] = df["Total_Revenue"] / df["Num_Tickets"]
    df["Ancillary_Ratio"] = (
        (df["Merchandise_Spend"] + df["Drink_Spend"]) / df["Total_Revenue"]
    )
    
    # Interaction features
    df["Sat_x_Rec"] = df["Satisfaction_Score"] * df["Recommendation_Likelihood"]
    df["Spend_x_Tickets"] = df["Spend_Per_Ticket"] * df["Num_Tickets"]

    # Date features
    df["Visit_Date"] = pd.to_datetime(df["Visit_Date"])
    df["Visit_Month"] = df["Visit_Date"].dt.month
    df["Visit_DayOfWeek"] = df["Visit_Date"].dt.dayofweek  # 0=Mon, 6=Sun
    df["Visit_Quarter"] = df["Visit_Date"].dt.quarter

    # Age binning
    bins = [0, 25, 35, 45, 55, 65, 100]
    labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
    df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=True)

    print(f"[PREPROCESS] Engineered {df.shape[1]} columns")
    return df


def encode_and_split(df: pd.DataFrame):

    full_processed = df.copy()

    
    df = pd.get_dummies(df, columns=CATEGORICAL_COLS + ["Age_Group"], drop_first=True)

    
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors="ignore")

    # Stratified split on churn target
    train_df, test_df = train_test_split(
        df,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=df[CHURN_TARGET],
    )

    print(f"[PREPROCESS] Train: {len(train_df)}  |  Test: {len(test_df)}")
    return train_df, test_df, full_processed


def main():
    print("=" * 60)
    print("STAGE 1 : DATA PREPROCESSING")
    print("=" * 60)

    df = load_raw_data()
    df = engineer_features(df)
    train_df, test_df, full_processed = encode_and_split(df)


    train_df.to_csv(os.path.join(OUTPUT_DIR, "train.csv"), index=False)
    test_df.to_csv(os.path.join(OUTPUT_DIR, "test.csv"), index=False)
    full_processed.to_csv(os.path.join(OUTPUT_DIR, "full_processed.csv"), index=False)

    print(f"[PREPROCESS] Saved train.csv, test.csv, full_processed.csv → {OUTPUT_DIR}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
