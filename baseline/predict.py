import os
import csv
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from model import build_model, get_transforms

# CONFIG
TEST_DIR   = "data/test"
MODEL_SAVE = "baseline/best_model.pth"
PRED_CSV   = "submissions/baseline_predictions.csv"
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"

def predict():
    if not os.path.exists(MODEL_SAVE):
        print("[ERREUR] Modèle introuvable.")
        return

    test_ds = datasets.ImageFolder(TEST_DIR, transform=get_transforms(train=False))
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False)

    model = build_model(num_classes=len(test_ds.classes), device=DEVICE)
    model.load_state_dict(torch.load(MODEL_SAVE, map_location=DEVICE))
    model.eval()

    img_paths = [os.path.basename(p) for p, _ in test_ds.imgs]
    results = []

    print("[INFO] Inférence en cours...")
    with torch.no_grad():
        for imgs, _ in test_loader:
            imgs = imgs.to(DEVICE)
            out = model(imgs)
            preds = out.argmax(1).cpu().tolist()
            results.extend(preds)

    os.makedirs("submissions", exist_ok=True)
    with open(PRED_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "prediction"])
        for row in zip(img_paths, results):
            writer.writerow(row)

    print(f"[OK] Fichier créé : {PRED_CSV}")

if __name__ == "__main__":
    predict()