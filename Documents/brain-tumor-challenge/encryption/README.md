# 🔒 Encryption Guide

This folder contains everything you need to encrypt your submission before the Pull Request.

## Files

| File | Purpose |
|------|---------|
| `public_key.pem` | RSA-2048 public key — use this to encrypt |
| `encrypt.py` | Encryption script |

## How to Encrypt

```bash
python encryption/encrypt.py \
  submissions/your_team_name.csv \
  encryption/public_key.pem \
  submissions/your_team_name.enc
```

## How It Works

Your predictions CSV is encrypted using **AES-256-CBC** (hybrid encryption):
1. A random AES-256 key is generated
2. Your CSV is encrypted with AES-256-CBC
3. The AES key is encrypted with the RSA public key
4. Both are bundled into `your_team.enc`

Only the organizer's **private key** (never exposed) can decrypt the `.enc` file.

## ⚠️ Important

- Only commit the `.enc` file — **never the `.csv`**
- One `.enc` file per Pull Request
- The `.enc` file is safe to share publicly — it's unreadable without the private key
