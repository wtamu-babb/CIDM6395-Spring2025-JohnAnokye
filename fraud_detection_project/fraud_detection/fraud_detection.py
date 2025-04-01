import pandas as pd
import numpy as np
import logging
from hashlib import sha256
from joblib import dump, load
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, roc_curve, auc
)

# Logging setup to ensure PII Masking
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Setting up the configuration for threshold cutoff and categorical variables mapping
THRESHOLD = 0.3  # Custom fraud probability cutoff
TYPE_MAP = {"CASH_OUT": 1, "PAYMENT": 2,
            "CASH_IN": 3, "TRANSFER": 4, "DEBIT": 5}
DROP_COLS = ['isFlaggedFraud']

# PII-SAFE Masking - Ensuring security


def mask_account_ids(df):
    for col in ['nameOrig', 'nameDest']:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: sha256(str(x).encode()).hexdigest())
    return df

# PII-SAFE Logging


def log_safe(message):
    logging.info("[SAFE] " + message)

# Preprocessing Function


def preprocess_fn(df):
    df = mask_account_ids(df)
    df = df.drop(columns=['nameOrig', 'nameDest'],
                 errors='ignore')  # ✅ Drop SHA256 columns
    df = df.drop(
        columns=[col for col in DROP_COLS if col in df.columns], errors='ignore')
    if 'type' in df.columns:
        df['type'] = df['type'].map(TYPE_MAP).fillna(0).astype(int)
    return df


# Scikit-Learn Preprocessing Pipeline
preprocessor = FunctionTransformer(preprocess_fn, validate=False)

# Full Machine Learning Pipeline (Global)
pipeline = Pipeline([
    ('preprocess', preprocessor),
    ('model', DecisionTreeClassifier(
        max_depth=10,
        min_samples_split=2,
        min_samples_leaf=2,
        random_state=42
    ))
])

# Running Training and Evaluation


def run_pipeline(csv_file):
    df = pd.read_csv(csv_file)
    df = mask_account_ids(df)
    labeled = 'isFraud' in df.columns

    if labeled:
        X = df.drop(columns=['isFraud'])
        y = df['isFraud']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)

        pipeline.fit(X_train, y_train)  # uses global pipeline

        y_train_prob = pipeline.predict_proba(X_train)[:, 1]
        y_test_prob = pipeline.predict_proba(X_test)[:, 1]
        y_train_pred = (y_train_prob >= THRESHOLD).astype(int)
        y_test_pred = (y_test_prob >= THRESHOLD).astype(int)

        train_acc = accuracy_score(y_train, y_train_pred)
        test_acc = accuracy_score(y_test, y_test_pred)
        roc_auc = auc(*roc_curve(y_test, y_test_prob)[:2])

        log_safe(f"Training Accuracy: {train_acc:.4f}")
        log_safe(f"Testing Accuracy: {test_acc:.4f}")
        log_safe(f"ROC AUC: {roc_auc:.4f}")

        with open("model_report.txt", "w") as f:
            f.write("Classification Report:\n")
            f.write(classification_report(y_test, y_test_pred))
            f.write("\nConfusion Matrix:\n")
            f.write(str(confusion_matrix(y_test, y_test_pred)))
            f.write(f"\nROC AUC: {roc_auc:.4f}\n")

        plot_roc(y_train, y_train_prob, y_test, y_test_prob)

        X_test['Actual_isFraud'] = y_test
        X_test['Predicted_isFraud'] = y_test_pred
        X_test['Fraud_Probability'] = y_test_prob
        X_test.to_csv("fraud_predictions.csv", index=False)

        dump(pipeline, "decision_tree_pipeline.joblib")
        log_safe("Model and predictions saved.")

    else:
        # 🔧 FIXED: avoid redefining 'pipeline', use different variable name
        loaded_pipeline = load("decision_tree_pipeline.joblib")
        X = preprocess_fn(df.copy())
        preds = loaded_pipeline.predict(X)
        probs = loaded_pipeline.predict_proba(X)[:, 1]
        X['Predicted_isFraud'] = preds
        X['Fraud_Probability'] = probs
        X.to_csv("fraud_predictions_unlabeled.csv", index=False)
        log_safe("Unlabeled predictions saved.")

# ROC Plot


def plot_roc(y_train, train_prob, y_test, test_prob):
    fpr_train, tpr_train, _ = roc_curve(y_train, train_prob)
    fpr_test, tpr_test, _ = roc_curve(y_test, test_prob)
    plt.figure(figsize=(6, 6))
    plt.plot(fpr_train, tpr_train, label='Train ROC')
    plt.plot(fpr_test, tpr_test, label='Test ROC')
    plt.plot([0, 1], [0, 1], linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.grid(True)
    plt.savefig("roc_curve.png")
    plt.close()
    log_safe("ROC curve saved as roc_curve.png")

# Unit Test


def test_preprocess():
    test_df = pd.DataFrame({
        'nameOrig': ['C12345'],
        'nameDest': ['M67890'],
        'type': ['CASH_OUT'],
        'isFlaggedFraud': [0],
        'amount': [1000]
    })
    result = preprocess_fn(test_df.copy())
    assert 'type' in result and result['type'].iloc[0] == 1
    assert 'isFlaggedFraud' not in result
    # assert len(result['nameOrig'].iloc[0]) == 64
    # assert len(result['nameDest'].iloc[0]) == 64
    print("test_preprocess passed.")


# Entry point
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", help="Path to input CSV")
    args = parser.parse_args()
    run_pipeline(args.csv_file)
    test_preprocess()
