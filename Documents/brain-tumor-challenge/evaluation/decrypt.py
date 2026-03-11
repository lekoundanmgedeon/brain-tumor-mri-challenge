"""
decrypt.py — Brain Tumor MRI Challenge (ORGANIZER / CI USE ONLY)
Decrypt a participant's .enc submission file.

Usage:
    python evaluation/decrypt.py <submission.enc> <private_key.pem> <output.csv>
"""

import sys
import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def decrypt_file(enc_path: str, private_key_path: str, output_path: str):
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    with open(enc_path, "r") as f:
        bundle = json.load(f)

    encrypted_aes_key = base64.b64decode(bundle["encrypted_key"])
    iv = base64.b64decode(bundle["iv"])
    ciphertext = base64.b64decode(bundle["ciphertext"])

    # Decrypt AES key with RSA private key
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt data with AES-256-CBC
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

    # Remove padding
    pad_len = decrypted_padded[-1]
    decrypted = decrypted_padded[:-pad_len]

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(decrypted)

    print(f"[OK] Decrypted to: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    decrypt_file(sys.argv[1], sys.argv[2], sys.argv[3])
