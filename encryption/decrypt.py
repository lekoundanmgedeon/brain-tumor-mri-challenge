import sys
import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes, serialization, padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def decrypt_file(enc_path: str, private_key_path: str, output_path: str):
    if not os.path.exists(enc_path):
        print(f"[ERROR] Fichier .enc introuvable: {enc_path}"); sys.exit(1)

    # --- Chargement de la clé privée ---
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    # --- Lecture du bundle JSON ---
    with open(enc_path, "r") as f:
        bundle = json.load(f)

    encrypted_aes_key = base64.b64decode(bundle["encrypted_key"])
    iv = base64.b64decode(bundle["iv"])
    ciphertext = base64.b64decode(bundle["ciphertext"])

    # --- Déchiffrement de la clé AES avec RSA ---
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # --- Déchiffrement des données avec AES ---
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    # Retrait du padding PKCS7
    unpadder = sym_padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    # --- Sauvegarde du résultat ---
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(data)

    print(f"[SUCCESS] Fichier déchiffré : {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python decrypt.py <enc_file> <priv_key> <output>")
        sys.exit(1)
    decrypt_file(sys.argv[1], sys.argv[2], sys.argv[3])