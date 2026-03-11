import sys
import os
import csv
import json
import re
from datetime import datetime

LEADERBOARD_PATH = "leaderboard/leaderboard.csv"
README_PATH = "README.md"
FIELDNAMES = ["rank", "team", "accuracy", "f1_weighted", "f1_macro",
              "coverage", "total", "submissions", "last_updated"]

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_PATH):
        return {}
    teams = {}
    with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            teams[row["team"]] = row
    return teams

def update_readme(sorted_teams):
    """Génère un tableau Markdown et l'injecte dans le README.md"""
    if not os.path.exists(README_PATH):
        print("[WARN] README.md non trouvé, injection annulée.")
        return

    # Préparation du tableau Markdown
    headers = ["Rank", "Team", "F1 Score (weighted)", "Accuracy", "Submissions", "Last Update"]
    separator = ["---"] * len(headers)
    
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(separator) + " |"]
    
    for row in sorted_teams:
        medal = {"1": "🥇", "2": "🥈", "3": "🥉"}.get(str(row["rank"]), "")
        rank_str = f"{medal} {row['rank']}" if medal else row['rank']
        
        line = [
            str(rank_str),
            f"**{row['team']}**",
            f"`{float(row['f1_weighted']):.4f}`",
            f"`{float(row['accuracy']):.4f}`",
            str(row['submissions']),
            row['last_updated'].split('T')[0] # Garde juste la date
        ]
        lines.append("| " + " | ".join(line) + " |")
    
    markdown_table = "\n".join(lines)

    # Injection dans le README
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r".*"
    replacement = f"\n\n{markdown_table}\n\n"
    
    if "" in content:
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("[OK] README.md mis à jour")
    else:
        print("[WARN] Balises manquantes dans le README.md")

def save_leaderboard(teams: dict):
    # Sort by f1_weighted descending, then accuracy
    sorted_teams = sorted(
        teams.values(),
        key=lambda x: (float(x["f1_weighted"]), float(x["accuracy"])),
        reverse=True
    )
    
    for rank, row in enumerate(sorted_teams, 1):
        row["rank"] = rank

    # Sauvegarde CSV
    with open(LEADERBOARD_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(sorted_teams)
    
    print(f"[OK] Leaderboard saved with {len(sorted_teams)} teams")
    
    # Mise à jour du README
    update_readme(sorted_teams)

def update_leaderboard(result_path: str):
    with open(result_path, "r", encoding="utf-8") as f:
        result = json.load(f)

    teams = load_leaderboard()
    team = result["team"]

    if team in teams:
        prev = teams[team]
        submissions = int(prev.get("submissions", 0)) + 1
        # Keep best score only
        if float(result["f1_weighted"]) > float(prev["f1_weighted"]):
            print(f"[INFO] New best score for {team}: {result['f1_weighted']} (was {prev['f1_weighted']})")
        else:
            print(f"[INFO] Score not improved for {team}. Keeping previous best.")
            # On met quand même à jour le nombre de soumissions et la date
            teams[team]["submissions"] = submissions
            teams[team]["last_updated"] = result["timestamp"]
            save_leaderboard(teams)
            return
    else:
        submissions = 1
        print(f"[INFO] New team: {team}")

    teams[team] = {
        "rank": 0,
        "team": team,
        "accuracy": result["accuracy"],
        "f1_weighted": result["f1_weighted"],
        "f1_macro": result["f1_macro"],
        "coverage": f"{result['coverage']}/{result['total']}",
        "total": result["total"],
        "submissions": submissions,
        "last_updated": result["timestamp"],
    }

    save_leaderboard(teams)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    update_leaderboard(sys.argv[1])
