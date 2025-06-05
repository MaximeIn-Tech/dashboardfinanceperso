import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.helpers import format_nombre, load_css

css = load_css()


def calculateur_impots_render():
    st.header("🧮 Calculateur d'Impôts et TMI")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Revenus")
        revenus_imposables = st.number_input(
            "Revenus bruts annuels (€)",
            min_value=0.0,
            value=45000.0,
            step=1000.0,
            format="%.0f",
            key="tmi_revenus",
        )

        situation_familiale = st.selectbox(
            "Situation familiale",
            [
                "Célibataire",
                "Marié(e)/Pacsé(e)",
                "Marié(e) avec 1 enfant",
                "Marié(e) avec 2 enfants",
                "Marié(e) avec 3 enfants",
            ],
            key="tmi_situation",
        )

        parts_fiscales = {
            "Célibataire": 1,
            "Marié(e)/Pacsé(e)": 2,
            "Marié(e) avec 1 enfant": 2.5,
            "Marié(e) avec 2 enfants": 3,
            "Marié(e) avec 3 enfants": 4,
        }

        nb_parts = parts_fiscales[situation_familiale]

    with col2:
        st.subheader("⚙️ Paramètres")
        annee_fiscale = st.selectbox("Année fiscale", [2024, 2023], key="tmi_annee")

        # Application de l'abattement de 10 % sur les revenus (plafonné à 13 522 € pour 2024)
        plafond_abattement = 13522 if annee_fiscale == 2024 else 12912
        abattement_10 = min(revenus_imposables * 0.10, plafond_abattement)
        revenus_abattus = revenus_imposables - abattement_10

        st.info(f"📊 Nombre de parts fiscales : {nb_parts}")
        st.info(
            f"📉 Abattement de 10% appliqué : {abattement_10:,.0f} €\n\n"
            f"Revenus imposables après abattement : {revenus_abattus:,.0f} €"
        )

    # Barème 2024 (revenus 2023)
    if annee_fiscale == 2024:
        tranches = [
            (0, 11497, 0),
            (11498, 29315, 11),
            (29316, 83823, 30),
            (83824, 180294, 41),
            (180294, float("inf"), 45),
        ]
    else:  # 2023
        tranches = [
            (0, 11497, 0),
            (11498, 29315, 11),
            (29316, 83823, 30),
            (83824, 180294, 41),
            (180294, float("inf"), 45),
        ]

    # Calcul du quotient familial
    quotient_familial = revenus_abattus / nb_parts

    # Calcul de l'impôt par part
    impot_par_part = 0
    tmi = 0
    impot_par_tranche = []

    for seuil_inf, seuil_sup, taux in tranches:
        if quotient_familial > seuil_inf:
            base_imposable = min(quotient_familial, seuil_sup) - seuil_inf
            impot_tranche = base_imposable * (taux / 100)
            impot_par_part += impot_tranche
            impot_par_tranche.append(
                (
                    f"{seuil_inf:,.0f} - {seuil_sup if seuil_sup != float('inf') else '∞'} €",
                    impot_tranche * nb_parts,
                )
            )
            if quotient_familial > seuil_inf:
                tmi = taux

    # Impôt total
    impot_brut = impot_par_part * nb_parts

    # Décote (si applicable)
    if nb_parts <= 2:
        seuil_decote = 1929 if annee_fiscale == 2024 else 1837
        plafond_decote = 2590 if annee_fiscale == 2024 else 2469
    else:
        seuil_decote = (1929 if annee_fiscale == 2024 else 1837) * nb_parts / 2
        plafond_decote = (2590 if annee_fiscale == 2024 else 2469) * nb_parts / 2

    decote = 0
    if impot_brut < seuil_decote:
        decote = min(impot_brut, (seuil_decote - impot_brut) * 0.45)

    impot_net = max(0, impot_brut - decote)

    # Taux moyen
    taux_moyen = (impot_net / revenus_imposables * 100) if revenus_abattus > 0 else 0

    # Revenus nets après IR
    revenus_nets_ir = revenus_abattus - impot_net

    # Calcul des cotisations sociales (estimation)
    if st.checkbox("Inclure les cotisations sociales", key="tmi_cotisations"):
        st.subheader("🏥 Cotisations sociales")

        statut = st.selectbox(
            "Statut", ["Salarié", "Fonctionnaire", "Indépendant"], key="tmi_statut"
        )

        if statut == "Salarié":
            cotisations_rate = 0.225  # ~22.5% (estimation globale)
        elif statut == "Fonctionnaire":
            cotisations_rate = 0.21  # ~21%
        else:  # Indépendant
            cotisations_rate = 0.45  # ~45% (charges sociales élevées)

        cotisations = revenus_imposables * cotisations_rate
        revenus_nets_total = revenus_imposables - impot_net - cotisations
    else:
        cotisations = 0
        revenus_nets_total = revenus_nets_ir

    st.markdown("---")

    # Résultats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💼 Revenus annuels imposables", f"{format_nombre(revenus_abattus)} €"
        )

    with col2:
        st.metric(
            "📊 TMI",
            f"{tmi}%",
            help="Tranche Marginale d'Imposition - taux appliqué à votre dernière tranche de revenus",
        )

    with col3:
        st.metric(
            "📈 Taux moyen",
            f"{taux_moyen:.1f}%",
            help="Taux réel d'imposition sur l'ensemble de vos revenus",
        )

    with col4:
        st.metric("💸 Impôt sur le revenu", f"{impot_net:,.0f} €")

    if cotisations > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏥 Cotisations sociales", f"{cotisations:,.0f} €")
        with col2:
            st.metric("🔢 Total prélèvements", f"{impot_net + cotisations:,.0f} €")
        with col3:
            st.metric("💰 Revenus nets totaux", f"{revenus_nets_total:,.0f} €")
        with col4:
            taux_global = (
                ((impot_net + cotisations) / revenus_imposables * 100)
                if revenus_imposables > 0
                else 0
            )
            st.metric("📊 Taux global", f"{taux_global:.1f}%")

    # Détail des tranches
    st.subheader("📋 Détail du calcul par tranches")
    col1, col2 = st.columns(2)
    with col1:
        detail_tranches = []
        cumul_impot = 0
        for i, (seuil_inf, seuil_sup, taux) in enumerate(tranches):
            if quotient_familial > seuil_inf:
                base = min(quotient_familial, seuil_sup) - seuil_inf
                impot_tranche = base * (taux / 100)
                cumul_impot += impot_tranche
                if seuil_sup == float("inf"):
                    tranche_desc = f"Au-delà de {seuil_inf:,.0f} €"
                else:
                    tranche_desc = f"De {seuil_inf:,.0f} € à {seuil_sup:,.0f} €"
                detail_tranches.append(
                    {
                        "Tranche": tranche_desc,
                        "Taux": f"{taux}%",
                        "Base (QF)": f"{base:,.0f} €",
                        "Impôt/part": f"{impot_tranche:,.0f} €",
                        "Impôt total": f"{impot_tranche * nb_parts:,.0f} €",
                    }
                )

        if detail_tranches:
            df_tranches = pd.DataFrame(detail_tranches)
            st.dataframe(df_tranches, hide_index=True)

        if decote > 0:
            st.info(f"✅ Décote appliquée : {decote:,.0f} € (impôt réduit)")

    # Graphiques répartition

    with col2:
        # Demi-camembert pour les tranches d'imposition
        if detail_tranches:
            # Préparer les données pour le graphique des tranches
            tranches_values = []
            tranches_labels = []
            tranches_colors = ["#e8f4fd", "#87ceeb", "#4682b4", "#ff6b6b", "#ff4757"]

            for i, tranche in enumerate(detail_tranches):
                # Récupérer le montant d'impôt total pour chaque tranche
                impot_value = float(
                    tranche["Impôt total"].replace(" €", "").replace(",", "")
                )
                if impot_value > 0:
                    tranches_values.append(impot_value)
                    tranches_labels.append(f"Tranche {tranche['Taux']}")

            if tranches_values:
                # Créer le demi-camembert
                fig_semi = go.Figure(
                    data=[
                        go.Pie(
                            labels=tranches_labels,
                            values=tranches_values,
                            hole=0.3,
                            direction="clockwise",
                            sort=False,
                            marker_colors=tranches_colors[: len(tranches_values)],
                            textinfo="label+value",
                            textposition="auto",
                            # Configuration pour faire un demi-cercle
                            rotation=90,
                            pull=[
                                0.1 if i == 0 else 0
                                for i in range(len(tranches_values))
                            ],
                        )
                    ]
                )

                # Configurer le layout pour un demi-cercle
                fig_semi.update_layout(
                    title="Tranches d'imposition",
                    showlegend=True,
                    legend=dict(
                        orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01
                    ),
                    margin=dict(l=20, r=20, t=40, b=20),
                    # Force un demi-cercle en limitant l'angle
                    shapes=[
                        dict(
                            type="rect",
                            xref="paper",
                            yref="paper",
                            x0=0,
                            y0=0,
                            x1=1,
                            y1=0.5,
                            fillcolor="white",
                            line=dict(color="white", width=0),
                            layer="above",
                        )
                    ],
                )

                # Alternative plus simple : utiliser un graphique en secteurs avec rotation
                fig_semi_alt = px.pie(
                    values=tranches_values,
                    names=tranches_labels,
                    title="Tranches d'imposition",
                    color_discrete_sequence=tranches_colors[: len(tranches_values)],
                )

                # Modifier pour ressembler à un demi-camembert
                fig_semi_alt.update_traces(
                    rotation=90,
                    direction="clockwise",
                    textinfo="label+value",
                    textposition="auto",
                    hole=0.4,
                    pull=[0.05] * len(tranches_values),
                )

                fig_semi_alt.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5
                    ),
                    margin=dict(l=20, r=20, t=40, b=80),
                )

                st.plotly_chart(fig_semi_alt, use_container_width=True)
            else:
                st.info("Aucune tranche d'imposition applicable")
        else:
            st.info("Aucune donnée de tranche disponible")

        # Conseils d'optimisation fiscale
    # Conseils d'optimisation fiscale
    st.subheader("💡 Conseils d'optimisation fiscale")

    # CSS personnalisé qui utilise automatiquement les variables CSS de Streamlit
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # Créer les conseils avec catégories et priorités
    conseils_data = []

    if tmi >= 30:
        conseils_data.append(
            {
                "titre": "Plan d'Épargne en Actions (PEA)",
                "emoji": "🏦",
                "description": "Optimisez vos investissements avec un PEA",
                "avantage": "Exonéré d'impôt après 5 ans",
                "priorite": "Élevée",
                "categorie": "Épargne & Investissement",
            }
        )

    conseils_data.append(
        {
            "titre": "Assurance-vie",
            "emoji": "🏠",
            "description": "Profitez de l'abattement fiscal",
            "avantage": "4 600€/an d'abattement après 8 ans",
            "priorite": "Élevée",
            "categorie": "Épargne & Investissement",
        }
    )

    if tmi >= 41:
        conseils_data.append(
            {
                "titre": "Plan d'Épargne Retraite (PER)",
                "emoji": "📊",
                "description": "Déduction fiscale sur vos revenus",
                "avantage": "Jusqu'à 10% de vos revenus déductibles",
                "priorite": "Très élevée",
                "categorie": "Retraite & Défiscalisation",
            }
        )

        conseils_data.append(
            {
                "titre": "Investissement locatif",
                "emoji": "🏡",
                "description": "Déficit foncier déductible",
                "avantage": "Réduction d'impôt par déficit foncier",
                "priorite": "Moyenne",
                "categorie": "Immobilier",
            }
        )

    if revenus_imposables > 50000:
        conseils_data.append(
            {
                "titre": "Dons aux associations",
                "emoji": "🎯",
                "description": "Soutenez des causes tout en réduisant vos impôts",
                "avantage": "66% de réduction d'impôt",
                "priorite": "Moyenne",
                "categorie": "Solidarité",
            }
        )

        conseils_data.append(
            {
                "titre": "FCPI/FIP",
                "emoji": "💼",
                "description": "Investissement dans l'innovation",
                "avantage": "18% de réduction d'impôt",
                "priorite": "Faible",
                "categorie": "Investissement à risque",
            }
        )

    if situation_familiale == "Célibataire":
        conseils_data.append(
            {
                "titre": "PACS ou Mariage",
                "emoji": "💑",
                "description": "Optimisation fiscale selon les revenus du conjoint",
                "avantage": "Possible réduction selon situation",
                "priorite": "Variable",
                "categorie": "Situation familiale",
            }
        )

    # Affichage moderne des conseils
    if conseils_data:
        # Grouper par priorité
        priorites = {
            "Très élevée": {"conseils": [], "icon": "🔥", "css_class": "tres-elevee"},
            "Élevée": {"conseils": [], "icon": "⭐", "css_class": "elevee"},
            "Moyenne": {"conseils": [], "icon": "💡", "css_class": "moyenne"},
            "Faible": {"conseils": [], "icon": "💭", "css_class": "faible"},
            "Variable": {"conseils": [], "icon": "🤔", "css_class": "variable"},
        }

        for conseil in conseils_data:
            priorites[conseil["priorite"]]["conseils"].append(conseil)

        # Afficher par ordre de priorité
        for priorite, data in priorites.items():
            if data["conseils"]:
                st.markdown(
                    f"""
                <div class="priorite-header priorite-{data['css_class']}">
                    {data['icon']} Priorité {priorite}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Créer des colonnes pour les conseils de même priorité
                if len(data["conseils"]) == 1:
                    conseil = data["conseils"][0]
                    st.markdown(
                        f"""
                    <div class="conseil-card border-{data['css_class']}">
                        <div class="conseil-header">
                            <span class="conseil-emoji">{conseil['emoji']}</span>
                            <h5 class="conseil-title">{conseil['titre']}</h5>
                        </div>
                        <p class="conseil-description">{conseil['description']}</p>
                        <div class="conseil-avantage bg-{data['css_class']}">
                            💰 {conseil['avantage']}
                        </div>
                        <div class="conseil-categorie">
                            📂 {conseil['categorie']}
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    # Afficher en colonnes si plusieurs conseils
                    cols = st.columns(min(len(data["conseils"]), 2))
                    for i, conseil in enumerate(data["conseils"]):
                        with cols[i % 2]:
                            st.markdown(
                                f"""
                            <div class="conseil-card-compact border-{data['css_class']}">
                                <div class="conseil-header">
                                    <span style="font-size: 20px; margin-right: 8px;">{conseil['emoji']}</span>
                                    <h6 class="conseil-title-compact">{conseil['titre']}</h6>
                                </div>
                                <p class="conseil-description-compact">
                                    {conseil['description']}
                                </p>
                                <div class="conseil-avantage-compact bg-{data['css_class']}">
                                    💰 {conseil['avantage']}
                                </div>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )
    else:
        st.info(
            "Aucun conseil d'optimisation spécifique pour votre situation actuelle."
        )
