import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# from utils.helpers import custom_alert


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

        # Variables pour le locataire
        loyer = loyer_initial
        portefeuille_locataire = (
            cout_initial_achat  # Investit l'équivalent de l'apport + frais
        )

        # Variables pour l'acheteur
        valeur_bien = prix_bien

        for annee in range(1, duree_projection + 1):
            # === SCENARIO ACHETEUR ===
            # Valeur du bien qui augmente (à partir de la 2ème année)
            if annee > 1:
                valeur_bien *= 1 + croissance_immo

            # Mensualité du crédit (0 si prêt fini)
            mensualite_annuelle = mensualite_credit * 12 if annee <= duree_credit else 0

            # Solde restant du prêt
            solde_emprunt = soldes_pret[annee - 1] if annee <= duree_credit else 0

            # Valeur nette de l'acheteur (valeur du bien - solde du prêt - frais de revente)
            valeur_nette_acheteur = valeur_bien * (1 - frais_revente) - solde_emprunt

            # === SCENARIO LOCATAIRE ===
            # Coût du loyer pour l'année
            cout_loyer_annuel = loyer * 12

            # Différence mensuelle entre mensualité crédit et loyer
            difference_mensuelle = (
                (mensualite_credit - loyer) if annee <= duree_credit else -loyer
            )
            difference_annuelle = difference_mensuelle * 12

            # Le portefeuille du locataire croît avec les rendements
            portefeuille_locataire *= 1 + rendement_portefeuille

            # Si la mensualité est plus élevée que le loyer, le locataire peut investir la différence
            if difference_annuelle > 0:
                portefeuille_locataire += difference_annuelle

            # Si le prêt est fini, le locataire peut investir l'équivalent de ce que l'acheteur
            # ne paie plus (mais continue à payer le loyer)
            if annee > duree_credit:
                # L'acheteur n'a plus de mensualité, mais le locataire paie toujours le loyer
                # Le locataire peut investir l'équivalent de l'ancienne mensualité
                portefeuille_locataire += mensualite_credit * 12

            # L'acheteur paie des frais d'entretien que le locataire n'a pas
            # Le locataire peut investir cet équivalent
            portefeuille_locataire += entretien_annuel

            data.append(
                {
                    "Année": annee,
                    "Valeur Bien (€)": valeur_bien,
                    "Solde Emprunt (€)": solde_emprunt,
                    "Mensualité Annuelle (€)": mensualite_annuelle,
                    "Coût Loyer Annuel (€)": cout_loyer_annuel,
                    "Valeur Nette Acheteur (€)": valeur_nette_acheteur,
                    "Portefeuille Locataire (€)": portefeuille_locataire,
                    "Loyer Mensuel (€)": loyer,
                    "Différence Mensuelle (€)": difference_mensuelle,
                }
            )

            # Augmentation du loyer pour l'année suivante
            loyer *= 1 + croissance_loyer

        # Création du DataFrame
        df = pd.DataFrame(data)

        # Valeurs finales
        portefeuille_acheteur_final = df["Valeur Nette Acheteur (€)"].iloc[-1]
        portefeuille_locataire_final = df["Portefeuille Locataire (€)"].iloc[-1]

        # Calcul de la différence en pourcentage
        if portefeuille_acheteur_final > 0:
            diff_pct = (
                100
                * (portefeuille_locataire_final - portefeuille_acheteur_final)
                / portefeuille_acheteur_final
            )
        else:
            diff_pct = 0

        st.subheader("📊 Comparaison finale")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="🏡 Patrimoine Acheteur",
                value=f"{portefeuille_acheteur_final:,.0f} €",
                help="Valeur nette du bien immobilier après déduction des frais de revente et du solde du prêt",
            )

        with col2:
            delta_str = f"{diff_pct:+.1f} %"
            st.metric(
                label="💼 Portefeuille Locataire",
                value=f"{portefeuille_locataire_final:,.0f} €",
                delta=delta_str,
                help="Portefeuille financier constitué grâce aux économies réalisées par rapport à l'achat",
            )

        with col3:
            avantage = (
                "🏡 Acheteur"
                if portefeuille_acheteur_final > portefeuille_locataire_final
                else "💼 Locataire"
            )
            ecart = abs(portefeuille_acheteur_final - portefeuille_locataire_final)
            st.metric(
                label="🏆 Avantage",
                value=avantage,
                delta=f"{ecart:,.0f} €",
                help="Qui a le meilleur patrimoine final et l'écart en euros",
            )

        # Recherche du point de croisement
        annee_croisement = None
        for i in range(1, len(df)):
            if (
                df["Portefeuille Locataire (€)"].iloc[i]
                > df["Valeur Nette Acheteur (€)"].iloc[i]
                and df["Portefeuille Locataire (€)"].iloc[i - 1]
                <= df["Valeur Nette Acheteur (€)"].iloc[i - 1]
            ):
                annee_croisement = df["Année"].iloc[i]
                break

        # Graphique principal
        fig = go.Figure()

        # Trace Acheteur
        fig.add_trace(
            go.Scatter(
                x=df["Année"],
                y=df["Valeur Nette Acheteur (€)"],
                mode="lines+markers",
                name="🏡 Patrimoine Acheteur",
                line=dict(color="#2ca02c", width=3),
                marker=dict(size=4),
                hovertemplate="<b>Acheteur</b><br>Année: %{x}<br>Patrimoine: %{y:,.0f} €<extra></extra>",
            )
        )

        # Trace Locataire
        fig.add_trace(
            go.Scatter(
                x=df["Année"],
                y=df["Portefeuille Locataire (€)"],
                mode="lines+markers",
                name="💼 Portefeuille Locataire",
                line=dict(color="#ff7f0e", width=3),
                marker=dict(size=4),
                hovertemplate="<b>Locataire</b><br>Année: %{x}<br>Portefeuille: %{y:,.0f} €<extra></extra>",
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
                )
                * 0.9,
                text=f"📍 Croisement: Année {annee_croisement}",
                showarrow=True,
                arrowhead=1,
                bgcolor="white",
                bordercolor="red",
                borderwidth=1,
            )

        fig.update_layout(
            title="📈 Évolution du patrimoine - Acheter vs Louer",
            xaxis_title="Année",
            yaxis_title="Patrimoine (€)",
            template="plotly_white",
            hovermode="x unified",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            height=500,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tableau détaillé
        with st.expander("📋 Tableau détaillé année par année"):
            st.dataframe(
                df.style.format(
                    {
                        "Valeur Bien (€)": "{:,.0f}",
                        "Solde Emprunt (€)": "{:,.0f}",
                        "Mensualité Annuelle (€)": "{:,.0f}",
                        "Coût Loyer Annuel (€)": "{:,.0f}",
                        "Valeur Nette Acheteur (€)": "{:,.0f}",
                        "Portefeuille Locataire (€)": "{:,.0f}",
                        "Loyer Mensuel (€)": "{:,.0f}",
                        "Différence Mensuelle (€)": "{:+,.0f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

        # Informations et interprétation
        st.info(
            f"""
            **💡 Interprétation des résultats :**

            **Acheteur :**
            - Investissement initial : {cout_initial_achat:,.0f} € (apport + frais)
            - Mensualité : {mensualite_credit:,.0f} €/mois pendant {duree_credit} ans
            - Frais d'entretien : {entretien_annuel:,.0f} €/an
            - Patrimoine final : {portefeuille_acheteur_final:,.0f} €

            **Locataire :**
            - Investissement initial : {cout_initial_achat:,.0f} € (équivalent apport + frais)
            - Loyer initial : {loyer_initial:,.0f} €/mois
            - Loyer final : {df['Loyer Mensuel (€)'].iloc[-1]:,.0f} €/mois
            - Portefeuille final : {portefeuille_locataire_final:,.0f} €

            **Hypothèses :**
            - Le locataire investit l'équivalent de l'apport + frais en bourse
            - Le locataire investit la différence mensuelle (si positive) entre mensualité et loyer
            - Le locataire investit l'équivalent des frais d'entretien qu'il n'a pas à payer
            - Après la fin du crédit, le locataire investit l'équivalent de l'ancienne mensualité
            """
        )

        # Analyse de sensibilité
        st.subheader("🔍 Analyse de sensibilité")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Impact du rendement des investissements**")
            if rendement_portefeuille > croissance_immo:
                st.success(
                    "✅ Le rendement boursier est supérieur à la croissance immobilière, favorisant la location"
                )
            else:
                st.warning(
                    "⚠️ La croissance immobilière est supérieure au rendement boursier, favorisant l'achat"
                )

        with col2:
            st.write("**Impact de la différence mensuelle**")
            diff_moy = df["Différence Mensuelle (€)"].mean()
            if diff_moy > 0:
                st.info(
                    f"💰 Économie moyenne : {diff_moy:,.0f} €/mois avec la location"
                )
            else:
                st.info(
                    f"💸 Surcoût moyen : {abs(diff_moy):,.0f} €/mois avec la location"
                )
