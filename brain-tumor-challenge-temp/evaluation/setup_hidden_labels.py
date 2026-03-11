"""
setup_hidden_labels.py — ORGANIZER USE ONLY
Run this script ONCE to generate the hidden test labels file from the Kaggle dataset.
The output (hidden_labels.enc) is stored in the repo — encrypted so participants cannot read it.

Usage:
    python evaluation/setup_hidden_labels.py \
        --test-dir data/Testing \
        --public-key encryption/public_key.pem \
        --private-key scripts/private_key.pem

IMPORTANT:
    - Run this before launching the competition
    - Commit hidden_labels.enc to the repo (it's encrypted, safe to share)
    - NEVER commit private_key.pem — add it to GitHub Secrets as PRIVATE_KEY
    - NEVER commit hidden_labels.csv — only the .enc version
"""

import os
import csv
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from encryption.encrypt import encrypt_file
from evaluation.decrypt import decrypt_file


CLASS_MAP = {"glioma": 0, "meningioma": 1, "no_tumor": 2, "pituitary": 3}


def build_labels(test_dir: str) -> list:
    """Walk test directory and build (filename, label) pairs."""
    rows = []
    for class_name, label in CLASS_MAP.items():
        class_dir = os.path.join(test_dir, class_name)
        if not os.path.isdir(class_dir):
            print(f"[WARNING] Class directory not found: {class_dir}")
            continue
        for fname in sorted(os.listdir(class_dir)):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                rows.append((fname, label))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-dir", default="data/Testing", help="Path to Testing/ folder")
    parser.add_argument("--public-key", default="encryption/public_key.pem")
    parser.add_argument("--private-key", default="scripts/private_key.pem")
    args = parser.parse_args()

    print("[STEP 1] Reading test labels from:", args.test_dir)
    rows = build_labels(args.test_dir)
    if not rows:
        print("[ERROR] No images found. Check --test-dir path.")
        sys.exit(1)
    print(f"[INFO] Found {len(rows)} test images across {len(CLASS_MAP)} classes")

    # Write hidden CSV
    csv_path = "evaluation/hidden_labels.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "prediction"])
        writer.writerows(rows)
    print(f"[STEP 2] Written: {csv_path}")

    # Encrypt it
    enc_path = "evaluation/hidden_labels.enc"
    encrypt_file(csv_path, args.public_key, enc_path)
    print(f"[STEP 3] Encrypted: {enc_path}")

    # Verify decryption works
    verify_path = "evaluation/hidden_labels_verify.csv"
    decrypt_file(enc_path, args.private_key, verify_path)
    with open(csv_path) as f1, open(verify_path) as f2:
        assert f1.read() == f2.read(), "Verification FAILED: encrypt/decrypt mismatch!"
    os.remove(verify_path)
    print("[STEP 4] Verification: PASSED ✓")

    # Remove plaintext labels
    os.remove(csv_path)
    print(f"[STEP 5] Removed plaintext {csv_path} — only .enc remains")

    print()
    print("=" * 55)
    print("  SETUP COMPLETE")
    print("=" * 55)
    print(f"  Commit to repo : {enc_path}")
    print(f"  Add to Secrets : PRIVATE_KEY = contents of {args.private_key}")
    print(f"  Total test imgs: {len(rows)}")
    for cls, lbl in CLASS_MAP.items():
        count = sum(1 for _, l in rows if l == lbl)
        print(f"    {lbl} ({cls}): {count}")
    print()
    print("  ⚠  NEVER commit scripts/private_key.pem to the repository!")


if __name__ == "__main__":
    main()
