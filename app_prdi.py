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
# CSS PREMIUM
# =========================================================

st.markdown("""
<style>

/* =====================================================
GLOBAL
===================================================== */

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    color: #f4efe9 ;
}

/* =====================================================
BACKGROUND
===================================================== */

.stApp {
    background:
        linear-gradient(
            135deg,
            rgba(20,15,29,0.97),
            rgba(89,29,46,0.94)
        );
}

/* =====================================================
TEXT
===================================================== */

p, label {
    color: #f4efe9 !important;
}

/* =====================================================
TITLES
===================================================== */

h1 {
    color: white !important;
    font-size: 3.3rem !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: white !important;
    font-weight: 700 !important;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #1c1528,
            #241328
        );

    border-right: 2px solid rgba(255,255,255,0.05);
}

/* =====================================================
SELECTBOX
===================================================== */

div[data-baseweb="select"] > div {
    background-color: #2b2036 !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

/* texte affiché dans la case */
div[data-baseweb="select"] span {
    color: black !important;
}

/* menu déroulant */
ul[role="listbox"] {
    background: black !important;
}

/* options */
ul[role="listbox"] li {
    color: black !important;
    background: black !important;
}

/* hover */
ul[role="listbox"] li:hover {
    background: #f1f1f1 !important;
    color: black !important;
}

/* =====================================================
SLIDER
===================================================== */

.stSlider * {
    color: white !important;
}

/* =====================================================
RADIO
===================================================== */

.stRadio label {
    color: white !important;
}

/* =====================================================
METRICS
===================================================== */

[data-testid="metric-container"] {

    background: rgba(255,255,255,0.06);

    border: 1px solid rgba(255,255,255,0.08);

    padding: 25px;

    border-radius: 22px;

    backdrop-filter: blur(8px);

    box-shadow:
        0 4px 30px rgba(0,0,0,0.2);
}

[data-testid="metric-container"] * {
    color: white !important;
}

/* =====================================================
DATAFRAME
===================================================== */

[data-testid="stDataFrame"] {

    background: rgba(255,255,255,0.04);

    border-radius: 18px;

    padding: 10px;
}

/* =====================================================
EXPANDER
===================================================== */

.streamlit-expanderHeader {

    background: rgba(255,255,255,0.04);

    border-radius: 12px;

    border: 1px solid rgba(255,255,255,0.05);
}

/* =====================================================
PROGRESS BAR
===================================================== */

.stProgress > div > div > div > div {
    background-color: #ff4b6e !important;
}

/* =====================================================
MOBILE
===================================================== */

@media (max-width: 768px) {

    h1 {
        font-size: 2.4rem !important;
    }

    .stApp {
        background:
            linear-gradient(
                180deg,
                #140f1d,
                #2a1025
            );
    }
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.title("🍷 Simulateur technico-économique viticole")

st.markdown("""
## Projet PRDI — coût de production et prix consommateur estimé
""")

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

st.sidebar.caption("""
Le coefficient permet d’estimer un prix consommateur
à partir du coût de production.
""")

st.sidebar.markdown("---")

st.sidebar.header("🌱 Choix techniques indépendants")

options = ["Conventionnel", "Éco-responsable"]

rendement_mode = st.sidebar.selectbox(
    "Rendement",
    options
)

main_oeuvre_mode = st.sidebar.selectbox(
    "Main-d'œuvre",
    options
)

vendange_mode = st.sidebar.selectbox(
    "Vendange : énergie, eau, matériel",
    options
)

intrants_mode = st.sidebar.selectbox(
    "Intrants phytosanitaires",
    options
)

emballage_mode = st.sidebar.selectbox(
    "Emballages",
    options
)

fermentation_mode = st.sidebar.selectbox(
    "Fermentation",
    options
)

stabilisation_mode = st.sidebar.selectbox(
    "Stabilisation",
    options
)

elevage_mode = st.sidebar.selectbox(
    "Élevage",
    options
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
# PARAMÈTRES SÉLECTIONNÉS
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

# =========================================================
# DÉCHETS
# =========================================================

if dechets_mode == "Élimination":

    couts["Gestion déchets"] = (
        elevage_p["elimination"] * surface
    )

elif dechets_mode == "Compost":

    couts["Gestion déchets"] = (
        elevage_p["compost"] * surface
    )

else:

    couts["Gestion déchets"] = (
        elevage_p["valorisation"] * surface
    )

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

df["% du coût total"] = (
    df["Coût (€)"] / df["Coût (€)"].sum() * 100
).round(1)

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

# =========================================================
# SCORE
# =========================================================

st.header("🌍 Score environnemental simplifié")

st.metric(
    "Score",
    f"{score}/100"
)

st.progress(score / 100)

# =========================================================
# EXPLICATIONS
# =========================================================

with st.expander("ℹ️ Comprendre les paramètres indépendants"):

    st.write("""
Chaque étape du procédé peut être choisie indépendamment.

Exemple :
- fermentation éco-responsable,
- mais élevage conventionnel.

Cela permet de simuler des scénarios hybrides réalistes.
""")

with st.expander("ℹ️ Comprendre le score environnemental"):

    st.write("""
Le score environnemental prend en compte :
- l’énergie,
- les intrants,
- l’élevage,
- les déchets,
- le packaging.

Plus le score est élevé,
plus le procédé est considéré comme responsable.
""")

# =========================================================
# GRAPHES
# =========================================================

# =========================================================
# GRAPHES
# =========================================================

st.header("📈 Répartition des coûts")

fig2 = px.pie(
df,
values="Coût (€)",
names="Poste",
hole=0.42,
color_discrete_sequence=px.colors.sequential.Blues_r
)

fig2.update_traces(
textinfo='percent+label',
textfont_size=16
)

fig2.update_layout(

paper_bgcolor='white',
plot_bgcolor='white',

font=dict(
    color='black',
    size=16
),

legend=dict(
    font=dict(
        color='black',
        size=15
    ),
    orientation="v",
    x=0,
    y=0.5,
    xanchor="left",
    yanchor="middle"
),

margin=dict(
    t=40,
    l=20,
    r=20,
    b=20
),

height=750
)

st.plotly_chart(
fig2,
use_container_width=True
)

# =========================================================
# TABLEAU
# =========================================================

st.header("📋 Détail des coûts")

df_affichage = df.sort_values(
    "Coût (€)",
    ascending=False
)

df_affichage["Coût (€)"] = (
    df_affichage["Coût (€)"]
    .round(0)
)

df_affichage["% du coût total"] = (
    df_affichage["% du coût total"]
    .astype(str) + " %"
)

st.dataframe(
    df_affichage,
    use_container_width=True
)

# =========================================================
# ANALYSE
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

- Coût de production :
**{cout_bouteille:.2f} €/bouteille**

- Prix consommateur estimé :
**{prix_conso:.2f} €**

- Score environnemental :
**{score}/100**

- Poste dominant :
**{poste_max['Poste']}**

Cette simulation met en évidence
les compromis entre performance économique
et impact environnemental.
""")
