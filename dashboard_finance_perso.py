import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def calculer_tmi_simplifiee(revenus_annuels, nb_parts=1, annee=2024):
    """Calcul simplifié de la TMI"""
    if annee == 2024:
        tranches = [
            (0, 10777, 0),
            (10777, 27478, 11),
            (27478, 78570, 30),
            (78570, 168994, 41),
            (168994, float("inf"), 45),
        ]
    else:  # 2023
        tranches = [
            (0, 10225, 0),
            (10225, 26070, 11),
            (26070, 74545, 30),
            (74545, 160336, 41),
            (160336, float("inf"), 45),
        ]

    quotient_familial = revenus_annuels / nb_parts
    tmi = 0

    for seuil_inf, seuil_sup, taux in tranches:
        if quotient_familial > seuil_inf:
            tmi = taux

    return tmi


# Configuration de la page
st.set_page_config(page_title="Calculateurs Financiers", page_icon="💰", layout="wide")

# Titre principal
st.title("💰 Calculateurs Financiers")
st.markdown("Une suite d'outils pour planifier vos finances personnelles")

st.markdown(
    """
    <meta name="description" content="Une application Streamlit pour suivre facilement ses finances personnelles : revenus, dépenses, investissements.">
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# Création des onglets
tab1, tab2, tab3 = st.tabs(
    ["🏦 Intérêts Composés", "🔥 Calculateur FIRE", "🧮 Calculateur d'Impôts"]
)

# ============= ONGLET 1: INTÉRÊTS COMPOSÉS =============
with tab1:
    st.header("🏦 Calculateur d'Intérêts Composés")

    # Paramètres principaux
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💶 Capital et versements")
        capital_initial = st.number_input(
            "Capital initial (€)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            key="ic_capital",
        )

        versement_periodique = st.number_input(
            "Versement périodique (€)",
            min_value=0.0,
            value=100.0,
            step=10.0,
            key="ic_versement",
        )

        frequence_versement = st.selectbox(
            "Fréquence des versements",
            ["Mensuel", "Trimestriel", "Semestriel", "Annuel"],
            key="ic_freq_versement",
        )

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

    with col2:

        st.subheader("⚙️ Paramètres de capitalisation")

        frequence_capitalisation = st.selectbox(
            "Fréquence de capitalisation des intérêts",
            ["Mensuelle", "Trimestrielle", "Semestrielle", "Annuelle", "Continue"],
            index=3,  # Annuelle par défaut
            key="ic_freq_capitalisation",
            help="À quelle fréquence les intérêts sont ajoutés au capital pour générer de nouveaux intérêts",
        )

        moment_versement = st.selectbox(
            "Moment du versement",
            ["Début de période", "Fin de période"],
            index=1,  # Fin de période par défaut
            key="ic_moment_versement",
            help="Les versements sont-ils effectués au début ou à la fin de chaque période ?",
        )

        st.subheader("🧾 Fiscalité et TMI")

        calcul_apres_impot = st.checkbox(
            "Calcul après impôt", value=False, key="ic_impot_check"
        )

        if calcul_apres_impot:
            type_placement = st.selectbox(
                "Type de placement",
                ["CTO (Compte-titres ordinaire)", "PEA", "Assurance-vie"],
                key="ic_placement",
            )

            # Nouvelle option TMI personnalisée
            utiliser_tmi_personnalisee = st.checkbox(
                "Utiliser ma TMI personnelle",
                value=False,
                key="ic_tmi_perso_check",
                help="Utilise votre Tranche Marginale d'Imposition pour optimiser le calcul fiscal",
            )

            if utiliser_tmi_personnalisee:
                col_tmi1, col_tmi2 = st.columns(2)

                with col_tmi1:
                    # Option 1: TMI manuelle
                    saisie_tmi = st.radio(
                        "Comment définir votre TMI ?",
                        ["Saisie manuelle", "Calcul automatique"],
                        key="ic_saisie_tmi",
                    )

                    if saisie_tmi == "Saisie manuelle":
                        tmi_utilisateur = st.selectbox(
                            "Votre TMI (%)",
                            [0, 11, 30, 41, 45],
                            index=2,  # 30% par défaut
                            key="ic_tmi_manuelle",
                        )
                    else:
                        # Calcul automatique TMI
                        revenus_annuels = st.number_input(
                            "Revenus annuels (€)",
                            min_value=0.0,
                            value=45000.0,
                            step=1000.0,
                            key="ic_revenus",
                        )

                        situation_familiale = st.selectbox(
                            "Situation familiale",
                            [
                                "Célibataire",
                                "Marié(e)/Pacsé(e)",
                                "Couple + 1 enfant",
                                "Couple + 2 enfants",
                                "Couple + 3 enfants",
                            ],
                            key="ic_situation",
                        )

                        parts_fiscales = {
                            "Célibataire": 1,
                            "Marié(e)/Pacsé(e)": 2,
                            "Couple + 1 enfant": 2.5,
                            "Couple + 2 enfants": 3,
                            "Couple + 3 enfants": 4,
                        }

                        nb_parts = parts_fiscales[situation_familiale]
                        tmi_utilisateur = calculer_tmi_simplifiee(
                            revenus_annuels, nb_parts
                        )

                with col_tmi2:
                    if saisie_tmi == "Calcul automatique":
                        st.metric("Votre TMI calculée", f"{tmi_utilisateur}%")

                    # Information sur l'optimisation
                    st.info(
                        f"""
                    **Optimisation fiscale :**
                    Avec votre TMI de {tmi_utilisateur}%, certains placements peuvent être plus avantageux que le PFU de 30%.
                    """
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
                    taux_imposition = 30
        else:
            taux_imposition = 0.0

        # TODO : A reprendre en main, je veux que ce soit calculé aussi dans les impôts !
        # st.subheader("🧮 Optimisation fiscale avancée")

        # # Checkbox principale
        # optimisation_fiscale = st.checkbox(
        #     "Calcul avec TMI personnelle",
        #     value=False,
        #     key="ic_optimisation_fiscale",
        #     help="Utilise votre TMI réelle pour calculer l'impôt sur les plus-values",
        # )
        # # Affichage conditionnel des paramètres avancés
        # if optimisation_fiscale:
        #     col1, col2, col3 = st.columns([1.2, 1, 1])

        #     # Revenus annuels
        #     with col1:
        #         revenus_annuels_tmi = st.number_input(
        #             "Vos revenus annuels (€)",
        #             min_value=0.0,
        #             value=45000.0,
        #             step=1000.0,
        #             key="ic_revenus_tmi",
        #         )

        #     # Situation familiale
        #     with col2:
        #         situation_familiale_ic = st.selectbox(
        #             "Situation familiale",
        #             [
        #                 "Célibataire",
        #                 "Marié(e)/Pacsé(e)",
        #                 "Couple + 1 enfant",
        #                 "Couple + 2 enfants",
        #                 "Couple + 3 enfants",
        #             ],
        #             key="ic_situation",
        #         )

        #         parts_fiscales_ic = {
        #             "Célibataire": 1,
        #             "Marié(e)/Pacsé(e)": 2,
        #             "Couple + 1 enfant": 2.5,
        #             "Couple + 2 enfants": 3,
        #             "Couple + 3 enfants": 4,
        #         }

        #         nb_parts_ic = parts_fiscales_ic[situation_familiale_ic]

        #     # Calcul TMI + Stratégie
        #     with col3:
        #         tmi_personnelle = calculer_tmi_simplifiee(revenus_annuels_tmi, nb_parts_ic)
        #         st.metric("Votre TMI", f"{tmi_personnelle}%")

        #         optimisation_type = st.selectbox(
        #             "Stratégie d'optimisation",
        #             [
        #                 "Plus-values mobilières",
        #                 "Intérêts (livrets/obligations)",
        #                 "Dividendes",
        #             ],
        #             key="ic_optimisation_type",
        #             help="Type de revenus générés par votre placement",
        #         )

        # Mapping des fréquences
        freq_versement_map = {
            "Mensuel": 12,
            "Trimestriel": 4,
            "Semestriel": 2,
            "Annuel": 1,
        }
        freq_capitalisation_map = {
            "Mensuelle": 12,
            "Trimestrielle": 4,
            "Semestrielle": 2,
            "Annuelle": 1,
            "Continue": float("inf"),
        }

    m = freq_versement_map[frequence_versement]  # Fréquence des versements
    n = freq_capitalisation_map[frequence_capitalisation]  # Fréquence de capitalisation
    r = taux_annuel / 100
    t = duree_annees

    def calculer_interet_compose_avance(P, PMT, r, n, m, t, debut_periode=False):
        """
        Calcul des intérêts composés avec fréquences différentes pour capitalisation et versements

        P : capital initial
        PMT : montant du versement périodique
        r : taux annuel (ex: 0.05 pour 5%)
        n : fréquence de capitalisation (nombre de périodes d'intérêt par an)
        m : fréquence des versements (nombre de versements par an)
        t : durée en années
        debut_periode : True si versements en début de période, False si fin de période
        """

        # Cas spécial : capitalisation continue
        if n == float("inf"):
            # Valeur future du capital initial avec capitalisation continue
            FV_capital = P * np.exp(r * t)

            # Pour les versements avec capitalisation continue
            if PMT > 0 and r > 0:
                # Facteur d'ajustement pour versements en début vs fin de période
                facteur_moment = np.exp(r / m) if debut_periode else 1

                # Somme des versements avec capitalisation continue
                FV_versements = 0
                for k in range(int(m * t)):
                    temps_depuis_versement = t - k / m
                    if debut_periode:
                        temps_depuis_versement -= 1 / m
                    FV_versements += (
                        PMT * facteur_moment * np.exp(r * temps_depuis_versement)
                    )
            elif PMT > 0:
                FV_versements = PMT * m * t
            else:
                FV_versements = 0

            return FV_capital + FV_versements

        # Cas normal : capitalisation discrète
        # Valeur future du capital initial
        FV_capital = P * (1 + r / n) ** (n * t)

        # Valeur future des versements
        if PMT > 0 and r > 0:
            # Facteur d'ajustement pour versements en début vs fin de période
            facteur_moment = (1 + r / n) ** (n / m) if debut_periode else 1

            FV_versements = 0
            total_versements = int(m * t)

            for k in range(total_versements):
                # Temps restant après le k-ième versement (en années)
                temps_restant = t - (k + 1) / m
                if debut_periode:
                    temps_restant += 1 / m

                # Capitalisation du versement jusqu'à la fin
                if temps_restant >= 0:
                    FV_versements += (
                        PMT * facteur_moment * (1 + r / n) ** (n * temps_restant)
                    )
        elif PMT > 0:
            FV_versements = PMT * m * t
        else:
            FV_versements = 0

        return FV_capital + FV_versements

    def calc_van_versements_avance(P, PMT, i, m, t, debut_periode=False):
        """Calcul de la valeur actuelle nette des versements"""
        van = P  # Capital initial à t=0

        facteur_moment = (1 + i) ** (1 / m) if debut_periode else 1

        total_versements = int(m * t)
        for k in range(total_versements):
            temps_versement = (k + 1) / m
            if debut_periode:
                temps_versement -= 1 / m
            van += PMT * facteur_moment / ((1 + i) ** temps_versement)
        return van

    # Calculs avec les nouvelles options
    debut_periode = moment_versement == "Début de période"

    valeur_finale_brute = calculer_interet_compose_avance(
        capital_initial, versement_periodique, r, n, m, t, debut_periode
    )
    total_verse = capital_initial + (versement_periodique * m * t)
    interets_bruts = valeur_finale_brute - total_verse

    van_versements = calc_van_versements_avance(
        capital_initial, versement_periodique, taux_inflation / 100, m, t, debut_periode
    )

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

        rendement_reel_annuel = (
            ((pouvoir_achat_final / van_versements) ** (1 / t) - 1) * 100
            if van_versements > 0
            else 0
        )
    else:
        pouvoir_achat_final = valeur_finale_nette
        perte_pouvoir_achat = 0
        rendement_reel_annuel = (
            ((valeur_finale_nette / van_versements) ** (1 / t) - 1) * 100
            if van_versements > 0
            else 0
        )

    st.markdown("---")

    # Affichage des paramètres de capitalisation
    col1, col2 = st.columns(2)
    with col1:
        if frequence_capitalisation == "Continue":
            st.info(f"🔄 **Capitalisation continue** - Intérêts calculés en permanence")
        else:
            st.info(
                f"🔄 **Capitalisation {frequence_capitalisation.lower()}** - Intérêts calculés {freq_capitalisation_map[frequence_capitalisation]} fois par an"
            )

    with col2:
        st.info(
            f"📅 **Versements {frequence_versement.lower()}s** en **{moment_versement.lower()}**"
        )

    frequences_affichage = {
        "Mensuel": "par mois",
        "Trimestriel": "par trimestre",
        "Semestriel": "par semestre",
        "Annuel": "par an",
    }
    # Formattage dynamique
    affichage_frequence = frequences_affichage.get(
        frequence_versement, frequence_versement.lower()
    )

    if capital_initial:
        st.info(
            f"📝 Pour un investissement initial de {capital_initial} € avec un versement de {versement_periodique} € {affichage_frequence} sur {duree_annees} ans avec un rendement de {taux_annuel} % par an."
        )
    else:
        # Résultats
        st.info(
            f"📝 Pour un investissement de {versement_periodique:.1f} € {affichage_frequence} sur {duree_annees} ans avec un rendement de {taux_annuel} % par an."
        )
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
                # (
                #     f"-{(perte_pouvoir_achat/valeur_finale_nette)*100:.1f}%"
                #     if valeur_finale_nette > 0
                #     else "0%"
                # ),
            )
            # st.metric(
            #     "📉 Rendement réel annualisé",
            #     f"{rendement_reel_annuel:.2f} %",
            # )
        elif calcul_apres_impot and impots_sur_interets > 0:
            st.metric(
                "💸 Impôts payés",
                f"{impots_sur_interets:,.2f} €",
                f"{taux_imposition:.1f}%",
            )

    # Comparaison des fréquences de capitalisation
    if st.checkbox("📊 Comparer les fréquences de capitalisation", key="compare_freq"):
        st.subheader("Impact de la fréquence de capitalisation")

        freq_comparison = {
            "Annuelle": 1,
            "Semestrielle": 2,
            "Trimestrielle": 4,
            "Mensuelle": 12,
            "Continue": float("inf"),
        }

        comparison_results = []
        for freq_name, freq_value in freq_comparison.items():
            valeur_comp = calculer_interet_compose_avance(
                capital_initial,
                versement_periodique,
                r,
                freq_value,
                m,
                t,
                debut_periode,
            )
            interets_comp = valeur_comp - total_verse
            comparison_results.append(
                {
                    "Fréquence": freq_name,
                    "Valeur finale": valeur_comp,
                    "Intérêts": interets_comp,
                    "Gain vs Annuelle": (
                        interets_comp - comparison_results[0]["Intérêts"]
                        if comparison_results
                        else 0
                    ),
                }
            )

        df_comparison = pd.DataFrame(comparison_results)

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(
                df_comparison.style.format(
                    {
                        "Valeur finale": "{:,.2f} €",
                        "Intérêts": "{:,.2f} €",
                        "Gain vs Annuelle": "{:+,.2f} €",
                    }
                ),
                hide_index=True,
            )

        with col2:
            fig_comp = px.bar(
                df_comparison,
                x="Fréquence",
                y="Intérêts",
                title="Intérêts selon la fréquence de capitalisation",
            )
            st.plotly_chart(fig_comp, use_container_width=True)

    # Informations détaillées selon les options
    if calcul_apres_impot or ajuster_inflation:
        st.subheader("📊 Détail des calculs")
        col1, col2 = st.columns(2)

        with col1:
            if calcul_apres_impot:

                annees_abattement = math.ceil(interets_bruts / 4600)
                st.info(
                    f"""
                **Fiscalité {type_placement} :**
                - Intérêts bruts : {interets_bruts:,.2f} €
                - Taux d'imposition : {taux_imposition:.1f}%
                {"- Abattement appliqué : 4 600 €" if type_placement == "Assurance-vie" and duree_annees >= 8 else ""}
                - Impôts : {impots_sur_interets:,.2f} €
                - **Intérêts nets : {interets_nets:,.2f} €**

                Pour optimiser votre imposition, vous devriez retirer 4600€/an sur {annees_abattement} ans.
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
                - **Rendement réel annualisé : {rendement_reel_annuel:.2f}%**
                - **Rendement réel sur la période : {((pouvoir_achat_final/van_versements)*100-100):.1f}%**
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
        valeur_brute = calculer_interet_compose_avance(
            capital_initial, versement_periodique, r, n, m, annee, debut_periode
        )
        valeurs_brutes.append(valeur_brute)

        # Versements cumulés
        verse_cumule = capital_initial + (versement_periodique * m * annee)
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
                taux_annee = 30
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
        title=f"Évolution du capital (Capitalisation {frequence_capitalisation.lower()}, Versements {moment_versement.lower()})",
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

# ============= ONGLET 3: CALCULATEUR TMI =============
with tab3:
    st.header("🧮 Calculateur d'Impôts et TMI")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Revenus")
        revenus_imposables = st.number_input(
            "Revenus imposables annuels (€)",
            min_value=0.0,
            value=45000.0,
            step=1000.0,
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

        st.info(f"📊 Nombre de parts fiscales : {nb_parts}")

    # Barème 2024 (revenus 2023)
    if annee_fiscale == 2024:
        tranches = [
            (0, 10777, 0),
            (10777, 27478, 11),
            (27478, 78570, 30),
            (78570, 168994, 41),
            (168994, float("inf"), 45),
        ]
    else:  # 2023
        tranches = [
            (0, 10225, 0),
            (10225, 26070, 11),
            (26070, 74545, 30),
            (74545, 160336, 41),
            (160336, float("inf"), 45),
        ]

    # Calcul du quotient familial
    quotient_familial = revenus_imposables / nb_parts

    # Calcul de l'impôt par part
    impot_par_part = 0
    tmi = 0

    for i, (seuil_inf, seuil_sup, taux) in enumerate(tranches):
        if quotient_familial > seuil_inf:
            base_imposable = min(quotient_familial, seuil_sup) - seuil_inf
            impot_par_part += base_imposable * (taux / 100)
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
    taux_moyen = (impot_net / revenus_imposables * 100) if revenus_imposables > 0 else 0

    # Revenus nets après IR
    revenus_nets_ir = revenus_imposables - impot_net

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
        st.metric("💼 Revenus bruts", f"{revenus_imposables:,.0f} €")

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

    # Graphique répartition
    col1, col2 = st.columns(2)

    with col1:
        # Graphique camembert
        if cotisations > 0:
            values = [revenus_nets_total, impot_net, cotisations]
            labels = ["Revenus nets", "Impôt sur le revenu", "Cotisations sociales"]
            colors = ["#2ca02c", "#d62728", "#ff7f0e"]
        else:
            values = [revenus_nets_ir, impot_net]
            labels = ["Revenus nets", "Impôt sur le revenu"]
            colors = ["#2ca02c", "#d62728"]

        fig_pie = px.pie(
            values=values,
            names=labels,
            title="Répartition des revenus",
            color_discrete_sequence=colors,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Simulation d'augmentation
        st.subheader("🔮 Impact d'une augmentation")
        augmentation = st.slider(
            "Augmentation de salaire (€)",
            min_value=0,
            max_value=10000,
            value=1000,
            step=100,
            key="tmi_augmentation",
        )

        if augmentation > 0:
            nouveaux_revenus = revenus_imposables + augmentation
            nouveau_quotient = nouveaux_revenus / nb_parts

            # Recalcul rapide
            nouvel_impot_par_part = 0
            nouvelle_tmi = 0

            for seuil_inf, seuil_sup, taux in tranches:
                if nouveau_quotient > seuil_inf:
                    base_imposable = min(nouveau_quotient, seuil_sup) - seuil_inf
                    nouvel_impot_par_part += base_imposable * (taux / 100)
                    if nouveau_quotient > seuil_inf:
                        nouvelle_tmi = taux

            nouvel_impot_brut = nouvel_impot_par_part * nb_parts

            # Nouvelle décote
            nouvelle_decote = 0
            if nouvel_impot_brut < seuil_decote:
                nouvelle_decote = min(
                    nouvel_impot_brut, (seuil_decote - nouvel_impot_brut) * 0.45
                )

            nouvel_impot_net = max(0, nouvel_impot_brut - nouvelle_decote)

            augmentation_impot = nouvel_impot_net - impot_net
            augmentation_nette = augmentation - augmentation_impot

            if cotisations > 0:
                nouvelles_cotisations = nouveaux_revenus * cotisations_rate
                augmentation_cotisations = nouvelles_cotisations - cotisations
                augmentation_nette -= augmentation_cotisations
                taux_prelevement = (
                    (augmentation_impot + augmentation_cotisations) / augmentation * 100
                )
            else:
                taux_prelevement = augmentation_impot / augmentation * 100

            st.info(
                f"""
            **Pour +{augmentation:,.0f} € bruts :**
            - Nouvel impôt : +{augmentation_impot:,.0f} €
            {"- Nouvelles cotisations : +" + f"{augmentation_cotisations:,.0f}" + " €" if cotisations > 0 else ""}
            - **Gain net : +{augmentation_nette:,.0f} €**
            - **Taux de prélèvement : {taux_prelevement:.1f}%**
            """
            )

    # Conseils d'optimisation
    st.subheader("💡 Conseils d'optimisation fiscale")

    conseils = []

    if tmi >= 30:
        conseils.append(
            "🏦 **PEA** : Optimisez vos investissements avec un PEA (exonéré après 5 ans)"
        )
        conseils.append(
            "🏠 **Assurance-vie** : Profitez de l'abattement de 4 600€/an après 8 ans"
        )

    if tmi >= 41:
        conseils.append("📊 **PER** : Déduction fiscale jusqu'à 10% de vos revenus")
        conseils.append("🏡 **Investissement locatif** : Déficit foncier déductible")

    if revenus_imposables > 50000:
        conseils.append("🎯 **Don aux associations** : 66% de réduction d'impôt")
        conseils.append(
            "💼 **FCPI/FIP** : Réduction d'impôt de 18% (placements risqués)"
        )

    if situation_familiale == "Célibataire":
        conseils.append(
            "💑 **PACS** : Peut être avantageux fiscalement selon les revenus du conjoint"
        )

    for conseil in conseils:
        st.info(conseil)

st.markdown("---")
st.markdown(
    "💡 **Conseil** : Ces calculateurs sont à titre indicatif. Les rendements passés ne garantissent pas les performances futures."
)
st.markdown(
    "❤️ Ce site a été créé avec amour par [Maxime in tech](https://github.com/MaximeIn-Tech) !"
)
