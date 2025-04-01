import pandas as pd
import numpy as np
import logging
import os
from hashlib import sha256
from joblib import dump, load
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, roc_curve, auc
)

# 🔧 Configuration
THRESHOLD = 0.3
TYPE_MAP = {"CASH_OUT": 1, "PAYMENT": 2,
            "CASH_IN": 3, "TRANSFER": 4, "DEBIT": 5}
DROP_COLS = ['isFlaggedFraud']

# Output directory setup
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "Outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🧪 PII-safe Logging Setup
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


def log_safe(message): logging.info("[SAFE] " + message)

# ---------------------------------------------------
# 🧼 Preprocessing Functions
# ---------------------------------------------------


def mask_account_ids(df):
    for col in ['nameOrig', 'nameDest']:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: sha256(str(x).encode()).hexdigest())
    return df


def preprocess_fn(df):
    df = mask_account_ids(df)
    df = df.drop(columns=['nameOrig', 'nameDest'], errors='ignore')
    df = df.drop(
        columns=[col for col in DROP_COLS if col in df.columns], errors='ignore')
    if 'type' in df.columns:
        df['type'] = df['type'].map(TYPE_MAP).fillna(0).astype(int)
    return df

# ---------------------------------------------------
# 🧪 Unit test for preprocessing
# ---------------------------------------------------


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
    assert 'nameOrig' not in result and 'nameDest' not in result
    print("✅ test_preprocess passed.")


# ---------------------------------------------------
# 🧠 Model pipeline
# ---------------------------------------------------
preprocessor = FunctionTransformer(preprocess_fn, validate=False)

pipeline = Pipeline([
    ('preprocess', preprocessor),
    ('model', DecisionTreeClassifier(
        max_depth=10,
        min_samples_split=2,
        min_samples_leaf=2,
        random_state=42
    ))
])

# ---------------------------------------------------
# 🗃️ Load data from SQLite DB
# ---------------------------------------------------


def load_data_from_db(db_path, table_name="transactions"):
    engine = create_engine(f"sqlite:///{db_path}")
    df = pd.read_sql_table(table_name, con=engine)
    log_safe(f"Loaded {len(df)} records from {db_path}")
    return df

# ---------------------------------------------------
# 💾 Save predictions to DB
# ---------------------------------------------------


def write_predictions_to_db(df, db_path, table_name="predictions"):
    engine = create_engine(f"sqlite:///{db_path}")
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    log_safe(f"Predictions written to {db_path} → {table_name}")

# ---------------------------------------------------
# 📈 Plot ROC curve
# ---------------------------------------------------


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
    roc_path = os.path.join(OUTPUT_DIR, "roc_curve.png")
    plt.savefig(roc_path)
    plt.close()
    log_safe(f"ROC curve saved as {roc_path}")

# ---------------------------------------------------
# 🚀 Main pipeline logic
# ---------------------------------------------------


def run_pipeline(input_path, is_db=False, save_to_db=False, output_db_path=None):
    df = load_data_from_db(input_path) if is_db else pd.read_csv(input_path)
    df = mask_account_ids(df)
    labeled = 'isFraud' in df.columns

    if labeled:
        X = df.drop(columns=['isFraud'])
        y = df['isFraud']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)

        pipeline.fit(X_train, y_train)

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

        report_path = os.path.join(OUTPUT_DIR, "model_report.txt")
        with open(report_path, "w") as f:
            f.write("Classification Report:\n")
            f.write(classification_report(y_test, y_test_pred))
            f.write("\nConfusion Matrix:\n")
            f.write(str(confusion_matrix(y_test, y_test_pred)))
            f.write(f"\nROC AUC: {roc_auc:.4f}\n")

        plot_roc(y_train, y_train_prob, y_test, y_test_prob)

        X_test['Actual_isFraud'] = y_test
        X_test['Predicted_isFraud'] = y_test_pred
        X_test['Fraud_Probability'] = y_test_prob
        pred_path = os.path.join(OUTPUT_DIR, "fraud_predictions.csv")
        X_test.to_csv(pred_path, index=False)

        if save_to_db and output_db_path:
            write_predictions_to_db(
                X_test, output_db_path, "predicted_results")

        model_path = os.path.join(OUTPUT_DIR, "decision_tree_pipeline.joblib")
        dump(pipeline, model_path)
        log_safe(f"Model and predictions saved to {OUTPUT_DIR}.")

    else:
        loaded_pipeline = load(os.path.join(
            OUTPUT_DIR, "decision_tree_pipeline.joblib"))
        X = preprocess_fn(df.copy())
        preds = loaded_pipeline.predict(X)
        probs = loaded_pipeline.predict_proba(X)[:, 1]
        X['Predicted_isFraud'] = preds
        X['Fraud_Probability'] = probs
        pred_path = os.path.join(OUTPUT_DIR, "fraud_predictions_unlabeled.csv")
        X.to_csv(pred_path, index=False)

        if save_to_db and output_db_path:
            write_predictions_to_db(
                X, output_db_path, "predicted_results_unlabeled")

        log_safe("Unlabeled predictions saved.")


# ---------------------------------------------------
# 🏁 Entry point
# ---------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fraud Detection Pipeline")
    parser.add_argument("input", help="Path to CSV file or SQLite DB")
    parser.add_argument("--db", action="store_true",
                        help="Flag: read from database")
    parser.add_argument("--save-db", action="store_true",
                        help="Flag: write results to DB")
    parser.add_argument("--output-db", help="Path to output SQLite DB")

    args = parser.parse_args()

    run_pipeline(
        input_path=args.input,
        is_db=args.db,
        save_to_db=args.save_db,
        output_db_path=args.output_db
    )

    test_preprocess()
