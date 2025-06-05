import streamlit as st

from modules.interets_composes import interets_composes_render
from modules.calculateur_fire import calculateur_fire_render
from modules.calculateur_impots import calculateur_impots_render
from modules.calculateur_pret import calculateur_pret_render
from modules.calculateur_achat_vs_location import achat_vs_location_render

from components.footer import render_footer

from utils.helpers import format_nombre, load_css

# Configuration générale
st.set_page_config(page_title="Calculateurs Financiers", page_icon="💰", layout="wide")

css = load_css()

st.title("💰 Calculateurs Financiers")
st.markdown("Une suite d'outils pour planifier vos finances personnelles")
st.markdown(
    """<meta name="description" content="Une application Streamlit pour suivre facilement ses finances personnelles">""",
    unsafe_allow_html=True,
)

# Création des onglets
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🏦 Intérêts Composés",
        "🔥 Calculateur FI/RE",
        "🧮 Calculateur d'Impôts",
        "🏠 Acheter VS Louer",
        "🏦 Simulateur de prêt immobilier",
    ]
)

# ============= ONGLET 1: INTÉRÊTS COMPOSÉS =============
with tab1:
    interets_composes_render()


# ============= ONGLET 2: CALCULATEUR FIRE =============
with tab2:
    calculateur_fire_render()

# ============= ONGLET 3: CALCULATEUR TMI =============
with tab3:
    calculateur_impots_render()
# ============= ONGLET 4: ACHETER VS LOUER =============
with tab4:
    achat_vs_location_render()
# ============= ONGLET 5: PRÊT IMMO =============
with tab5:
    calculateur_pret_render()


render_footer()
