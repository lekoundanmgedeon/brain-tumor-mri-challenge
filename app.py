import streamlit as st
import pandas as pd
import os
import plotly.express as px


def format_rank(rank):
    if rank == 1: return "🥇"
    if rank == 2: return "🥈"
    if rank == 3: return "🥉"
    return str(rank)

st.set_page_config(page_title="Brain Tumor Challenge Leaderboard", layout="wide")

st.title("🏆 Brain Tumor MRI Challenge - Leaderboard")
st.markdown("""
Bienvenue sur le tableau de bord officiel de la compétition. 
Les scores sont mis à jour automatiquement à chaque nouvelle soumission validée.
""")


# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=600)
def load_data():
    file_path = "leaderboard/leaderboard.csv"
    if os.path.exists(file_path):
        data = pd.read_csv(file_path)
        # Vérification si le CSV est vide ou n'a pas les colonnes attendues
        if data.empty or "Accuracy" not in data.columns:
            return None
        return data
    return None

df = load_data()

if df is not None:
    # --- MÉTRIQUES CLÉS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre d'équipes", len(df))
    # On utilise .get() ou on vérifie l'existence pour éviter le crash
    max_acc = df["Accuracy"].max() if "Accuracy" in df.columns else 0
    mean_f1 = df["F1-Score"].mean() if "F1-Score" in df.columns else 0
    
    col2.metric("Meilleure Accuracy", f"{max_acc:.4f}")
    col3.metric("Moyenne F1-Score", f"{mean_f1:.4f}")
    
    st.divider()

    # --- TABLEAU ET GRAPHIQUE ---
    left_column, right_column = st.columns([2, 1])

    with left_column:
        st.subheader("Classement Général")
        # Style pour mettre en valeur le Top 3
        st.dataframe(
            df.style.highlight_max(axis=0, subset=['Accuracy', 'F1-Score'], color='#2E7D32'),
            use_container_width=True,
            hide_index=True
        )

    with right_column:
        st.subheader("Distribution des Scores")
        fig = px.scatter(df, x="Accuracy", y="F1-Score", hover_name="Team", 
                         color="Accuracy", color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Le leaderboard est vide ou le fichier 'leaderboard.csv' est mal formaté.")
    st.info("Lancez d'abord une évaluation pour générer les premiers résultats.")

# --- SIDEBAR INFO ---
st.sidebar.header("À propos")
st.sidebar.info("""
**Classes :**
- 0: Glioma
- 1: Meningioma
- 2: No Tumor
- 3: Pituitary
""")

if st.sidebar.button("Actualiser les données"):
    st.cache_data.clear()
    st.rerun()

