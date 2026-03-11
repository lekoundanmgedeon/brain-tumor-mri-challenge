"""
evaluate.py — Brain Tumor MRI Challenge
Score a decrypted predictions CSV against hidden test labels.

Usage (called by GitHub Actions):
    python evaluation/evaluate.py <predictions.csv> <hidden_labels.csv> <team_name>
"""

import sys
import os
import csv
import json
from datetime import datetime

try:
    from sklearn.metrics import f1_score, accuracy_score, classification_report
except ImportError:
    print("[ERROR] scikit-learn is required: pip install scikit-learn")
    sys.exit(1)


CLASS_NAMES = {0: "glioma", 1: "meningioma", 2: "no_tumor", 3: "pituitary"}
VALID_LABELS = set(CLASS_NAMES.keys())


def load_csv(path):
    """Load CSV with columns: filename, prediction"""
    data = {}
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fn = row["filename"].strip()
            try:
                pred = int(row["prediction"].strip())
            except ValueError:
                print(f"[ERROR] Non-integer prediction for {fn}: {row['prediction']}")
                sys.exit(1)
            if pred not in VALID_LABELS:
                print(f"[ERROR] Invalid label {pred} for {fn}. Must be 0-3.")
                sys.exit(1)
            data[fn] = pred
    return data


def evaluate(predictions_path, labels_path, team_name):
    preds = load_csv(predictions_path)
    labels = load_csv(labels_path)

    # Check coverage
    missing = [f for f in labels if f not in preds]
    extra = [f for f in preds if f not in labels]

    if missing:
        print(f"[WARNING] {len(missing)} test images not in submission:")
        for m in missing[:5]:
            print(f"   - {m}")
        if len(missing) > 5:
            print(f"   ... and {len(missing)-5} more")

    if extra:
        print(f"[WARNING] {len(extra)} filenames in submission not in test set (ignored)")

    # Align on test set order
    common = [f for f in labels if f in preds]
    if len(common) == 0:
        print("[ERROR] No matching filenames between submission and test labels.")
        sys.exit(1)

    y_true = [labels[f] for f in common]
    y_pred = [preds[f] for f in common]

    # For missing images: predict majority class (penalizes incomplete submissions)
    if missing:
        majority = max(set(y_true), key=y_true.count)
        y_true += [labels[f] for f in missing]
        y_pred += [majority] * len(missing)
        print(f"[INFO] Missing {len(missing)} predictions → assigned majority class label ({majority})")

    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average="weighted")
    f1_macro = f1_score(y_true, y_pred, average="macro")

    print("\n" + "="*55)
    print(f"  RESULTS FOR: {team_name}")
    print("="*55)
    print(f"  Accuracy          : {acc:.4f} ({acc*100:.2f}%)")
    print(f"  F1 Score (weighted): {f1:.4f}")
    print(f"  F1 Score (macro)   : {f1_macro:.4f}")
    print(f"  Coverage           : {len(common)}/{len(labels)} images")
    print("="*55)
    print("\nPer-class report:")
    print(classification_report(y_true, y_pred, target_names=list(CLASS_NAMES.values())))

    result = {
        "team": team_name,
        "accuracy": round(acc, 6),
        "f1_weighted": round(f1, 6),
        "f1_macro": round(f1_macro, 6),
        "coverage": len(common),
        "total": len(labels),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    }

    # Save result to JSON for leaderboard updater
    result_path = f"evaluation/results/{team_name}.json"
    os.makedirs("evaluation/results", exist_ok=True)
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n[INFO] Result saved to {result_path}")

    return result


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    evaluate(sys.argv[1], sys.argv[2], sys.argv[3])
