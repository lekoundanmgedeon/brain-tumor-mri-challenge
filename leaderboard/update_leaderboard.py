import os
import json
import pandas as pd

# ─── CONFIGURATION ────────────────────────────────────────────────────────
RESULTS_DIR = "evaluation/results"
LEADERBOARD_FILE = "leaderboard/leaderboard.csv"
# ──────────────────────────────────────────────────────────────────────────

def update_leaderboard():
    all_results = []

    # 1. Scanner tous les fichiers JSON de résultats
    if not os.path.exists(RESULTS_DIR):
        print(f"[ERREUR] Le dossier {RESULTS_DIR} n'existe pas.")
        return

    json_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')]
    
    for file in json_files:
        team_name = file.replace('.json', '')
        file_path = os.path.join(RESULTS_DIR, file)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            all_results.append({
                "Team": team_name,
                "Accuracy": round(data.get("accuracy", 0), 4),
                "F1-Score": round(data.get("f1_score", 0), 4)
            })
        except Exception as e:
            print(f"[ERREUR] Impossible de lire {file}: {e}")

    if not all_results:
        print("[INFO] Aucun résultat trouvé.")
        return

    # 2. Créer le DataFrame et trier (par Accuracy puis F1-Score)
    df = pd.DataFrame(all_results)
    df = df.sort_values(by=["Accuracy", "F1-Score"], ascending=False)
    
    # Ajouter le rang (1, 2, 3...)
    df.insert(0, "Rank", range(1, len(df) + 1))

    # 3. Sauvegarder en CSV
    os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)
    df.to_csv(LEADERBOARD_FILE, index=False)
    
    print(f"[OK] Leaderboard mis à jour avec {len(all_results)} équipes.")
    print(df.to_string(index=False))

if __name__ == "__main__":
    update_leaderboard()