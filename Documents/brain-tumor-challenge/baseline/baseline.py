"""
baseline.py — Brain Tumor MRI Challenge
EfficientNet-B0 baseline using PyTorch + torchvision.
Version : Sans encryption.
"""

import os
import csv
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR

# ─── CONFIG ──────────────────────────────────────────────────────────────
DATA_DIR      = "data"
TRAIN_DIR     = os.path.join(DATA_DIR, "Training")
TEST_DIR      = os.path.join(DATA_DIR, "Testing")
MODEL_SAVE    = "baseline/best_model.pth"
PRED_CSV      = "submissions/baseline_predictions.csv"
BATCH_SIZE    = 32
EPOCHS        = 20
IMG_SIZE      = 224
LR            = 1e-4
DEVICE        = "cuda" if torch.cuda.is_available() else "cpu"

CLASS_NAMES   = ["glioma", "meningioma", "no_tumor", "pituitary"]
# ─────────────────────────────────────────────────────────────────────────

def get_transforms(train=True):
    if train:
        return transforms.Compose([
            transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
            transforms.RandomCrop(IMG_SIZE),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

def build_model(num_classes=4):
    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes)
    )
    return model.to(DEVICE)

def train():
    print(f"[INFO] Entraînement sur : {DEVICE}")

    train_ds = datasets.ImageFolder(TRAIN_DIR, transform=get_transforms(train=True))
    val_ds   = datasets.ImageFolder(TEST_DIR,  transform=get_transforms(train=False))

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=4)
    val_loader   = DataLoader(val_ds,  batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

    print(f"[INFO] Train: {len(train_ds)} images | Val: {len(val_ds)} images")
    
    model     = build_model()
    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=EPOCHS)

    best_acc = 0.0
    os.makedirs("baseline", exist_ok=True)

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss, correct = 0, 0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            out  = model(imgs)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * imgs.size(0)
            correct    += (out.argmax(1) == labels).sum().item()
        
        scheduler.step()
        train_acc = correct / len(train_ds)

        model.eval()
        val_correct = 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                out = model(imgs)
                val_correct += (out.argmax(1) == labels).sum().item()
        
        val_acc = val_correct / len(val_ds)

        print(f"Epoch {epoch:02d}/{EPOCHS} | Loss: {total_loss/len(train_ds):.4f} | "
              f"Train Acc: {train_acc:.4f} | Val Acc: {val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), MODEL_SAVE)
            print(f"  ✓ Meilleur modèle sauvegardé ({best_acc:.4f})")

    print(f"\n[DONE] Meilleure précision validation : {best_acc:.4f}")
    return best_acc

def predict():
    """Génère le fichier CSV final sans encryption."""
    print("[INFO] Génération des prédictions...")

    if not os.path.exists(MODEL_SAVE):
        print(f"[ERREUR] Aucun modèle trouvé à {MODEL_SAVE}. Lancez d'abord l'entraînement.")
        return

    test_transform = get_transforms(train=False)
    test_ds = datasets.ImageFolder(TEST_DIR, transform=test_transform)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

    # Récupérer les noms de fichiers
    img_paths = [os.path.basename(p) for p, _ in test_ds.imgs]

    model = build_model()
    model.load_state_dict(torch.load(MODEL_SAVE, map_location=DEVICE))
    model.eval()

    all_preds = []
    with torch.no_grad():
        for imgs, _ in test_loader:
            imgs = imgs.to(DEVICE)
            out  = model(imgs)
            preds = out.argmax(1).cpu().tolist()
            all_preds.extend(preds)

    os.makedirs("submissions", exist_ok=True)
    with open(PRED_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "prediction"])
        for fname, pred in zip(img_paths, all_preds):
            writer.writerow([fname, pred])

    print(f"[OK] {len(all_preds)} prédictions enregistrées dans {PRED_CSV}")
    print(f"Index : 0=glioma, 1=meningioma, 2=no_tumor, 3=pituitary")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["train", "predict", "all"], default="all")
    args = parser.parse_args()

    if args.mode in ("train", "all"):
        train()
    if args.mode in ("predict", "all"):
        predict()
