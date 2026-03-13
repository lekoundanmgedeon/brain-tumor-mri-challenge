import sys
import os
import json
import base64
import secrets
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes, serialization, padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt_file(csv_path: str, public_key_path: str, output_path: str):
    # --- Validations de base ---
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV introuvable: {csv_path}"); sys.exit(1)
    
    # --- Chargement de la clé publique ---
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    # --- Lecture et Validation du CSV ---
    try:
        with open(csv_path, "rb") as f:
            data = f.read()
        content = data.decode("utf-8").strip().split("\n")
        if len(content) < 2 or "filename" not in content[0].lower():
            raise ValueError("Format CSV invalide ou fichier vide.")
    except Exception as e:
        print(f"[ERROR] Échec de lecture du CSV: {e}"); sys.exit(1)

    # --- Chiffrement AES-256 (Symétrique) ---
    aes_key = secrets.token_bytes(32)
    iv = secrets.token_bytes(16)
    
    # Padding PKCS7
    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # --- Chiffrement de la clé AES avec RSA (Asymétrique) ---
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # --- Export en format JSON ---
    bundle = {
        "version": "1.1",
        "encrypted_key": base64.b64encode(encrypted_aes_key).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
    }

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(bundle, f, indent=2)

    print(f"[SUCCESS] Fichier chiffré : {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python encrypt.py <csv> <pub_key> <output>")
        sys.exit(1)
    encrypt_file(sys.argv[1], sys.argv[2], sys.argv[3])