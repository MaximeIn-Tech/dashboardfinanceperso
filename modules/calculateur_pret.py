import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.helpers import format_nombre


def calculateur_pret_render():
    st.header("🏠 Simulateur de Prêt Immobilier")

    # Taux économiques - à mettre à jour dynamiquement plus tard

    taux_usure = 6.24  # Exemple pour prêt >20 ans (mai 2025)
    taux_bce = 4.25  # Taux directeur BCE

    with st.expander("📊 Informations de marché (taux)", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Taux d'usure (20 ans+)", "6.24 %")
        with col2:
            st.metric("Taux directeur BCE", "4.25 %")

        st.caption("Données à jour de la Banque de France / BCE.")

    # Interface d'entrée avec colonnes
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 💰 Montant du prêt")
        montant = st.number_input(
            "Montant emprunté (€)",
            min_value=1000,
            max_value=2_000_000,
            value=250_000,
            step=1_000,
            help="Rentrez le montant que vous souhaitez emprunter.",
        )

    with col2:
        st.markdown("### 📅 Durée du prêt")

        col_duree, col_unite = st.columns([4, 2])

        with col_unite:
            unite_duree = st.selectbox("", options=["ans", "mois"])

        with col_duree:
            if unite_duree == "ans":
                duree = st.number_input(
                    "Durée du prêt", min_value=1, max_value=30, value=20
                )
                duree_mois = duree * 12
            else:
                duree = st.number_input(
                    "Durée du prêt", min_value=12, max_value=360, value=240, step=12
                )
                duree_mois = duree

    with col3:
        st.markdown("### 📈 Taux d'intérêt")
        taeg = st.number_input(
            "TAEG (%)",
            min_value=0.1,
            max_value=10.0,
            value=2.5,
            step=0.1,
            help=(
                "Le TAEG (Taux Annuel Effectif Global) inclut **tous les frais** du crédit : "
                "taux nominal, assurance, frais de dossier, etc. "
                "C'est le meilleur indicateur pour comparer les offres entre elles."
            ),
        )

    st.markdown("---")

    # Calculs
    mois = duree_mois
    taux_mensuel = taeg / 100 / 12
    if taux_mensuel > 0:
        mensualite = montant * (taux_mensuel / (1 - (1 + taux_mensuel) ** -mois))
    else:
        mensualite = montant / mois

    # Construction du tableau d'amortissement
    data = []
    capital_restant = montant
    cumul_interets = 0
    cumul_capital = 0

    for i in range(0, mois + 1):
        if i == 0:
            data.append(
                {
                    "Mois": i,
                    "Année": 0,
                    "Mensualité": 0,
                    "Intérêts": 0,
                    "Capital": 0,
                    "Cumul_Interets": 0,
                    "Cumul_Capital": 0,
                    "Capital_Restant": round(capital_restant, 2),
                }
            )
        else:
            interet = round(capital_restant * taux_mensuel, 2)

            # Dernier mois : on ajuste pour solder le capital restant
            if i == mois:
                capital = capital_restant
                mensualite = round(capital + interet, 2)
            else:
                capital = round(mensualite - interet, 2)

            capital_restant = round(max(0, capital_restant - capital), 2)
            cumul_interets = round(cumul_interets + interet, 2)
            cumul_capital = round(cumul_capital + capital, 2)

            data.append(
                {
                    "Mois": i,
                    "Année": (i - 1) // 12 + 1,
                    "Mensualité": mensualite,
                    "Intérêts": interet,
                    "Capital": capital,
                    "Cumul_Interets": cumul_interets,
                    "Cumul_Capital": cumul_capital,
                    "Capital_Restant": capital_restant,
                }
            )

    df = pd.DataFrame(data)

    # Métriques principales
    total_interets = df["Cumul_Interets"].iloc[-1]
    total_rembourse = mensualite * mois
    ratio_interet = total_interets / montant

    # Affichage des métriques avec des couleurs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🏦 Montant emprunté",
            f"{format_nombre(montant)} €",
            help="Capital initial emprunté",
        )

    with col2:
        st.metric(
            "💸 Mensualité",
            f"{mensualite:,.0f}".replace(",", " ") + " €",
            help="Montant à payer chaque mois",
        )

    with col3:
        st.metric(
            "📈 Intérêts totaux",
            f"{format_nombre(total_interets)} €",
            delta=f"{ratio_interet:.1%} du capital",
            help="Total des intérêts sur toute la durée",
        )

    with col4:
        st.metric(
            "💰 Coût total",
            f"{format_nombre(total_rembourse)} €",
            help="Montant total remboursé",
        )

    # Indicateur de qualité du taux
    if ratio_interet < 0.15:
        st.success("🎉 **Excellent taux !** Votre prêt est très avantageux.")
    elif ratio_interet < 0.35:
        st.warning("⚡ **Taux correct.** Dans la moyenne du marché.")
    else:
        st.error("🔥 **Attention !** Ce prêt est coûteux en intérêts.")

    st.markdown("---")

    df = df.rename(
        columns={
            "Mensualité": "Mensualité (€)",
            "Intérêts": "Intérêts (€)",
            "Capital": "Capital Remboursé (€)",
            "Cumul_Interets": "Cumul Intérêts (€)",
            "Cumul_Capital": "Cumul Capital (€)",
            "Capital_Restant": "Capital Restant (€)",
        }
    )

    # Création des tabs
    tabs = st.tabs(["Graphiques", "Tableau complet", "Résumé par année"])

    with tabs[0]:
        fig = go.Figure()

        # Montant total payé (mensualités cumulées)
        fig.add_trace(
            go.Scatter(
                x=df["Mois"],
                y=df["Mensualité (€)"].cumsum(),
                name="Total Remboursé (€)",
                line=dict(color="blue"),
            )
        )

        # Capital réellement remboursé
        fig.add_trace(
            go.Scatter(
                x=df["Mois"],
                y=df["Cumul Capital (€)"],
                name="Création de Patrimoine (€)",
                line=dict(color="green"),
            )
        )

        # Intérêts cumulés
        fig.add_trace(
            go.Scatter(
                x=df["Mois"],
                y=df["Cumul Intérêts (€)"],
                name="Coût des Intérêts (€)",
                line=dict(color="red", dash="dot"),
            )
        )

        fig.update_layout(
            title="Impact des Intérêts sur la Création de Patrimoine",
            xaxis_title="Mois",
            yaxis_title="Montant (€)",
            hovermode="x unified",
            template="plotly_white",
            height=550,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.subheader("Tableau d'amortissement complet")
        st.dataframe(
            df.style.format("{:.2f}"), hide_index=True, use_container_width=True
        )

    with tabs[2]:
        st.subheader("Résumé annuel")
        df_annual = (
            df.groupby("Année")
            .agg(
                {
                    "Mensualité (€)": "mean",
                    "Intérêts (€)": "sum",
                    "Capital Remboursé (€)": "sum",
                    "Cumul Intérêts (€)": "max",
                    "Cumul Capital (€)": "max",
                    "Capital Restant (€)": "min",
                }
            )
            .reset_index()
        )
        st.dataframe(
            df_annual.style.format("{:.2f}"), hide_index=True, use_container_width=True
        )
