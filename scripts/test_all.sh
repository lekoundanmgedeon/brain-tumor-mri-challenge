#!/bin/bash

# Arrêter le script en cas d'erreur
set -e

echo "🚀 Démarrage du test d'intégration local..."

# 1. Nettoyage des anciens fichiers de test
echo "[1/6] Nettoyage..."
rm -f evaluation/true_labels.csv
rm -f submissions/current_submission.csv
rm -rf evaluation/results/*.json

# 2. Simulation : Déchiffrement de la Vérité Terrain
# Note : On suppose que tu as ta private_key.pem dans scripts/
echo "[2/6] Déchiffrement de la vérité terrain..."
python evaluation/decrypt.py \
    evaluation/true_labels.csv.enc \
    scripts/private_key.pem \
    evaluation/true_labels.csv

# 3. Simulation : Choix d'une soumission
# On prend la première disponible dans submissions/
SUB_FILE=$(ls submissions/*.csv | head -n 1)
echo "[3/6] Soumission détectée : $SUB_FILE"

# 4. Évaluation
echo "[4/6] Lancement de l'évaluation..."
python evaluation/evaluate.py --submission "$SUB_FILE"

# 5. Mise à jour du Leaderboard
echo "[5/6] Mise à jour du classement..."
python leaderboard/update_leaderboard.py

# 6. Vérification finale
echo "[6/6] Vérification des fichiers générés..."
if [ -f "leaderboard/leaderboard.csv" ]; then
    echo "✅ SUCCÈS : Le leaderboard a été généré."
    tail -n 5 leaderboard/leaderboard.csv
else
    echo "❌ ERREUR : Le leaderboard est manquant."
    exit 1
fi

echo "🎉 Tout est prêt pour être poussé sur GitHub !"