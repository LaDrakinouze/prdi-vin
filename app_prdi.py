import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="PRDI - Simulateur Vin", layout="wide")
st.sidebar.markdown("---")
mode_story = st.sidebar.checkbox("🎬 Mode storytelling")
st.title("🍷 Simulateur du coût de revient d’une bouteille")
st.markdown("### Analyse technico-économique — Projet PRDI")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("⚙️ Paramètres")

surface = st.sidebar.slider("Surface (ha)", 0.5, 20.0, 2.0)

mode = st.sidebar.radio(
    "Mode de production",
    ["Conventionnel", "Éco-responsable"]
)

gestion_dechets = st.sidebar.selectbox(
    "Gestion des déchets",
    ["Élimination", "Compost", "Valorisation"]
)

# -----------------------------
# BASE DE DONNÉES
# -----------------------------
params = {
    "Conventionnel": {
        "rendement": 60,
        "cout_horaire": 18,
        "temps_ha": 120,
        "energie_vendange": 250,
        "eau": 50,
        "cout_eau": 2,
        "materiel": 300,
        "fongicide_cout": 25,
        "fongicide_nb": 10,
        "insecticide": 30,
        "herbicide": 80,
        "desherbage": 30,
        "bouteille": 0.8,
        "energie_fermentation": 8,
        "levures": 2.5,
        "sulfites": 0.8,
        "filtration": 4,
        "elevage": 4.5,
        "pertes": 0.05,
        "marc": 1430,
        "dechets": {
            "Élimination": 0.03,
            "Compost": -40,
            "Valorisation": -72
        }
    },
    "Éco-responsable": {
        "rendement": 45,
        "cout_horaire": 18,
        "temps_ha": 160,
        "energie_vendange": 200,
        "eau": 40,
        "cout_eau": 2,
        "materiel": 450,
        "fongicide_cout": 20,
        "fongicide_nb": 14,
        "insecticide": 200,
        "herbicide": 0,
        "desherbage": 200,
        "bouteille": 1.5,
        "energie_fermentation": 1,
        "levures": 0.2,
        "sulfites": 0.4,
        "filtration": 1,
        "elevage": 85,
        "pertes": 0.10,
        "marc": 1040,
        "dechets": {
            "Élimination": 0.03,
            "Compost": -40,
            "Valorisation": -52
        }
    }
}

prix_energie = 0.252

# -----------------------------
# FONCTION CALCUL
# -----------------------------
def calcul(mode):
    p = params[mode]

    rendement_reel = p["rendement"] * (1 - p["pertes"])
    volume_hl = rendement_reel * surface
    nb_bouteilles = volume_hl * 100 / 0.75

    couts = {
        "Main-d'œuvre": p["cout_horaire"] * p["temps_ha"] * surface,
        "Énergie vendange": p["energie_vendange"] * prix_energie * surface,
        "Eau": p["eau"] * p["cout_eau"] * surface,
        "Matériel": p["materiel"] * surface,
        "Fongicides": p["fongicide_cout"] * p["fongicide_nb"] * surface,
        "Insecticides": p["insecticide"] * surface,
        "Herbicides / désherbage": (p["herbicide"] + p["desherbage"]) * surface,
        "Bouteilles": p["bouteille"] * nb_bouteilles,
        "Énergie fermentation": p["energie_fermentation"] * prix_energie * volume_hl,
        "Levures": p["levures"] * volume_hl,
        "Sulfites": p["sulfites"] * volume_hl,
        "Filtration": p["filtration"] * volume_hl,
        "Élevage": p["elevage"] * volume_hl,
    }

    if gestion_dechets == "Élimination":
        couts["Déchets"] = p["marc"] * p["dechets"]["Élimination"] * surface
    elif gestion_dechets == "Compost":
        couts["Déchets"] = p["dechets"]["Compost"] * surface
    else:
        couts["Déchets"] = p["dechets"]["Valorisation"] * surface

    total = sum(couts.values())
    cout_bouteille = total / nb_bouteilles

    df = pd.DataFrame({
        "Poste": list(couts.keys()),
        "Coût (€)": list(couts.values())
    })

    df["%"] = df["Coût (€)"] / total * 100

    return total, cout_bouteille, volume_hl, nb_bouteilles, df


# -----------------------------
# CALCULS
# -----------------------------
total, cb, vol, nb, df = calcul(mode)
total_c, cb_c, _, _, df_c = calcul("Conventionnel")
total_e, cb_e, _, _, df_e = calcul("Éco-responsable")

# -----------------------------
# KPI
# -----------------------------
st.subheader("📊 Résultats")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Volume", f"{vol:.1f} hL")
c2.metric("Bouteilles", f"{nb:,.0f}".replace(",", " "))
c3.metric("Coût total", f"{total:,.0f} €")
c4.metric("€/bouteille", f"{cb:.2f} €")

# -----------------------------
# COMPARAISON
# -----------------------------
st.subheader("⚖️ Comparaison des scénarios")

col1, col2 = st.columns(2)

col1.metric("Conventionnel €/bouteille", f"{cb_c:.2f} €")
col2.metric("Éco-responsable €/bouteille", f"{cb_e:.2f} €")

st.info(f"Écart : +{cb_e - cb_c:.2f} €/bouteille")

# -----------------------------
# GRAPHIQUES
# -----------------------------
st.subheader("📈 Analyse des coûts")

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(df, x="Poste", y="Coût (€)", text_auto=".0f")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.pie(df, values="Coût (€)", names="Poste")
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TABLEAU
# -----------------------------
st.subheader("📋 Détail des coûts")

st.dataframe(df.sort_values("Coût (€)", ascending=False), use_container_width=True)

# -----------------------------
# ANALYSE AUTO
# -----------------------------
st.subheader("🧠 Analyse automatique")

poste_max = df.sort_values("Coût (€)", ascending=False).iloc[0]
if mode_story:
    st.header("🎬 Scénario guidé")

    st.markdown("### Étape 1 : Domaine de base")
    st.write("Nous considérons un domaine de 2 hectares.")

    st.markdown("### Étape 2 : Production conventionnelle")
    total_c, cb_c, _, _, _ = calcul("Conventionnel")
    st.metric("Coût conventionnel", f"{cb_c:.2f} €/bouteille")

    st.markdown("### Étape 3 : Passage à l’éco-responsable")
    total_e, cb_e, _, _, _ = calcul("Éco-responsable")
    st.metric("Coût éco-responsable", f"{cb_e:.2f} €/bouteille")

    st.markdown("### Étape 4 : Analyse")
    diff = cb_e - cb_c
    st.warning(f"Le passage à l’éco augmente le coût de +{diff:.2f} €/bouteille")

    st.markdown("### Étape 5 : Interprétation")
    st.success("""
    Les principaux facteurs sont :
    - L’élevage en barrique
    - Le coût des bouteilles
    - L’augmentation de la main d’œuvre
    """)
st.success(
    f"Le poste dominant est **{poste_max['Poste']}** "
    f"({poste_max['%']:.1f}% du coût total)."
)

st.markdown("""
### 🔍 Lecture
- Le coût de la bouteille est souvent dominant  
- L’élevage (barrique) augmente fortement le coût  
- Les pratiques écologiques augmentent le coût mais améliorent l’impact environnemental  
""")            