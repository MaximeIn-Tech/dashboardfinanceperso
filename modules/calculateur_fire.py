import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.helpers import format_nombre


def calculateur_fire_render():
    st.header("🔥 Calculateur FI/RE (Financial Independence, Retire Early)")

    col1, col2, col3 = st.columns(3)

    with col1:
        revenus_annuels = st.number_input(
            "Revenus annuels nets (€)",
            min_value=0.0,
            value=40000.0,
            step=1000.0,
            format="%.0f",
            key="fire_revenus",
        )

        depenses_annuelles = st.number_input(
            "Dépenses annuelles (€)",
            min_value=0.0,
            value=25000.0,
            step=1000.0,
            format="%.0f",
            key="fire_depenses",
        )

    with col2:
        patrimoine_actuel = st.number_input(
            "Patrimoine actuel (€)",
            min_value=0.0,
            value=10000.0,
            step=1000.0,
            format="%.0f",
            key="fire_patrimoine",
        )

        taux_retour = st.number_input(
            "Taux de retour attendu (%)",
            min_value=0.0,
            max_value=20.0,
            value=7.0,
            step=0.5,
            key="fire_taux",
        )

    with col3:
        taux_retrait = st.number_input(
            "Règle de retrait (%)",
            min_value=1.0,
            max_value=10.0,
            value=4.0,
            step=0.5,
            key="fire_retrait",
            help="Pourcentage du patrimoine que vous pourrez retirer chaque année en retraite (règle des 4%)",
        )

        age_actuel = st.number_input(
            "Âge actuel", min_value=18, max_value=65, value=30, key="fire_age"
        )

    # Calculs FIRE
    epargne_annuelle = revenus_annuels - depenses_annuelles
    taux_epargne = (
        (epargne_annuelle / revenus_annuels) * 100 if revenus_annuels > 0 else 0
    )

    # Calcul du nombre FIRE (25x les dépenses annuelles pour la règle des 4%)
    nombre_fire = depenses_annuelles * (100 / taux_retrait)

    # Calcul du temps pour atteindre FIRE
    if epargne_annuelle > 0 and taux_retour > 0:
        r_annual = taux_retour / 100
        if patrimoine_actuel >= nombre_fire:
            annees_fire = 0
        else:
            # Formule pour calculer le temps nécessaire avec versements périodiques
            if patrimoine_actuel > 0:
                annees_fire = np.log(
                    (nombre_fire * r_annual / epargne_annuelle + 1)
                    / (patrimoine_actuel * r_annual / epargne_annuelle + 1)
                ) / np.log(1 + r_annual)
            else:
                annees_fire = np.log(
                    nombre_fire * r_annual / epargne_annuelle + 1
                ) / np.log(1 + r_annual)
    else:
        annees_fire = float("inf")

    age_fire = age_actuel + annees_fire

    st.markdown("---")

    # Métriques FIRE
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "💰 Nombre FIRE",
            f"{format_nombre(nombre_fire)} €",
            help="Votre capital investi pour pouvoir être FI/RE.",
        )
    with col2:
        st.metric(
            "📊 Taux d'épargne",
            f"{taux_epargne:.1f}%",
            help="Votre capacité/taux d'épargne accessible.",
        )
    with col3:
        if annees_fire < 100:
            st.metric(
                "⏰ Années jusqu'à FIRE",
                f"{annees_fire:.1f} ans",
                help="Le nombre d'années qu'il vous reste pour être FI/RE.",
            )
        else:
            st.metric("⏰ Années jusqu'à FIRE", "Impossible")
    with col4:
        if annees_fire < 100:
            st.metric(
                "🎂 Âge FIRE",
                f"{age_fire:.0f} ans",
                help="Votre âge quand vous pourrez être FI/RE.",
            )
        else:
            st.metric("🎂 Âge FIRE", "N/A")

    # Conseils FIRE
    col1, col2 = st.columns(2)

    with col1:
        if taux_epargne >= 50:
            st.success(
                "🚀 Excellent taux d'épargne ! Vous êtes sur la voie rapide vers FIRE."
            )
        elif taux_epargne >= 25:
            st.info("👍 Bon taux d'épargne. Continuez comme ça !")
        elif taux_epargne >= 10:
            st.warning(
                "⚠️ Taux d'épargne modéré. Essayez d'augmenter vos revenus ou réduire vos dépenses."
            )
        else:
            st.error(
                "📉 Taux d'épargne faible. FIRE sera difficile à atteindre sans changements majeurs."
            )

    with col2:
        st.info(
            f"""
        **Votre situation FIRE :**
        - Épargne mensuelle : {format_nombre(epargne_annuelle/12)} €
        - Revenus passifs nécessaires : {format_nombre(depenses_annuelles)} €/an
        - Patrimoine manquant : {format_nombre(max(0, nombre_fire - patrimoine_actuel))} €
        """
        )

    # Simulation évolution patrimoine
    if annees_fire < 50:
        annees_sim = list(range(0, int(annees_fire) + 5))
        patrimoine_evolution = []

        for annee in annees_sim:
            if annee == 0:
                patrimoine_evolution.append(patrimoine_actuel)
            else:
                # Croissance du patrimoine avec intérêts composés et épargne annuelle
                patrimoine = patrimoine_actuel * (1 + taux_retour / 100) ** annee
                if epargne_annuelle > 0:
                    patrimoine += epargne_annuelle * (
                        ((1 + taux_retour / 100) ** annee - 1) / (taux_retour / 100)
                    )
                patrimoine_evolution.append(patrimoine)

        fig_fire = go.Figure()
        fig_fire.add_trace(
            go.Scatter(
                x=annees_sim,
                y=patrimoine_evolution,
                name="Patrimoine projeté",
                line=dict(color="#ff7f0e"),
            )
        )
        fig_fire.add_hline(
            y=nombre_fire,
            line_dash="dash",
            line_color="red",
            annotation_text="Nombre FIRE",
        )
        fig_fire.update_layout(
            title="Projection vers l'indépendance financière",
            xaxis_title="Années",
            yaxis_title="Patrimoine (€)",
        )
        st.plotly_chart(fig_fire, use_container_width=True)
