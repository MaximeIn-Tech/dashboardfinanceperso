import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


def achat_vs_location_render():
    # Fonction de calcul des mensualités de prêt
    def calcul_mensualite_emprunt(montant, taux_annuel, duree_annees):
        taux_mensuel = taux_annuel / 12
        n_mois = duree_annees * 12
        if taux_mensuel == 0:
            return montant / n_mois
        mensualite = montant * taux_mensuel / (1 - (1 + taux_mensuel) ** -n_mois)
        return mensualite

    # Fonction pour calculer le solde restant du prêt année après année
    def solde_restant_pret(montant, taux_annuel, duree_annees):
        mensualite = calcul_mensualite_emprunt(montant, taux_annuel, duree_annees)
        solde = montant
        taux_mensuel = taux_annuel / 12
        soldes_annuels = []
        for annee in range(1, duree_annees + 1):
            for _ in range(12):
                interet = solde * taux_mensuel
                principal = mensualite - interet
                solde -= principal
            soldes_annuels.append(max(solde, 0))
        return soldes_annuels

    # Entrées utilisateur
    st.header("🏠 Simulateur Acheter vs Louer")

    st.markdown(
        """
    <style>
    input[type=number] {
        border-radius: 0.5rem;
        padding: 0.5rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("### 📋 Paramètres de la simulation")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🏡 Acheter")
            with st.expander("Paramètres achat", expanded=True):
                prix_bien = st.number_input(
                    "Prix du bien (€)",
                    100000,
                    2000000,
                    300000,
                    step=10000,
                    help="Prix d'achat du bien immobilier.",
                )
                apport = st.number_input(
                    "Apport initial (€)",
                    0,
                    1000000,
                    50000,
                    step=5000,
                    help="Montant que vous apportez au départ, réduit le montant à emprunter.",
                )
                taux_emprunt = (
                    st.number_input(
                        "Taux emprunt (%)",
                        0.0,
                        10.0,
                        2.5,
                        step=0.1,
                        help="Taux d'intérêt annuel du crédit immobilier.",
                    )
                    / 100
                )
                duree_credit = st.number_input(
                    "Durée du crédit (ans)",
                    5,
                    30,
                    20,
                    help="Durée de remboursement du prêt immobilier.",
                )
                frais_notaire = (
                    st.number_input(
                        "Frais d'achat (%)",
                        0.0,
                        10.0,
                        7.5,
                        step=0.1,
                        help="Frais de notaire et frais d'acquisition (% du prix du bien).",
                    )
                    / 100
                )
                entretien_annuel = st.number_input(
                    "Frais annuels (entretien, taxes, etc.) (€)",
                    0,
                    10000,
                    2000,
                    help="Dépenses annuelles liées à l'entretien du bien, taxes, etc.",
                )
                croissance_immo = (
                    st.number_input(
                        "Croissance du marché immobilier (%)",
                        -5.0,
                        10.0,
                        1.5,
                        step=0.1,
                        help="Estimation de la croissance annuelle de la valeur du bien.",
                    )
                    / 100
                )
                frais_revente = (
                    st.number_input(
                        "Frais de revente (%)",
                        0.0,
                        10.0,
                        6.0,
                        step=0.1,
                        help="Frais estimés lors de la revente du bien (agence, notaire, etc.).",
                    )
                    / 100
                )

        with col2:
            st.markdown("#### 🏠 Louer")
            with st.expander("Paramètres location", expanded=True):
                loyer_initial = st.number_input(
                    "Loyer mensuel (€)",
                    300,
                    5000,
                    1000,
                    step=50,
                    help="Montant du loyer mensuel initial.",
                )
                croissance_loyer = (
                    st.number_input(
                        "Croissance annuelle du loyer (%)",
                        0.0,
                        5.0,
                        1.5,
                        step=0.1,
                        help="Taux d'augmentation annuel du loyer.",
                    )
                    / 100
                )
                rendement_portefeuille = (
                    st.number_input(
                        "Rendement des investissements (%)",
                        0.0,
                        10.0,
                        5.0,
                        step=0.1,
                        help="Rendement annuel des investissements réalisés avec l'argent non utilisé pour acheter.",
                    )
                    / 100
                )
                duree_projection = st.number_input(
                    "Durée de la projection (années)",
                    5,
                    40,
                    20,
                    help="Nombre total d'années pour la comparaison entre l'achat et la location.",
                )

        # Calculs initiaux
        montant_emprunte = prix_bien - apport
        mensualite_credit = calcul_mensualite_emprunt(
            montant_emprunte, taux_emprunt, duree_credit
        )
        cout_initial_achat = apport + prix_bien * frais_notaire

        # Solde du prêt chaque année
        soldes_pret = solde_restant_pret(montant_emprunte, taux_emprunt, duree_credit)

        # Simulation année par année
        data = []
        loyer = loyer_initial
        valeur_bien = prix_bien
        portefeuille_loc = cout_initial_achat  # L'apport est investi
        cash_acheteur = 0

        for annee in range(1, duree_projection + 1):
            valeur_bien *= 1 + croissance_immo

            cout_location = loyer * 12
            paiement_annuel_credit = (
                mensualite_credit * 12 if annee <= duree_credit else 0
            )
            interets_annuels = (
                soldes_pret[annee - 1] * taux_emprunt if annee <= duree_credit else 0
            )
            capital_rembourse = (
                paiement_annuel_credit - interets_annuels
                if annee <= duree_credit
                else 0
            )

            # Locataire : investit la différence entre mensualité crédit et loyer
            surplus_annuel = max(0, paiement_annuel_credit - cout_location)
            portefeuille_loc *= 1 + rendement_portefeuille
            portefeuille_loc += surplus_annuel

            # Acheteur : simule les liquidités restantes (ex. économies faites vs location)
            epargne_equivalente = max(0, cout_location - paiement_annuel_credit)
            cash_acheteur += epargne_equivalente
            cash_acheteur *= 1 + rendement_portefeuille

            # Solde du prêt
            solde_emprunt = soldes_pret[annee - 1] if annee <= duree_credit else 0
            valeur_nette_acheteur = (
                valeur_bien * (1 - frais_revente) - solde_emprunt + cash_acheteur
            )

            data.append(
                {
                    "Année": annee,
                    "Valeur Bien (€)": valeur_bien,
                    "Solde Emprunt (€)": solde_emprunt,
                    "Cash Acheteur (€)": cash_acheteur,
                    "Valeur Nette Acheteur (€)": valeur_nette_acheteur,
                    "Portefeuille Locataire (€)": portefeuille_loc,
                    "Loyer (€)": loyer,
                }
            )

            loyer *= 1 + croissance_loyer

        # Affichage
        df = pd.DataFrame(data)

        # Valeurs finales
        portefeuille_acheteur_final = df["Valeur Nette Acheteur (€)"].iloc[-1]
        portefeuille_locataire_final = df["Portefeuille Locataire (€)"].iloc[-1]

        # Calcul de la différence en pourcentage
        diff_pct = (
            100
            * (portefeuille_locataire_final - portefeuille_acheteur_final)
            / portefeuille_acheteur_final
        )

        st.subheader("📊 Comparaison finale")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="📦 Portefeuille Acheteur",
                value=f"{portefeuille_acheteur_final:,.0f} €",
            )

        with col2:
            delta_str = f"{diff_pct:+.1f} %"
            st.metric(
                label="💼 Portefeuille Locataire",
                value=f"{portefeuille_locataire_final:,.0f} €",
                delta=delta_str,
            )

        with col3:
            st.metric(
                label="🔍 Différence Relative",
                value=(
                    "Acheteur > Locataire" if diff_pct < 0 else "Locataire > Acheteur"
                ),
            )

        annee_croisement = None
        for i in range(1, len(df)):
            if (
                df["Portefeuille Locataire (€)"][i] > df["Valeur Nette Acheteur (€)"][i]
                and df["Portefeuille Locataire (€)"][i - 1]
                <= df["Valeur Nette Acheteur (€)"][i - 1]
            ):
                annee_croisement = df["Année"][i]
                break

        fig = go.Figure()

        # Trace Acheteur
        fig.add_trace(
            go.Scatter(
                x=df["Année"],
                y=df["Valeur Nette Acheteur (€)"],
                mode="lines",
                name="🏡 Valeur Nette Acheteur",
                line=dict(color="#2ca02c", width=3),
            )
        )

        # Trace Locataire
        fig.add_trace(
            go.Scatter(
                x=df["Année"],
                y=df["Portefeuille Locataire (€)"],
                mode="lines",
                name="💼 Portefeuille Locataire",
                line=dict(color="#ff7f0e", width=3),
            )
        )

        # Ajouter la ligne verticale de croisement
        if annee_croisement:
            fig.add_vline(
                x=annee_croisement, line_width=2, line_dash="dash", line_color="red"
            )
            fig.add_annotation(
                x=annee_croisement,
                y=max(
                    df["Portefeuille Locataire (€)"].max(),
                    df["Valeur Nette Acheteur (€)"].max(),
                ),
                text=f"📍 Croisement: Année {annee_croisement}",
                showarrow=True,
                arrowhead=1,
                bgcolor="white",
            )

        fig.update_layout(
            title="Évolution du patrimoine net - Acheter vs Louer",
            xaxis_title="Année",
            yaxis_title="Montant (€)",
            template="plotly_white",
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        st.info(
            """
        **💡 Interprétation :**
        - Le portefeuille locataire inclut l'apport investi et les économies réalisées chaque année.
        - La valeur nette acheteur tient compte de la revente du bien (avec frais) et du capital remboursé.
        - La ligne rouge verticale indique l'année où louer devient plus rentable qu'acheter (si applicable).
        """
        )
