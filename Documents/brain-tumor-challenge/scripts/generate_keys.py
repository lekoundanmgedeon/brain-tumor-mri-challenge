"""
generate_keys.py — Organizer utility
Generate a new RSA-2048 key pair for the competition.

Usage:
    python scripts/generate_keys.py

Outputs:
    encryption/public_key.pem   (commit to repo)
    scripts/private_key.pem     (ADD TO GITHUB SECRETS, never commit)
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key  = private_key.public_key()

    os.makedirs("encryption", exist_ok=True)
    os.makedirs("scripts", exist_ok=True)

    with open("encryption/public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    with open("scripts/private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ))

    print("✓ Keys generated:")
    print("  encryption/public_key.pem  → commit to repo")
    print("  scripts/private_key.pem    → add to GitHub Secrets as PRIVATE_KEY")
    print()
    print("To add to GitHub Secrets:")
    print("  Settings → Secrets and variables → Actions → New repository secret")
    print("  Name: PRIVATE_KEY")
    print("  Value: paste the entire contents of scripts/private_key.pem")
    print()
    print("⚠️  Do NOT commit scripts/private_key.pem!")


if __name__ == "__main__":
    generate_keys()
