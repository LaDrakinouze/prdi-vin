import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="PRDI - Simulateur Viticole",
    page_icon="🍷",
    layout="wide"
)

# =========================================================
# STYLE CSS PREMIUM
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
}

.stApp {
    background-color: #f4efe9;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background-color: #591d2e;
    padding-top: 1rem;
}

section[data-testid="stSidebar"] {
    background-color: #591d2e;
    padding-top: 1rem;
}

/* Texte sidebar */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}

/* Selectbox */
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background-color: white !important;
    color: #591d2e !important;
    border-radius: 10px;
}

/* Texte interne selectbox */
section[data-testid="stSidebar"] .stSelectbox span {
    color: #591d2e !important;
}

/* Slider */
section[data-testid="stSidebar"] .stSlider label {
    color: white !important;
}

/* Titres */

h1 {
    color: #591d2e;
    font-size: 3rem !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #591d2e;
    font-weight: 700 !important;
}

/* KPI cards */

div[data-testid="metric-container"] {
    background-color: white;
    border: 2px solid #591d2e;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

/* Progress bar */

.stProgress > div > div > div > div {
    background-color: #591d2e;
}

/* Expander */

.streamlit-expanderHeader {
    font-size: 18px;
    font-weight: 600;
    color: #591d2e;
}

/* Dataframe */

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Bloc texte */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Cards custom */

.custom-card {
    background-color: white;
    padding: 25px;
    border-radius: 18px;
    border-left: 8px solid #591d2e;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITRE
# =========================================================

st.markdown("""
# 🍷 Simulateur technico-économique viticole

### Projet PRDI — coût de production et prix consommateur estimé
""")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## ⚙️ Paramètres généraux")

surface = st.sidebar.slider(
    "Surface du domaine (ha)",
    0.5,
    20.0,
    2.0
)

coef_consommateur = st.sidebar.slider(
    "Coefficient prix consommateur",
    1.5,
    5.0,
    3.0,
    0.1
)

st.sidebar.markdown("""
Le coefficient permet d’estimer un prix consommateur
à partir du coût de production.
""")

st.sidebar.markdown("---")

st.sidebar.markdown("## 🌱 Choix techniques indépendants")

# =========================================================
# PARAMÈTRES
# =========================================================

params = {

    "Conventionnel": {

        "rendement": 60,
        "main_oeuvre": 120,
        "energie_vendange": 250,
        "eau": 50,
        "materiel": 300,

        "fongicides": 25 * 10,
        "insecticides": 30,
        "herbicides": 80,
        "desherbage": 30,

        "bouteille": 0.8,

        "energie_fermentation": 8,
        "levures": 2.5,

        "sulfites": 0.8,
        "filtration": 4,

        "elevage": 15,
        "pertes": 0.05,

        "marc": 1430,
        "dechets": 43,
        "valorisation": -72,

        "score": 45
    },

    "Éco-responsable": {

        "rendement": 45,
        "main_oeuvre": 160,
        "energie_vendange": 200,
        "eau": 40,
        "materiel": 450,

        "fongicides": 20 * 14,
        "insecticides": 200,
        "herbicides": 0,
        "desherbage": 200,

        "bouteille": 1.5,

        "energie_fermentation": 1,
        "levures": 0.2,

        "sulfites": 0.4,
        "filtration": 1,

        "elevage": 250,
        "pertes": 0.10,

        "marc": 1040,
        "dechets": 31,
        "valorisation": -52,

        "score": 90
    }
}

# =========================================================
# CHOIX INDÉPENDANTS
# =========================================================

choix = {}

parametres = [
    ("rendement", "Rendement"),
    ("main_oeuvre", "Main-d'œuvre"),
    ("energie_vendange", "Vendange : énergie, eau, matériel"),
    ("fongicides", "Intrants phytosanitaires"),
    ("bouteille", "Conditionnement"),
    ("energie_fermentation", "Fermentation"),
    ("sulfites", "Stabilisation"),
    ("elevage", "Élevage"),
    ("dechets", "Gestion des déchets")
]

for cle, nom in parametres:

    choix[cle] = st.sidebar.selectbox(
        nom,
        ["Conventionnel", "Éco-responsable"],
        key=cle
    )

# =========================================================
# CALCULS
# =========================================================

prix_energie = 0.252

def valeur(param):

    return params[choix[param]][param]

rendement = valeur("rendement")
main_oeuvre = valeur("main_oeuvre")
energie_vendange = valeur("energie_vendange")
fongicides = valeur("fongicides")
bouteille = valeur("bouteille")
energie_fermentation = valeur("energie_fermentation")
sulfites = valeur("sulfites")
elevage = valeur("elevage")
dechets = valeur("dechets")

eau = params[choix["energie_vendange"]]["eau"]
materiel = params[choix["energie_vendange"]]["materiel"]

insecticides = params[choix["fongicides"]]["insecticides"]
herbicides = params[choix["fongicides"]]["herbicides"]
desherbage = params[choix["fongicides"]]["desherbage"]

levures = params[choix["energie_fermentation"]]["levures"]
filtration = params[choix["sulfites"]]["filtration"]

pertes = params[choix["elevage"]]["pertes"]
marc = params[choix["dechets"]]["marc"]

# =========================================================
# RÉSULTATS
# =========================================================

rendement_reel = rendement * (1 - pertes)

volume_hl = rendement_reel * surface

nb_bouteilles = volume_hl * 100 / 0.75

couts = {

    "Main-d'œuvre":
        main_oeuvre * 18 * surface,

    "Énergie vendange":
        energie_vendange * prix_energie * surface,

    "Eau":
        eau * 2 * surface,

    "Matériel":
        materiel * surface,

    "Intrants":
        (fongicides + insecticides +
         herbicides + desherbage) * surface,

    "Fermentation":
        (energie_fermentation * prix_energie +
         levures) * volume_hl,

    "Stabilisation":
        (sulfites + filtration) * volume_hl,

    "Élevage":
        elevage * volume_hl,

    "Conditionnement":
        bouteille * nb_bouteilles,

    "Déchets":
        dechets * surface
}

total = sum(couts.values())

cout_bouteille = total / nb_bouteilles

prix_consommateur = cout_bouteille * coef_consommateur

# =========================================================
# SCORE ENVIRONNEMENTAL
# =========================================================

score = (
    params[choix["rendement"]]["score"] +
    params[choix["main_oeuvre"]]["score"] +
    params[choix["energie_vendange"]]["score"] +
    params[choix["fongicides"]]["score"] +
    params[choix["bouteille"]]["score"] +
    params[choix["energie_fermentation"]]["score"] +
    params[choix["sulfites"]]["score"] +
    params[choix["elevage"]]["score"] +
    params[choix["dechets"]]["score"]
) / 9

# =========================================================
# KPI
# =========================================================

st.markdown("## 📊 Résultats principaux")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Rendement réel", f"{rendement_reel:.1f} hL/ha")
c2.metric("Volume produit", f"{volume_hl:.1f} hL")
c3.metric("Nombre de bouteilles", f"{nb_bouteilles:,.0f}".replace(",", " "))
c4.metric("Coût de production", f"{cout_bouteille:.2f} €/bouteille")
c5.metric("Prix consommateur estimé", f"{prix_consommateur:.2f} €")

st.markdown("""
Le prix consommateur estimé est obtenu en appliquant
un coefficient commercial au coût de production.
Il inclut implicitement marge, distribution,
transport et fiscalité.
""")

# =========================================================
# SCORE ENVIRONNEMENTAL
# =========================================================

st.markdown("## 🌍 Score environnemental simplifié")

col1, col2 = st.columns([1,3])

with col1:

    st.metric("Score", f"{score:.0f}/100")

with col2:

    st.progress(score / 100)

    st.caption("""
Ce score est un indicateur pédagogique simplifié.
Il ne remplace pas une Analyse du Cycle de Vie complète.
""")

# =========================================================
# EXPLICATIONS
# =========================================================

with st.expander("ℹ️ Comprendre les paramètres indépendants"):

    st.markdown("""
Chaque poste technique peut être sélectionné
indépendamment :

- Rendement
- Main-d'œuvre
- Intrants
- Fermentation
- Élevage
- Gestion des déchets

Cela permet de simuler des systèmes hybrides
et d’identifier les postes ayant le plus d’impact
sur le coût final et sur l’environnement.
""")

with st.expander("ℹ️ Comprendre le score environnemental"):

    st.markdown("""
Le score environnemental repose sur une logique simplifiée :

- réduction des intrants chimiques,
- baisse des consommations énergétiques,
- réduction des herbicides,
- valorisation des déchets,
- diminution des pertes.

Un système plus éco-responsable obtient donc
un score plus élevé.
""")

# =========================================================
# DATAFRAME
# =========================================================

df = pd.DataFrame({
    "Poste": list(couts.keys()),
    "Coût (€)": list(couts.values())
})

# =========================================================
# GRAPHIQUES
# =========================================================

st.markdown("## 📈 Répartition des coûts")

palette = [
    "#591d2e",
    "#7a3147",
    "#9c5a6c",
    "#b57f8f",
    "#d8b5be",
    "#c49a6c",
    "#8c6a43",
    "#5c8a5c"
]

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        df,
        x="Poste",
        y="Coût (€)",
        color="Poste",
        color_discrete_sequence=palette
    )

    fig.update_layout(
        plot_bgcolor="#f4efe9",
        paper_bgcolor="#f4efe9",
        font_color="#591d2e",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    fig2 = px.pie(
        df,
        names="Poste",
        values="Coût (€)",
        color_discrete_sequence=palette
    )

    fig2.update_layout(
        paper_bgcolor="#f4efe9",
        font_color="#591d2e"
    )

    st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# TABLEAU
# =========================================================

st.markdown("## 📋 Détail des coûts")

st.dataframe(
    df.sort_values("Coût (€)", ascending=False),
    use_container_width=True
)

# =========================================================
# ANALYSE AUTO
# =========================================================

st.markdown("## 🧠 Analyse automatique")

poste_max = df.sort_values(
    "Coût (€)",
    ascending=False
).iloc[0]

st.markdown(f"""
<div class="custom-card">

<h3>Poste dominant</h3>

Le poste ayant le plus d’impact économique est :

<h2>{poste_max['Poste']}</h2>

avec un coût total de
<b>{poste_max['Coût (€)']:.0f} €</b>

</div>
""", unsafe_allow_html=True)

st.markdown("""
### 🔍 Lecture des résultats

- Le conditionnement représente souvent le poste dominant
- L’élevage en barrique augmente fortement les coûts
- Les systèmes éco-responsables réduisent certains impacts environnementaux
- Une baisse du rendement augmente mécaniquement le coût par bouteille
- La valorisation des déchets peut compenser une partie des surcoûts
""")
