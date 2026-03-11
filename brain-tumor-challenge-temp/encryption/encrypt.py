"""
encrypt.py — Brain Tumor MRI Challenge
Encrypt your predictions CSV before submitting via Pull Request.

Usage:
    python encryption/encrypt.py <predictions.csv> <public_key.pem> <output.enc>

Example:
    python encryption/encrypt.py submissions/team_alpha.csv encryption/public_key.pem submissions/team_alpha.enc
"""

import sys
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets
import json
import base64


def encrypt_file(csv_path: str, public_key_path: str, output_path: str):
    # --- Validate inputs ---
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found: {csv_path}")
        sys.exit(1)
    if not csv_path.endswith(".csv"):
        print("[ERROR] Input file must be a .csv file")
        sys.exit(1)
    if not output_path.endswith(".enc"):
        print("[WARNING] Output file should end with .enc")

    # --- Load public key ---
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    # --- Read CSV content ---
    with open(csv_path, "rb") as f:
        data = f.read()

    # --- Validate CSV structure ---
    lines = data.decode("utf-8").strip().split("\n")
    if not lines[0].strip().lower().startswith("filename,prediction"):
        print("[ERROR] CSV must start with header: filename,prediction")
        print(f"       Got: {lines[0]}")
        sys.exit(1)
    print(f"[INFO] Found {len(lines) - 1} predictions in CSV")

    # --- Generate AES-256 symmetric key + IV ---
    aes_key = secrets.token_bytes(32)   # 256 bits
    iv = secrets.token_bytes(16)        # 128 bits

    # --- Encrypt data with AES-256-CBC ---
    # Pad data to block size
    pad_len = 16 - (len(data) % 16)
    data_padded = data + bytes([pad_len] * pad_len)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data_padded) + encryptor.finalize()

    # --- Encrypt AES key with RSA public key ---
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # --- Bundle everything ---
    bundle = {
        "version": "1.0",
        "encrypted_key": base64.b64encode(encrypted_aes_key).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(encrypted_data).decode(),
    }

    # --- Save to .enc file ---
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(bundle, f, indent=2)

    print(f"[SUCCESS] Encrypted submission saved to: {output_path}")
    print(f"[INFO] File size: {os.path.getsize(output_path)} bytes")
    print()
    print("Next steps:")
    print(f"  git add {output_path}")
    print(f"  git commit -m 'Submission: <Your Team Name>'")
    print(f"  git push origin <your-branch>")
    print("  Then open a Pull Request!")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    csv_path, public_key_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]
    encrypt_file(csv_path, public_key_path, output_path)
