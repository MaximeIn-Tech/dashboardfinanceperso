import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Calculateurs Financiers", page_icon="💰", layout="wide")

# Titre principal
st.title("💰 Calculateurs Financiers")
st.markdown("Une suite d'outils pour planifier vos finances personnelles")
st.markdown("---")

# Création des onglets
tab1, tab2 = st.tabs(["🏦 Intérêts Composés", "🔥 Calculateur FIRE"])

# ============= ONGLET 1: INTÉRÊTS COMPOSÉS =============
with tab1:
    st.header("🏦 Calculateur d'Intérêts Composés")

    # Paramètres principaux
    col1, col2, col3 = st.columns(3)

    with col1:
        calc_type = st.selectbox(
            "Type de calcul",
            ["Avec capital initial", "Sans capital initial"],
            key="ic_calc_type",
        )

        if calc_type == "Avec capital initial":
            capital_initial = st.number_input(
                "Capital initial (€)",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                key="ic_capital",
            )
        else:
            capital_initial = 0.0

    with col2:
        versement_periodique = st.number_input(
            "Versement périodique (€)",
            min_value=0.0,
            value=100.0,
            step=10.0,
            key="ic_versement",
        )

        frequence = st.selectbox(
            "Fréquence des versements",
            ["Mensuel", "Trimestriel", "Semestriel", "Annuel"],
            key="ic_freq",
        )

    with col3:
        taux_annuel = st.number_input(
            "Taux d'intérêt annuel (%)",
            min_value=0.0,
            max_value=50.0,
            value=5.0,
            step=0.1,
            key="ic_taux",
        )

        duree_annees = st.number_input(
            "Durée (années)",
            min_value=1,
            max_value=50,
            value=10,
            step=1,
            key="ic_duree",
        )

    # Options avancées
    st.subheader("Options avancées")
    col1, col2, col3 = st.columns(3)

    with col1:
        ajuster_inflation = st.checkbox(
            "Ajuster à l'inflation", value=False, key="ic_inflation_check"
        )

        if ajuster_inflation:
            taux_inflation = st.number_input(
                "Taux d'inflation annuel (%)",
                min_value=0.0,
                max_value=30.0,
                value=1.8,
                step=0.1,
                key="ic_inflation",
            )
        else:
            taux_inflation = 0.0

    with col2:
        calcul_apres_impot = st.checkbox(
            "Calcul après impôt", value=False, key="ic_impot_check"
        )

        if calcul_apres_impot:
            type_placement = st.selectbox(
                "Type de placement",
                ["CTO (Compte-titres ordinaire)", "PEA", "Assurance-vie"],
                key="ic_placement",
            )

    with col3:
        if calcul_apres_impot:
            if type_placement == "CTO (Compte-titres ordinaire)":
                st.info("📋 **CTO** : PFU de 30% (17,2% IR + 12,8% PS)")
                taux_imposition = 30.0
            elif type_placement == "PEA":
                st.info("📋 **PEA** : Exonéré après 5 ans + 12,8% PS")
                if duree_annees >= 5:
                    taux_imposition = 12.8  # Seulement prélèvements sociaux
                else:
                    taux_imposition = 30.0  # PFU complet si retrait avant 5 ans
            else:  # Assurance-vie
                st.info("📋 **AV** : Abattement + prélèvements selon ancienneté")
                if duree_annees >= 8:
                    taux_imposition = (
                        7.5 + 12.8
                    )  # 7,5% IR + 12,8% PS (après abattement)
                else:
                    taux_imposition = 12.8 + 12.8  # 12,8% IR + 12,8% PS
        else:
            taux_imposition = 0.0

    # Calculs pour intérêts composés
    freq_map = {"Mensuel": 12, "Trimestriel": 4, "Semestriel": 2, "Annuel": 1}
    n = freq_map[frequence]
    r = taux_annuel / 100
    t = duree_annees

    def calculer_interet_compose(P, PMT, r, n, t):
        FV_capital = P * (1 + r / n) ** (n * t)
        if PMT > 0 and r > 0:
            FV_versements = PMT * (((1 + r / n) ** (n * t) - 1) / (r / n))
        elif PMT > 0 and r == 0:
            FV_versements = PMT * n * t
        else:
            FV_versements = 0
        return FV_capital + FV_versements

    # Calculs avec options avancées
    valeur_finale_brute = calculer_interet_compose(
        capital_initial, versement_periodique, r, n, t
    )
    total_verse = capital_initial + (versement_periodique * n * t)
    interets_bruts = valeur_finale_brute - total_verse

    # Application de l'impôt sur les intérêts uniquement
    if calcul_apres_impot and interets_bruts > 0:
        # Calcul des abattements selon le type de placement
        if type_placement == "Assurance-vie" and duree_annees >= 8:
            # Abattement de 4 600€ pour une personne seule
            interets_imposables = max(0, interets_bruts - 4600)
        else:
            interets_imposables = interets_bruts

        impots_sur_interets = interets_imposables * (taux_imposition / 100)
        valeur_finale_nette = total_verse + (interets_bruts - impots_sur_interets)
        interets_nets = interets_bruts - impots_sur_interets
    else:
        valeur_finale_nette = valeur_finale_brute
        interets_nets = interets_bruts
        impots_sur_interets = 0

    # Ajustement inflation (sur la valeur finale)
    if ajuster_inflation:
        pouvoir_achat_final = valeur_finale_nette / ((1 + taux_inflation / 100) ** t)
        perte_pouvoir_achat = valeur_finale_nette - pouvoir_achat_final
    else:
        pouvoir_achat_final = valeur_finale_nette
        perte_pouvoir_achat = 0

    st.markdown("---")

    # Résultats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💼 Total versé", f"{total_verse:,.2f} €")
    with col2:
        if calcul_apres_impot:
            st.metric("💰 Valeur finale (nette)", f"{valeur_finale_nette:,.2f} €")
        else:
            st.metric("💰 Valeur finale", f"{valeur_finale_brute:,.2f} €")
    with col3:
        if calcul_apres_impot:
            st.metric(
                "📈 Intérêts nets",
                f"{interets_nets:,.2f} €",
                f"{(interets_nets/total_verse)*100:.1f}%" if total_verse > 0 else "0%",
            )
        else:
            st.metric(
                "📈 Intérêts bruts",
                f"{interets_bruts:,.2f} €",
                f"{(interets_bruts/total_verse)*100:.1f}%" if total_verse > 0 else "0%",
            )
    with col4:
        if ajuster_inflation:
            st.metric(
                "🛒 Pouvoir d'achat final",
                f"{pouvoir_achat_final:,.2f} €",
                (
                    f"-{(perte_pouvoir_achat/valeur_finale_nette)*100:.1f}%"
                    if valeur_finale_nette > 0
                    else "0%"
                ),
            )
        elif calcul_apres_impot and impots_sur_interets > 0:
            st.metric(
                "💸 Impôts payés",
                f"{impots_sur_interets:,.2f} €",
                f"{taux_imposition:.1f}%",
            )

    # Informations détaillées selon les options
    if calcul_apres_impot or ajuster_inflation:
        st.subheader("📊 Détail des calculs")
        col1, col2 = st.columns(2)

        with col1:
            if calcul_apres_impot:
                st.info(
                    f"""
                **Fiscalité {type_placement} :**
                - Intérêts bruts : {interets_bruts:,.2f} €
                - Taux d'imposition : {taux_imposition:.1f}%
                {"- Abattement appliqué : 4 600 €" if type_placement == "Assurance-vie" and duree_annees >= 8 else ""}
                - Impôts : {impots_sur_interets:,.2f} €
                - **Intérêts nets : {interets_nets:,.2f} €**
                """
                )

        with col2:
            if ajuster_inflation:
                st.warning(
                    f"""
                **Impact de l'inflation ({taux_inflation}%/an) :**
                - Valeur nominale : {valeur_finale_nette:,.2f} €
                - Valeur réelle : {pouvoir_achat_final:,.2f} €
                - Perte de pouvoir d'achat : {perte_pouvoir_achat:,.2f} €
                - **Rendement réel : {((pouvoir_achat_final/total_verse)*100-100):.1f}%**
                """
                )

    # Graphique évolution avec options
    annees = list(range(0, int(duree_annees) + 1))
    valeurs_brutes = []
    valeurs_nettes = []
    valeurs_reelles = []
    versements_cumules = []

    for annee in annees:
        # Valeur brute
        valeur_brute = calculer_interet_compose(
            capital_initial, versement_periodique, r, n, annee
        )
        valeurs_brutes.append(valeur_brute)

        # Versements cumulés
        verse_cumule = capital_initial + (versement_periodique * n * annee)
        versements_cumules.append(verse_cumule)

        # Valeur nette (après impôt)
        if calcul_apres_impot and annee > 0:
            interets_annee = valeur_brute - verse_cumule
            if type_placement == "Assurance-vie" and annee >= 8:
                interets_imposables_annee = max(0, interets_annee - 4600)
            else:
                interets_imposables_annee = interets_annee

            # Adaptation du taux d'imposition selon l'ancienneté
            if type_placement == "PEA" and annee >= 5:
                taux_annee = 12.8
            elif type_placement == "Assurance-vie" and annee >= 8:
                taux_annee = 7.5 + 12.8
            elif type_placement == "Assurance-vie":
                taux_annee = 12.8 + 12.8
            else:
                taux_annee = taux_imposition

            impots_annee = interets_imposables_annee * (taux_annee / 100)
            valeur_nette = verse_cumule + (interets_annee - impots_annee)
        else:
            valeur_nette = valeur_brute

        valeurs_nettes.append(valeur_nette)

        # Valeur réelle (ajustée inflation)
        if ajuster_inflation and annee > 0:
            valeur_reelle = valeur_nette / ((1 + taux_inflation / 100) ** annee)
        else:
            valeur_reelle = valeur_nette

        valeurs_reelles.append(valeur_reelle)

    fig = go.Figure()

    # Versements cumulés
    fig.add_trace(
        go.Scatter(
            x=annees,
            y=versements_cumules,
            fill="tonexty",
            name="Versements cumulés",
            line=dict(color="#1f77b4"),
        )
    )

    # Valeur finale selon les options choisies
    if ajuster_inflation:
        fig.add_trace(
            go.Scatter(
                x=annees,
                y=valeurs_reelles,
                fill="tonexty",
                name="Valeur réelle (après inflation)",
                line=dict(color="#d62728"),
            )
        )
        if calcul_apres_impot:
            fig.add_trace(
                go.Scatter(
                    x=annees,
                    y=valeurs_nettes,
                    fill=None,
                    name="Valeur nette (avant inflation)",
                    line=dict(color="#ff7f0e", dash="dot"),
                )
            )
    elif calcul_apres_impot:
        fig.add_trace(
            go.Scatter(
                x=annees,
                y=valeurs_nettes,
                fill="tonexty",
                name="Valeur nette (après impôt)",
                line=dict(color="#ff7f0e"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=annees,
                y=valeurs_brutes,
                fill=None,
                name="Valeur brute (avant impôt)",
                line=dict(color="#2ca02c", dash="dot"),
            )
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=annees,
                y=valeurs_brutes,
                fill="tonexty",
                name="Valeur totale",
                line=dict(color="#ff7f0e"),
            )
        )

    fig.update_layout(
        title="Évolution du capital avec options avancées",
        xaxis_title="Années",
        yaxis_title="Montant (€)",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

# ============= ONGLET 2: CALCULATEUR FIRE =============
with tab2:
    st.header("🔥 Calculateur FIRE (Financial Independence, Retire Early)")

    col1, col2, col3 = st.columns(3)

    with col1:
        revenus_annuels = st.number_input(
            "Revenus annuels nets (€)",
            min_value=0.0,
            value=40000.0,
            step=1000.0,
            key="fire_revenus",
        )

        depenses_annuelles = st.number_input(
            "Dépenses annuelles (€)",
            min_value=0.0,
            value=25000.0,
            step=1000.0,
            key="fire_depenses",
        )

    with col2:
        patrimoine_actuel = st.number_input(
            "Patrimoine actuel (€)",
            min_value=0.0,
            value=10000.0,
            step=1000.0,
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
        st.metric("💰 Nombre FIRE", f"{nombre_fire:,.0f} €")
    with col2:
        st.metric("📊 Taux d'épargne", f"{taux_epargne:.1f}%")
    with col3:
        if annees_fire < 100:
            st.metric("⏰ Années jusqu'à FIRE", f"{annees_fire:.1f} ans")
        else:
            st.metric("⏰ Années jusqu'à FIRE", "Impossible")
    with col4:
        if annees_fire < 100:
            st.metric("🎂 Âge FIRE", f"{age_fire:.0f} ans")
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
        - Épargne mensuelle : {epargne_annuelle/12:,.0f} €
        - Revenus passifs nécessaires : {depenses_annuelles:,.0f} €/an
        - Patrimoine manquant : {max(0, nombre_fire - patrimoine_actuel):,.0f} €
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

# # ============= ONGLET 3: ÉPARGNE LOGEMENT =============
# with tab3:
#     st.header("🏠 Calculateur d'Épargne Logement")

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         prix_logement = st.number_input(
#             "Prix du logement (€)",
#             min_value=0.0,
#             value=200000.0,
#             step=10000.0,
#             key="log_prix",
#         )

#         apport_personnel = st.slider(
#             "Apport personnel (%)",
#             min_value=0,
#             max_value=100,
#             value=20,
#             key="log_apport",
#         )

#     with col2:
#         epargne_actuelle = st.number_input(
#             "Épargne actuelle (€)",
#             min_value=0.0,
#             value=15000.0,
#             step=1000.0,
#             key="log_epargne",
#         )

#         epargne_mensuelle = st.number_input(
#             "Épargne mensuelle (€)",
#             min_value=0.0,
#             value=500.0,
#             step=50.0,
#             key="log_mens",
#         )

#     with col3:
#         taux_placement = st.number_input(
#             "Taux de placement (%)",
#             min_value=0.0,
#             max_value=10.0,
#             value=2.0,
#             step=0.1,
#             key="log_taux",
#         )

#         frais_notaire = st.number_input(
#             "Frais de notaire (%)",
#             min_value=0.0,
#             max_value=10.0,
#             value=7.5,
#             step=0.5,
#             key="log_frais",
#         )

#     # Calculs logement
#     apport_euros = prix_logement * (apport_personnel / 100)
#     frais_euros = prix_logement * (frais_notaire / 100)
#     total_necessaire = apport_euros + frais_euros
#     manque = max(0, total_necessaire - epargne_actuelle)

#     if epargne_mensuelle > 0 and taux_placement > 0:
#         r_mensuel = taux_placement / 100 / 12
#         if manque > 0:
#             mois_necessaires = np.log(
#                 1 + (manque * r_mensuel) / epargne_mensuelle
#             ) / np.log(1 + r_mensuel)
#         else:
#             mois_necessaires = 0
#     elif epargne_mensuelle > 0:
#         mois_necessaires = manque / epargne_mensuelle if manque > 0 else 0
#     else:
#         mois_necessaires = float("inf")

#     st.markdown("---")

#     # Résultats logement
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.metric("🏠 Apport nécessaire", f"{apport_euros:,.0f} €")
#     with col2:
#         st.metric("📋 Frais de notaire", f"{frais_euros:,.0f} €")
#     with col3:
#         st.metric("💰 Total nécessaire", f"{total_necessaire:,.0f} €")
#     with col4:
#         if mois_necessaires < 600:
#             st.metric("⏰ Temps d'épargne", f"{mois_necessaires/12:.1f} ans")
#         else:
#             st.metric("⏰ Temps d'épargne", "Trop long")

#     # Simulation épargne logement
#     if mois_necessaires < 120:  # Moins de 10 ans
#         mois_sim = list(range(0, int(mois_necessaires) + 12, 3))  # Tous les 3 mois
#         epargne_evolution = []

#         for mois in mois_sim:
#             if taux_placement > 0:
#                 r_mensuel = taux_placement / 100 / 12
#                 epargne = epargne_actuelle * (1 + r_mensuel) ** mois
#                 if epargne_mensuelle > 0 and mois > 0:
#                     epargne += epargne_mensuelle * (
#                         ((1 + r_mensuel) ** mois - 1) / r_mensuel
#                     )
#             else:
#                 epargne = epargne_actuelle + (epargne_mensuelle * mois)
#             epargne_evolution.append(epargne)

#         fig_log = go.Figure()
#         fig_log.add_trace(
#             go.Scatter(
#                 x=[m / 12 for m in mois_sim],
#                 y=epargne_evolution,
#                 name="Épargne projetée",
#                 line=dict(color="#2ca02c"),
#             )
#         )
#         fig_log.add_hline(
#             y=total_necessaire,
#             line_dash="dash",
#             line_color="red",
#             annotation_text="Objectif",
#         )
#         fig_log.update_layout(
#             title="Évolution de l'épargne logement",
#             xaxis_title="Années",
#             yaxis_title="Épargne (€)",
#         )
#         st.plotly_chart(fig_log, use_container_width=True)

# # ============= ONGLET 4: COMPARATEUR PLACEMENTS =============
# with tab4:
#     st.header("📊 Comparateur de Placements")

#     st.subheader("Paramètres communs")
#     col1, col2 = st.columns(2)
#     with col1:
#         montant_initial = st.number_input(
#             "Montant initial (€)",
#             min_value=0.0,
#             value=10000.0,
#             step=1000.0,
#             key="comp_initial",
#         )
#         versement_comp = st.number_input(
#             "Versement mensuel (€)",
#             min_value=0.0,
#             value=200.0,
#             step=50.0,
#             key="comp_versement",
#         )
#     with col2:
#         duree_comp = st.number_input(
#             "Durée (années)", min_value=1, max_value=40, value=15, key="comp_duree"
#         )

#     st.subheader("Taux de rendement par placement")
#     col1, col2, col3, col4 = st.columns(4)

#     with col1:
#         taux_livret = st.number_input(
#             "Livret A (%)",
#             min_value=0.0,
#             max_value=10.0,
#             value=3.0,
#             step=0.1,
#             key="comp_livret",
#         )
#         taux_ldds = st.number_input(
#             "LDDS (%)",
#             min_value=0.0,
#             max_value=10.0,
#             value=3.0,
#             step=0.1,
#             key="comp_ldds",
#         )

#     with col2:
#         taux_assurance = st.number_input(
#             "Assurance-vie (%)",
#             min_value=0.0,
#             max_value=15.0,
#             value=4.5,
#             step=0.1,
#             key="comp_av",
#         )
#         taux_pea = st.number_input(
#             "PEA (%)",
#             min_value=0.0,
#             max_value=15.0,
#             value=7.0,
#             step=0.5,
#             key="comp_pea",
#         )

#     with col3:
#         taux_cto = st.number_input(
#             "CTO (%)",
#             min_value=0.0,
#             max_value=15.0,
#             value=8.0,
#             step=0.5,
#             key="comp_cto",
#         )
#         taux_crypto = st.number_input(
#             "Crypto (%)",
#             min_value=0.0,
#             max_value=50.0,
#             value=15.0,
#             step=1.0,
#             key="comp_crypto",
#         )

#     with col4:
#         taux_immobilier = st.number_input(
#             "Immobilier (%)",
#             min_value=0.0,
#             max_value=20.0,
#             value=5.0,
#             step=0.5,
#             key="comp_immo",
#         )
#         taux_or = st.number_input(
#             "Or (%)", min_value=0.0, max_value=15.0, value=3.5, step=0.5, key="comp_or"
#         )

#     # Calculs comparatifs
#     placements = {
#         "Livret A": taux_livret,
#         "LDDS": taux_ldds,
#         "Assurance-vie": taux_assurance,
#         "PEA": taux_pea,
#         "CTO": taux_cto,
#         "Crypto": taux_crypto,
#         "Immobilier": taux_immobilier,
#         "Or": taux_or,
#     }

#     resultats = {}
#     for nom, taux in placements.items():
#         r_mensuel = taux / 100 / 12
#         if r_mensuel > 0:
#             valeur_finale = montant_initial * (1 + r_mensuel) ** (12 * duree_comp)
#             if versement_comp > 0:
#                 valeur_finale += versement_comp * (
#                     ((1 + r_mensuel) ** (12 * duree_comp) - 1) / r_mensuel
#                 )
#         else:
#             valeur_finale = montant_initial + (versement_comp * 12 * duree_comp)

#         total_verse = montant_initial + (versement_comp * 12 * duree_comp)
#         gain = valeur_finale - total_verse
#         resultats[nom] = {"valeur_finale": valeur_finale, "gain": gain, "taux": taux}

#     st.markdown("---")

#     # Tableau comparatif
#     df_comp = pd.DataFrame(
#         {
#             "Placement": list(resultats.keys()),
#             "Taux (%)": [resultats[p]["taux"] for p in resultats.keys()],
#             "Valeur finale (€)": [
#                 f"{resultats[p]['valeur_finale']:,.0f}" for p in resultats.keys()
#             ],
#             "Gains (€)": [f"{resultats[p]['gain']:,.0f}" for p in resultats.keys()],
#             "Rendement total (%)": [
#                 f"{(resultats[p]['gain']/(montant_initial + versement_comp * 12 * duree_comp))*100:.1f}"
#                 for p in resultats.keys()
#             ],
#         }
#     )

#     st.dataframe(df_comp, use_container_width=True)

#     # Graphique comparatif
#     fig_comp = px.bar(
#         x=list(resultats.keys()),
#         y=[resultats[p]["valeur_finale"] for p in resultats.keys()],
#         title="Comparaison des valeurs finales par placement",
#         labels={"x": "Placements", "y": "Valeur finale (€)"},
#     )
#     st.plotly_chart(fig_comp, use_container_width=True)

#     # Top 3 des placements
#     top_placements = sorted(
#         resultats.items(), key=lambda x: x[1]["valeur_finale"], reverse=True
#     )[:3]

#     col1, col2, col3 = st.columns(3)
#     for i, (nom, data) in enumerate(top_placements):
#         with [col1, col2, col3][i]:
#             st.metric(
#                 f"🏆 #{i+1} {nom}",
#                 f"{data['valeur_finale']:,.0f} €",
#                 f"+{data['gain']:,.0f} €",
#             )

st.markdown("---")
st.markdown(
    "💡 **Conseil** : Ces calculateurs sont à titre indicatif. Les rendements passés ne garantissent pas les performances futures."
)
