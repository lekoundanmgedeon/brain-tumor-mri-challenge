import os
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR

from model import build_model, get_transforms

# CONFIG
TRAIN_DIR  = "data/train"
TEST_DIR   = "data/test"
MODEL_SAVE = "baseline/best_model.pth"
BATCH_SIZE = 32
EPOCHS     = 20
LR         = 1e-4
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"

def train():
    print(f"[INFO] Entraînement sur : {DEVICE}")
    os.makedirs("baseline", exist_ok=True)

    train_ds = datasets.ImageFolder(TRAIN_DIR, transform=get_transforms(train=True))
    val_ds   = datasets.ImageFolder(TEST_DIR,  transform=get_transforms(train=False))

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader   = DataLoader(val_ds,  batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

    model     = build_model(num_classes=len(train_ds.classes), device=DEVICE)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=EPOCHS)

    best_acc = 0.0
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
        
        # Validation
        model.eval()
        val_correct = 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                out = model(imgs)
                val_correct += (out.argmax(1) == labels).sum().item()
        
        val_acc = val_correct / len(val_ds)
        print(f"Epoch {epoch:02d} | Train Acc: {correct/len(train_ds):.4f} | Val Acc: {val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), MODEL_SAVE)
            print(f"  ✓ Modèle sauvegardé")

if __name__ == "__main__":
    train()