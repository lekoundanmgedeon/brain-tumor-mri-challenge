"""
update_leaderboard.py — Brain Tumor MRI Challenge
Called by GitHub Actions after evaluation to update leaderboard.csv.

Usage:
    python leaderboard/update_leaderboard.py <result.json>
"""

import sys
import os
import csv
import json
from datetime import datetime

LEADERBOARD_PATH = "leaderboard/leaderboard.csv"
FIELDNAMES = ["rank", "team", "accuracy", "f1_weighted", "f1_macro",
              "coverage", "total", "submissions", "last_updated"]


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_PATH):
        return {}
    teams = {}
    with open(LEADERBOARD_PATH, "r") as f:
        for row in csv.DictReader(f):
            teams[row["team"]] = row
    return teams


def save_leaderboard(teams: dict):
    # Sort by f1_weighted descending, then accuracy
    sorted_teams = sorted(
        teams.values(),
        key=lambda x: (float(x["f1_weighted"]), float(x["accuracy"])),
        reverse=True
    )
    with open(LEADERBOARD_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for rank, row in enumerate(sorted_teams, 1):
            row["rank"] = rank
            writer.writerow(row)
    print(f"[OK] Leaderboard saved with {len(sorted_teams)} teams")


def update_leaderboard(result_path: str):
    with open(result_path, "r") as f:
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
            print(f"[INFO] Score not improved for {team}: {result['f1_weighted']} < {prev['f1_weighted']} (keeping previous)")
            # Still update submission count
            teams[team]["submissions"] = submissions
            teams[team]["last_updated"] = result["timestamp"]
            save_leaderboard(teams)
            return
    else:
        submissions = 1
        print(f"[INFO] New team on leaderboard: {team}")

    teams[team] = {
        "rank": 0,  # will be computed in save
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

    # Print leaderboard summary
    print("\n🏆 CURRENT LEADERBOARD")
    print(f"{'Rank':<6} {'Team':<30} {'F1 (weighted)':<15} {'Accuracy':<12}")
    print("-" * 65)
    with open(LEADERBOARD_PATH) as f:
        for row in csv.DictReader(f):
            medal = {"1": "🥇", "2": "🥈", "3": "🥉"}.get(row["rank"], "  ")
            print(f"{medal} {row['rank']:<4} {row['team']:<30} {row['f1_weighted']:<15} {row['accuracy']:<12}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    update_leaderboard(sys.argv[1])
