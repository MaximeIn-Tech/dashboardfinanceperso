import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.helpers import format_nombre


def calculateur_fire_render():
    st.header("🔥 Calculateur FI/RE (Financial Independence, Retire Early)")

    st.caption(
        "Remplissez les champs ci-dessous pour simuler votre parcours vers l'indépendance financière."
    )

    # Layout 3 colonnes
    col1, col2, col3 = st.columns(3)

    # --- Colonne 1 : Revenus & Dépenses ---
    with col1:
        st.subheader("💼 Revenus & Dépenses")
        revenus_annuels = st.number_input(
            label="💼 Revenus nets annuels (€)",
            min_value=0.0,
            value=40000.0,
            step=1000.0,
            format="%.0f",
            key="fire_revenus",
            help="Vos revenus nets annuels, incluant salaire, primes, freelancing, etc.",
        )

        depenses_annuelles = st.number_input(
            label="💸 Dépenses annuelles (€)",
            min_value=0.0,
            value=25000.0,
            step=1000.0,
            format="%.0f",
            key="fire_depenses",
            help="Vos dépenses annuelles estimées : logement, alimentation, transport, loisirs, etc.",
        )

    # --- Colonne 2 : Patrimoine & Rendement ---
    with col2:
        st.subheader("📊 Situation financière actuelle")
        patrimoine_actuel = st.number_input(
            label="📊 Patrimoine total actuel (€)",
            min_value=0.0,
            value=10000.0,
            step=1000.0,
            format="%.0f",
            key="fire_patrimoine",
            help="Total de vos actifs disponibles (livrets, bourse, cryptos, etc.)",
        )

        taux_retour = st.number_input(
            label="📈 Rendement annuel attendu (%)",
            min_value=0.0,
            max_value=20.0,
            value=7.0,
            step=0.5,
            key="fire_taux",
            help="Taux de croissance annuel moyen espéré pour vos investissements.",
        )

    # --- Colonne 3 : Paramètres FIRE ---
    with col3:
        st.subheader("🔥 Hypothèses FIRE")
        taux_retrait = st.number_input(
            label="🔥 Taux de retrait (%)",
            min_value=1.0,
            max_value=10.0,
            value=4.0,
            step=0.5,
            key="fire_retrait",
            help="Pourcentage du patrimoine que vous pouvez retirer chaque année à la retraite (ex : règle des 4%).",
        )

        age_actuel = st.number_input(
            label="🎂 Âge actuel",
            min_value=18,
            max_value=70,
            value=30,
            step=1,
            key="fire_age",
            help="Votre âge aujourd'hui, utilisé pour estimer l'âge d'atteinte de l'indépendance.",
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

    # Dashboard FIRE moderne et visuel
    st.markdown("## 🔥 **Tableau de bord FIRE**")

    # Calculs préliminaires
    patrimoine_manquant = max(0, nombre_fire - patrimoine_actuel)
    progres_fire = (patrimoine_actuel / nombre_fire) * 100 if nombre_fire > 0 else 0

    # === SECTION 1 : Métriques principales avec couleurs conditionnelles ===
    col1, col2, col3, col4 = st.columns(4)

    # --- Capital FIRE ---
    with col1:
        st.metric(
            label="💰 Capital FIRE",
            value=f"{format_nombre(nombre_fire)} €",
            help="Capital nécessaire pour l'indépendance financière (25x vos dépenses annuelles)",
        )

    # --- Taux d'épargne ---
    with col2:
        if taux_epargne >= 50:
            delta_text = "🚀 Excellent !"
            delta_color = "normal"
        elif taux_epargne >= 25:
            delta_text = "👍 Très bien"
            delta_color = "normal"
        elif taux_epargne >= 10:
            delta_text = "⚠️ Modéré"
            delta_color = "off"
        else:
            delta_text = "📉 Faible"
            delta_color = "inverse"

        st.metric(
            label="📊 Taux d’épargne",
            value=f"{taux_epargne:.1f}%",
            delta=delta_text,
            delta_color=delta_color,
            help="Pourcentage de vos revenus que vous épargnez chaque année",
        )

    # --- Temps restant avant FIRE ---
    with col3:
        if annees_fire < 100:
            if annees_fire <= 10:
                delta_text = "🔥 Très proche !"
                delta_color = "normal"
            elif annees_fire <= 20:
                delta_text = "💪 Bon rythme"
                delta_color = "normal"
            else:
                delta_text = "⏳ Long terme"
                delta_color = "off"

            st.metric(
                label="⏰ Temps restant",
                value=f"{annees_fire:.1f} ans",
                delta=delta_text,
                delta_color=delta_color,
                help="Nombre d'années avant d’atteindre l’indépendance financière",
            )
        else:
            st.metric(
                label="⏰ Temps restant",
                value="∞",
                delta="Impossible en l'état",
                delta_color="inverse",
                help="Avec votre épargne actuelle, FIRE n’est pas atteignable",
            )

    # --- Âge d’indépendance ---
    with col4:
        if annees_fire < 100:
            if age_fire <= 40:
                delta_text = "🌟 Retraite précoce"
                delta_color = "normal"
            elif age_fire <= 55:
                delta_text = "🎯 Pré-retraite"
                delta_color = "normal"
            else:
                delta_text = "📅 Retraite standard"
                delta_color = "off"

            st.metric(
                label="🎂 Âge d’indépendance",
                value=f"{age_fire:.0f} ans",
                delta=delta_text,
                delta_color=delta_color,
                help="Votre âge estimé à l’atteinte de l’indépendance financière",
            )
        else:
            st.metric(
                label="🎂 Âge d’indépendance",
                value="N/A",
                delta="Objectif non atteignable",
                delta_color="inverse",
            )

    st.metric(
        label="📊 Progression vers FIRE",
        value=f"{progres_fire:.1f}%",
        delta=f"{format_nombre(patrimoine_manquant)} € restants",
    )

    st.progress(progres_fire / 100)

    # Note explicative
    st.markdown("---")

    # Simulation évolution patrimoine
    if annees_fire < 50:
        annees_sim = list(range(0, int(annees_fire) + 10))
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

        if patrimoine_actuel <= patrimoine_manquant:
            fig_fire = go.Figure()
            fig_fire.add_trace(
                go.Scatter(
                    x=annees_sim,
                    y=patrimoine_evolution,
                    mode="lines",
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
        else:
            # === Message de réussite FIRE ===
            with st.container():
                st.markdown("### 🏆 Objectif atteint : Indépendance Financière")
                st.success("🎉 Félicitations ! Vous avez atteint votre objectif FIRE.")
                st.markdown(
                    "Votre capital couvre désormais **vos dépenses annuelles à vie**, selon la **règle des 4%**.\n\n"
                    "Vous pouvez désormais **choisir de ne plus travailler pour l'argent**. "
                    "Libre à vous de ralentir, pivoter ou explorer de nouveaux projets !"
                )
                st.balloons()
            horizon_projection = int(annees_fire) + 5
            fig_fire = go.Figure()
            fig_fire.add_trace(
                go.Scatter(
                    x=annees_sim,
                    y=patrimoine_evolution,
                    mode="lines",
                    name="Patrimoine projeté",
                    line=dict(color="#2ca02c"),
                )
            )
            fig_fire.add_hline(
                y=nombre_fire,
                line_dash="dash",
                line_color="red",
                annotation_text="Seuil FIRE atteint",
                annotation_position="top right",
            )
            fig_fire.update_layout(
                title="🚀 Projection au-delà de l'indépendance financière",
                xaxis_title="Années",
                yaxis_title="Patrimoine (€)",
                showlegend=True,
            )
            st.plotly_chart(fig_fire, use_container_width=True)
