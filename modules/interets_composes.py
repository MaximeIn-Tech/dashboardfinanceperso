import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def interets_composes_render():
    st.header("🏦 Calculateur d'Intérêts Composés")
    st.write(
        "Simulez la croissance de votre capital avec versements périodiques et intérêts composés."
    )

    # === Mise en page 3 colonnes ===

    col1, col2, col3 = st.columns(3)

    # === Section 1: Capital & Versements ===
    with col1:
        st.subheader(
            "💶 Capital & Versements",
            help="Définissez votre point de départ et vos apports réguliers.",
        )

        capital_initial = st.number_input(
            "Capital initial (€)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            key="ic_capital",
            format="%.0f",
            help="Montant dont vous disposez au départ, sans encore générer d’intérêts.",
        )

        col_v1, col_v2 = st.columns([2, 1])
        with col_v1:
            versement_periodique = st.number_input(
                "Montant du versement périodique (€)",
                min_value=0.0,
                value=100.0,
                step=10.0,
                key="ic_versement",
                format="%.0f",
                help="Somme ajoutée régulièrement pour faire grossir votre capital.",
            )
        with col_v2:
            frequence_versement = st.selectbox(
                "Fréquence",
                ["Mensuel", "Trimestriel", "Semestriel", "Annuel"],
                key="ic_freq_versement",
                help="À quelle fréquence vous ajoutez ces versements à votre capital.",
            )

    # === Section 2: Croissance & Durée ===
    with col2:
        st.subheader(
            "📈 Croissance & Durée",
            help="Paramétrez le rendement attendu et la durée de votre investissement.",
        )

        taux_annuel = st.number_input(
            "Taux d'intérêt annuel (%)",
            min_value=0.0,
            max_value=50.0,
            value=5.0,
            step=0.1,
            key="ic_taux",
            format="%.1f",
            help="Taux de rendement attendu par an, hors inflation.",
        )

        duree_annees = st.number_input(
            "Durée du placement (années)",
            min_value=1,
            max_value=50,
            value=10,
            step=1,
            key="ic_duree",
            help="Nombre d'années pendant lesquelles vous laissez votre capital fructifier.",
        )

    # === Section 3: Capitalisation des intérêts ===
    with col3:
        st.subheader(
            "⚙️ Capitalisation des intérêts",
            help="Définissez la fréquence à laquelle vos intérêts sont ajoutés au capital, pour bénéficier de l’effet composé.",
        )

        frequence_capitalisation = st.selectbox(
            "Fréquence de capitalisation",
            ["Mensuelle", "Trimestrielle", "Semestrielle", "Annuelle", "Continue"],
            index=3,  # Annuelle par défaut
            key="ic_freq_capitalisation",
            help="À quelle fréquence les intérêts générés sont réinvestis dans le capital.",
        )

        moment_versement = st.selectbox(
            "Moment du versement périodique",
            ["Début de période", "Fin de période"],
            index=1,  # Fin de période par défaut
            key="ic_moment_versement",
            help="Quand vos versements réguliers sont ajoutés : avant ou après calcul des intérêts de la période.",
        )

    # Options avancées
    st.subheader("Options avancées")
    col1, col2, col3 = st.columns(3)

    # Fonction helper pour calculer la TMI
    def calculer_tmi_simplifiee(revenus_annuels, nb_parts=1, annee=2024):
        """Calcul simplifié de la TMI"""
        if annee == 2024:
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

        quotient_familial = revenus_annuels / nb_parts
        tmi = 0

        for seuil_inf, seuil_sup, taux in tranches:
            if quotient_familial > seuil_inf:
                tmi = taux

        return tmi

    def calculer_taux_imposition_effectif(
        type_placement,
        duree_annees,
        type_revenus,
        tmi_personnelle=None,
        utiliser_tmi=False,
    ):
        """Calcule le taux d'imposition effectif selon le type de placement et la durée"""

        if not utiliser_tmi or tmi_personnelle is None:
            # Utilisation des taux standard (PFU)
            if type_placement == "CTO (Compte-titres ordinaire)":
                return 30.0  # PFU : 17,2% IR + 12,8% PS
            elif type_placement == "PEA":
                if duree_annees >= 5:
                    return 12.8  # Seulement prélèvements sociaux
                else:
                    return 30.0  # PFU complet si retrait avant 5 ans
            else:  # Assurance-vie
                if duree_annees >= 8:
                    return 7.5 + 12.8  # 7,5% IR + 12,8% PS (après abattement)
                else:
                    return 30.0
        else:
            # Utilisation de la TMI personnelle
            if type_placement == "CTO (Compte-titres ordinaire)":
                if type_revenus == "Plus-values mobilières":
                    return 12.8  # Seulement prélèvements sociaux pour les PV
                elif type_revenus == "Dividendes":
                    # Option entre PFU (30%) ou barème progressif (TMI + 12,8%)
                    taux_bareme = tmi_personnelle + 12.8
                    return min(30.0, taux_bareme)  # Le plus avantageux
                else:  # Intérêts
                    taux_bareme = tmi_personnelle + 12.8
                    return min(30.0, taux_bareme)
            elif type_placement == "PEA":
                if duree_annees >= 5:
                    return 12.8  # Seulement prélèvements sociaux
                else:
                    # Avant 5 ans, utilisation du barème ou PFU
                    taux_bareme = tmi_personnelle + 12.8
                    return min(30.0, taux_bareme)
            else:  # Assurance-vie
                if duree_annees >= 8:
                    if type_revenus == "Plus-values mobilières":
                        return 7.5 + 12.8  # Taux spécifique AV
                    else:
                        taux_bareme = min(tmi_personnelle, 7.5) + 12.8
                        return taux_bareme
                else:
                    taux_bareme = tmi_personnelle + 12.8
                    return min(30.0, taux_bareme)

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
            # Checkbox pour l'optimisation fiscale avancée
            optimisation_fiscale = st.checkbox(
                "Utiliser ma TMI personnelle",
                value=False,
                key="ic_optimisation_fiscale",
                help="Utilise votre TMI réelle pour optimiser le calcul d'impôt",
            )

    # Section TMI personnalisée (affichage conditionnel)
    if calcul_apres_impot and optimisation_fiscale:
        st.subheader("🧮 Optimisation fiscale personnalisée")

        col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])

        # Revenus annuels
        with col1:
            revenus_annuels_tmi = st.number_input(
                "Vos revenus annuels (€)",
                min_value=0.0,
                value=45000.0,
                step=1000.0,
                key="ic_revenus_tmi",
                help="Revenus imposables avant déductions",
            )

        # Situation familiale
        with col2:
            situation_familiale_ic = st.selectbox(
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

            parts_fiscales_ic = {
                "Célibataire": 1,
                "Marié(e)/Pacsé(e)": 2,
                "Couple + 1 enfant": 2.5,
                "Couple + 2 enfants": 3,
                "Couple + 3 enfants": 4,
            }

            nb_parts_ic = parts_fiscales_ic[situation_familiale_ic]

        # Type de revenus générés
        with col3:
            optimisation_type = st.selectbox(
                "Type de revenus générés",
                [
                    "Plus-values mobilières",
                    "Intérêts (livrets/obligations)",
                    "Dividendes",
                ],
                key="ic_optimisation_type",
                help="Type de revenus générés par votre placement",
            )

        # Calcul et affichage TMI
        with col4:
            tmi_personnelle = calculer_tmi_simplifiee(revenus_annuels_tmi, nb_parts_ic)
            st.metric("Votre TMI", f"{tmi_personnelle}%")

            # Calcul du taux effectif avec TMI
            taux_effectif_tmi = calculer_taux_imposition_effectif(
                type_placement, duree_annees, optimisation_type, tmi_personnelle, True
            )
            st.metric("Taux effectif", f"{taux_effectif_tmi:.1f}%")

    # Calcul du taux d'imposition à utiliser
    if calcul_apres_impot:
        if optimisation_fiscale:
            taux_imposition = calculer_taux_imposition_effectif(
                type_placement, duree_annees, optimisation_type, tmi_personnelle, True
            )
            type_revenus_utilise = optimisation_type
        else:
            taux_imposition = calculer_taux_imposition_effectif(
                type_placement, duree_annees, "Standard", None, False
            )
            type_revenus_utilise = "Standard"

        # Affichage des informations sur le type de placement
        if not optimisation_fiscale:
            if type_placement == "CTO (Compte-titres ordinaire)":
                st.info("📋 **CTO** : PFU de 30% (17,2% IR + 12,8% PS)")
            elif type_placement == "PEA":
                if duree_annees >= 5:
                    st.info("📋 **PEA** : Exonéré après 5 ans + 12,8% PS")
                else:
                    st.info("📋 **PEA** : PFU de 30% si retrait avant 5 ans")
            else:  # Assurance-vie
                if duree_annees >= 8:
                    st.info(
                        "📋 **AV** : 7,5% + 12,8% PS après 8 ans (avec abattement 4 600€)"
                    )
                else:
                    st.info("📋 **AV** : PFU de 30% avant 8 ans")
    else:
        taux_imposition = 0.0
        type_revenus_utilise = "Aucun"

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
        abattement_applique = 0
        if type_placement == "Assurance-vie" and duree_annees >= 8:
            # Abattement de 4 600€ pour une personne seule
            abattement_applique = 4600
            interets_imposables = max(0, interets_bruts - abattement_applique)
        else:
            interets_imposables = interets_bruts

        impots_sur_interets = interets_imposables * (taux_imposition / 100)
        valeur_finale_nette = total_verse + (interets_bruts - impots_sur_interets)
        interets_nets = interets_bruts - impots_sur_interets
    else:
        valeur_finale_nette = valeur_finale_brute
        interets_nets = interets_bruts
        impots_sur_interets = 0
        abattement_applique = 0
        interets_imposables = interets_bruts

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
            )
        elif calcul_apres_impot and impots_sur_interets > 0:
            st.metric(
                "💸 Impôts payés",
                f"{impots_sur_interets:,.2f} €",
                f"{taux_imposition:.1f}%",
            )

    # Comparaison PFU vs TMI si optimisation activée
    if calcul_apres_impot and optimisation_fiscale:
        st.subheader("⚖️ Comparaison PFU vs Barème progressif (TMI)")

        # Calcul avec PFU standard
        taux_pfu = calculer_taux_imposition_effectif(
            type_placement, duree_annees, "Standard", None, False
        )

        if type_placement == "Assurance-vie" and duree_annees >= 8:
            interets_imposables_pfu = max(0, interets_bruts - 4600)
        else:
            interets_imposables_pfu = interets_bruts

        impots_pfu = interets_imposables_pfu * (taux_pfu / 100)
        valeur_finale_pfu = total_verse + (interets_bruts - impots_pfu)

        # Comparaison
        gain_optimisation = valeur_finale_nette - valeur_finale_pfu

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "💰 PFU Standard",
                f"{valeur_finale_pfu:,.2f} €",
                # f"Impôt: {impots_pfu:,.2f} € ({taux_pfu:.1f}%)",
            )
        with col2:
            st.metric(
                "🎯 Avec votre TMI",
                f"{valeur_finale_nette:,.2f} €",
                # f"Impôt: {impots_sur_interets:,.2f} € ({taux_imposition:.1f}%)",
            )
        with col3:
            couleur_gain = "normal" if gain_optimisation >= 0 else "inverse"
            st.metric(
                "📊 Gain d'optimisation",
                f"{gain_optimisation:+,.2f} €",
                # f"{(gain_optimisation/valeur_finale_pfu)*100:+.2f}%",
                delta_color=couleur_gain,
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
                # Calcul optimisé pour l'abattement annuel
                if abattement_applique > 0:
                    annees_abattement = math.ceil(interets_bruts / abattement_applique)
                    conseil_abattement = f"Pour optimiser votre imposition, vous devriez retirer {abattement_applique:,.0f}€/an sur {annees_abattement} ans."
                else:
                    conseil_abattement = ""

                # Information sur le type de revenus si TMI utilisée
                info_revenus = ""
                if optimisation_fiscale:
                    info_revenus = f"- Type de revenus : {type_revenus_utilise}\n"
                    if "tmi_personnelle" in locals():
                        info_revenus += f"- Votre TMI : {tmi_personnelle}%\n"

                st.info(
                    f"""### 💼 Fiscalité {type_placement}

{info_revenus}
• **Intérêts bruts** : {interets_bruts:,.2f} €

{"• **Abattement appliqué** : {:,.0f} €\n".format(abattement_applique) if abattement_applique > 0 else ""}\
• **Intérêts imposables** : {interets_imposables:,.2f} €
• **Taux d'imposition** : {taux_imposition:.1f} %
• **Impôts à payer** : {impots_sur_interets:,.2f} €
• ✅ **Intérêts nets après impôts** : {interets_nets:,.2f} €

{conseil_abattement}
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
