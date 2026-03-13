import os
import csv

# CONFIGURATION
TEST_DIR = "data/test"  # Chemin vers vos images de test
OUTPUT_FILE = "evaluation/true_labels.csv"

# L'ordre doit être identique à celui utilisé par le modèle (ordre alphabétique par défaut)
# 0: glioma, 1: meningioma, 2: notumor, 3: pituitary
CLASS_NAMES = sorted([d for d in os.listdir(TEST_DIR) if os.path.isdir(os.path.join(TEST_DIR, d))])

def generate_truth_file():
    print(f"[INFO] Classes détectées : {CLASS_NAMES}")
    
    truth_data = []
    
    # Parcourir chaque dossier de classe dans le répertoire de test
    for class_index, class_name in enumerate(CLASS_NAMES):
        class_path = os.path.join(TEST_DIR, class_name)
        
        # Lister toutes les images dans ce dossier
        for img_name in os.listdir(class_path):
            # On ne garde que le nom du fichier pour la comparaison
            truth_data.append([img_name, class_index])

    # Tri par nom de fichier pour garantir une cohérence avec les soumissions
    truth_data.sort(key=lambda x: x[0])

    # Écriture du fichier CSV
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "label"])
        writer.writerows(truth_data)

    print(f"[OK] Fichier de vérité terrain généré : {OUTPUT_FILE}")
    print(f"Total images : {len(truth_data)}")

if __name__ == "__main__":
    generate_truth_file()