import pandas as pd
import os
import argparse
from sklearn.metrics import accuracy_score, classification_report, f1_score
import json

# ─── CONFIGURATION ────────────────────────────────────────────────────────
TRUTH_FILE = "evaluation/true_labels.csv"
RESULTS_DIR = "evaluation/results"
# ──────────────────────────────────────────────────────────────────────────

def evaluate_submission(submission_file):
    """
    Compare une soumission avec la vérité terrain et calcule les scores.
    Gère les erreurs d'en-têtes et les problèmes de formatage.
    """
    print(f"[INFO] Évaluation du fichier : {submission_file}")

    if not os.path.exists(TRUTH_FILE):
        print(f"[ERREUR] Vérité terrain introuvable : {TRUTH_FILE}")
        return None

    try:
        # Lecture des fichiers
        df_truth = pd.read_csv(TRUTH_FILE)
        df_pred = pd.read_csv(submission_file)

        # 1. Normalisation stricte des colonnes (minuscules + sans espaces)
        df_truth.columns = [c.strip().lower() for c in df_truth.columns]
        df_pred.columns = [c.strip().lower() for c in df_pred.columns]

        # 2. Vérification de la colonne indispensable 'filename'
        if 'filename' not in df_pred.columns:
            print("[ERREUR] La colonne 'filename' est manquante dans votre CSV.")
            return None

        # 3. Flexibilité sur la colonne de prédiction
        # Le participant peut utiliser 'prediction' ou 'label'
        target_col = None
        for col in ['prediction', 'label']:
            if col in df_pred.columns:
                target_col = col
                break
        
        if not target_col:
            print("[ERREUR] Aucune colonne de prédiction trouvée ('prediction' ou 'label' attendu).")
            return None

        # 4. Nettoyage des données (suppression des espaces dans les noms de fichiers)
        df_truth['filename'] = df_truth['filename'].astype(str).str.strip()
        df_pred['filename'] = df_pred['filename'].astype(str).str.strip()

        # 5. Alignement des données sur 'filename'
        # On utilise un inner merge pour ne comparer que ce qui matche
        df_merged = pd.merge(df_truth, df_pred, on="filename", suffixes=("_true", "_pred"))

        # Debugging pour t'aider en cas de soucis
        print(f"[DEBUG] Lignes Truth: {len(df_truth)} | Lignes Pred: {len(df_pred)} | Match: {len(df_merged)}")

        if len(df_merged) == 0:
            print("[ERREUR] Aucun nom de fichier ne correspond entre votre CSV et la vérité terrain.")
            print(f"Exemple attendu: '{df_truth['filename'].iloc[0]}'")
            print(f"Exemple reçu: '{df_pred['filename'].iloc[0]}'")
            return None

        # 6. Extraction des vecteurs (on utilise 'label' pour la vérité car c'est ton en-tête)
        y_true = df_merged["label"]
        y_pred = df_merged[target_col]

        # 7. Calcul des métriques
        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average="weighted")
        
        # Le rapport de classification (on ignore les erreurs si les classes manquent)
        report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

        print(f"--- RÉSULTATS ---")
        print(f"Accuracy : {acc:.4f} | F1-Score : {f1:.4f}")
        
        return {
            "accuracy": acc,
            "f1_score": f1,
            "details": report
        }

    except Exception as e:
        print(f"[ERREUR SYSTEME] : {e}")
        return None

def save_results(team_name, metrics):
    """Sauvegarde les scores dans un fichier JSON pour le leaderboard."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output_path = os.path.join(RESULTS_DIR, f"{team_name}.json")
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=4)
    print(f"[OK] Résultats sauvegardés dans {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Évaluation MRI Challenge")
    parser.add_argument("--submission", type=str, required=True, help="Chemin vers le CSV")
    args = parser.parse_args()

    if os.path.exists(args.submission):
        # Nettoyage du nom de l'équipe
        team_name = os.path.basename(args.submission).lower().replace(".csv", "").replace(" ", "_")
        
        results = evaluate_submission(args.submission)
        if results:
            save_results(team_name, results)
    else:
        print(f"[!] Erreur : Le fichier {args.submission} est introuvable.")