import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="PRDI - Simulateur Vin",
    page_icon="🍷",
    layout="wide"
)

# =========================================================
# STYLE CSS
# =========================================================

st.markdown("""
<style>

/* ===== GLOBAL ===== */

html, body, [class*="css"] {
    color: #f4efe9 !important;
    font-family: 'Segoe UI', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #140f1d, #2a1025);
}

/* ===== TITRES ===== */

h1 {
    color: #ffffff !important;
    font-size: 3rem !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #f4efe9 !important;
}

/* ===== SIDEBAR ===== */

section[data-testid="stSidebar"] {
    background: #1c1528;
    border-right: 2px solid #591d2e;
}

/* ===== SELECTBOX FIX ===== */

div[data-baseweb="select"] > div {
    background-color: #2b2036 !important;
    color: white !important;
}

div[data-baseweb="select"] * {
    color: white !important;
}

/* ===== INPUTS ===== */

.stSlider > div > div {
    color: white !important;
}

.stRadio label {
    color: white !important;
}

/* ===== METRICS ===== */

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 18px;
    backdrop-filter: blur(6px);
}

/* ===== TABLE ===== */

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03);
    border-radius: 15px;
    padding: 10px;
}

/* ===== EXPANDER ===== */

.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
}

/* ===== MOBILE FIX ===== */

@media (max-width: 768px) {

    html, body, [class*="css"] {
        color: white !important;
        background-color: #140f1d !important;
    }

    .stApp {
        background: #140f1d !important;
    }

    h1 {
        font-size: 2.3rem !important;
    }

}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.title("🍷 Simulateur technico-économique viticole")
st.markdown("## Projet PRDI — coût de production et prix consommateur estimé")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Paramètres généraux")

surface = st.sidebar.slider(
    "Surface du domaine (ha)",
    0.5,
    20.0,
    2.0
)

coef_consommateur = st.sidebar.slider(
    "Coefficient prix consommateur",
    1.0,
    5.0,
    3.0
)

st.sidebar.caption(
    "Le coefficient permet d’estimer un prix consommateur "
    "à partir du coût de production."
)

st.sidebar.markdown("---")

st.sidebar.header("🌱 Choix techniques indépendants")

# =========================================================
# PARAMÈTRES
# =========================================================

param_options = ["Conventionnel", "Éco-responsable"]

rendement_mode = st.sidebar.selectbox(
    "Rendement",
    param_options
)

main_oeuvre_mode = st.sidebar.selectbox(
    "Main-d'œuvre",
    param_options
)

vendange_mode = st.sidebar.selectbox(
    "Vendange : énergie, eau, matériel",
    param_options
)

intrants_mode = st.sidebar.selectbox(
    "Intrants phytosanitaires",
    param_options
)

emballage_mode = st.sidebar.selectbox(
    "Emballages",
    param_options
)

fermentation_mode = st.sidebar.selectbox(
    "Fermentation",
    param_options
)

stabilisation_mode = st.sidebar.selectbox(
    "Stabilisation",
    param_options
)

elevage_mode = st.sidebar.selectbox(
    "Élevage",
    param_options
)

dechets_mode = st.sidebar.selectbox(
    "Gestion des déchets",
    ["Élimination", "Compost", "Valorisation"]
)

# =========================================================
# BASE DE DONNÉES
# =========================================================

params = {
    "Conventionnel": {
        "rendement": 60,
        "cout_horaire": 18,
        "temps_ha": 120,
        "energie_vendange": 250,
        "eau": 50,
        "cout_eau": 2,
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
        "elimination": 43,
        "compost": -40,
        "valorisation": -72,
    },

    "Éco-responsable": {
        "rendement": 45,
        "cout_horaire": 18,
        "temps_ha": 160,
        "energie_vendange": 200,
        "eau": 40,
        "cout_eau": 2,
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
        "elimination": 31,
        "compost": -40,
        "valorisation": -52,
    }
}

prix_energie = 0.252

# =========================================================
# RÉCUP PARAMÈTRES
# =========================================================

rendement_p = params[rendement_mode]
main_p = params[main_oeuvre_mode]
vendange_p = params[vendange_mode]
intrants_p = params[intrants_mode]
emballage_p = params[emballage_mode]
fermentation_p = params[fermentation_mode]
stabilisation_p = params[stabilisation_mode]
elevage_p = params[elevage_mode]

# =========================================================
# CALCULS
# =========================================================

rendement_reel = (
    rendement_p["rendement"]
    * (1 - elevage_p["pertes"])
)

volume_hl = rendement_reel * surface

nb_bouteilles = volume_hl * 100 / 0.75

couts = {

    "Main-d'œuvre":
        main_p["cout_horaire"]
        * main_p["temps_ha"]
        * surface,

    "Énergie vendange":
        vendange_p["energie_vendange"]
        * prix_energie
        * surface,

    "Eau":
        vendange_p["eau"]
        * vendange_p["cout_eau"]
        * surface,

    "Matériel":
        vendange_p["materiel"]
        * surface,

    "Intrants phytosanitaires":
        (
            intrants_p["fongicides"]
            + intrants_p["insecticides"]
            + intrants_p["herbicides"]
            + intrants_p["desherbage"]
        ) * surface,

    "Bouteilles":
        emballage_p["bouteille"]
        * nb_bouteilles,

    "Fermentation":
        (
            fermentation_p["energie_fermentation"]
            * prix_energie
            + fermentation_p["levures"]
        ) * volume_hl,

    "Stabilisation":
        (
            stabilisation_p["sulfites"]
            + stabilisation_p["filtration"]
        ) * volume_hl,

    "Élevage":
        elevage_p["elevage"]
        * volume_hl,

}

# Déchets

if dechets_mode == "Élimination":
    couts["Gestion déchets"] = elevage_p["elimination"] * surface

elif dechets_mode == "Compost":
    couts["Gestion déchets"] = elevage_p["compost"] * surface

else:
    couts["Gestion déchets"] = elevage_p["valorisation"] * surface

# =========================================================
# TOTALS
# =========================================================

cout_total = sum(couts.values())

cout_bouteille = cout_total / nb_bouteilles

prix_conso = cout_bouteille * coef_consommateur

# =========================================================
# SCORE ENVIRONNEMENTAL
# =========================================================

score = 100

if rendement_mode == "Conventionnel":
    score -= 15

if intrants_mode == "Conventionnel":
    score -= 25

if fermentation_mode == "Conventionnel":
    score -= 10

if emballage_mode == "Conventionnel":
    score -= 10

if elevage_mode == "Conventionnel":
    score -= 10

if dechets_mode == "Élimination":
    score -= 10

score = max(score, 0)

# =========================================================
# DATAFRAME
# =========================================================

df = pd.DataFrame({
    "Poste": list(couts.keys()),
    "Coût (€)": list(couts.values())
})

# =========================================================
# KPI
# =========================================================

st.header("📊 Résultats principaux")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Rendement réel",
    f"{rendement_reel:.1f} hL/ha"
)

c2.metric(
    "Volume produit",
    f"{volume_hl:.1f} hL"
)

c3.metric(
    "Nombre de bouteilles",
    f"{nb_bouteilles:,.0f}".replace(",", " ")
)

c4.metric(
    "Coût de production",
    f"{cout_bouteille:.2f} €/bouteille"
)

c5.metric(
    "Prix consommateur estimé",
    f"{prix_conso:.2f} €"
)

st.caption(
    "Le prix consommateur estimé est obtenu en appliquant "
    "un coefficient commercial au coût de production."
)

# =========================================================
# SCORE
# =========================================================

st.header("🌍 Score environnemental simplifié")

st.metric("Score", f"{score}/100")

st.progress(score / 100)

st.caption(
    "Ce score est un indicateur pédagogique simplifié."
)

# =========================================================
# EXPLICATIONS
# =========================================================

with st.expander("ℹ️ Comprendre les paramètres indépendants"):

    st.write("""
    Chaque étape du procédé peut être choisie indépendamment.

    Exemple :
    - utiliser une fermentation éco-responsable,
    - mais conserver un élevage conventionnel.

    Cela permet de simuler des stratégies hybrides réalistes.
    """)

with st.expander("ℹ️ Comprendre le score environnemental"):

    st.write("""
    Le score environnemental prend en compte :
    - l’utilisation d’intrants,
    - l’énergie,
    - le packaging,
    - la gestion des déchets,
    - les pertes liées à l’élevage.

    Plus le score est élevé,
    plus le procédé est considéré comme responsable.
    """)

# =========================================================
# GRAPHIQUES
# =========================================================

st.header("📈 Répartition des coûts")

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        df,
        x="Poste",
        y="Coût (€)",
        text_auto=".0f",
        color="Coût (€)"
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    fig2 = px.pie(
        df,
        values="Coût (€)",
        names="Poste"
    )

    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )

    st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# TABLEAU
# =========================================================

st.header("📋 Détail des coûts")

st.dataframe(
    df.sort_values("Coût (€)", ascending=False),
    use_container_width=True
)

# =========================================================
# ANALYSE AUTO
# =========================================================

poste_max = df.sort_values(
    "Coût (€)",
    ascending=False
).iloc[0]

st.header("🧠 Analyse automatique")

st.success(
    f"Le poste dominant est "
    f"**{poste_max['Poste']}**."
)

st.markdown(f"""
### Interprétation

- Le coût actuel de production est de **{cout_bouteille:.2f} €/bouteille**
- Le prix consommateur simulé est de **{prix_conso:.2f} €**
- Le score environnemental atteint **{score}/100**
- Le principal poste de coût est :
**{poste_max['Poste']}**

Cette simulation illustre les compromis
entre performance économique
et réduction des impacts environnementaux.
""")
