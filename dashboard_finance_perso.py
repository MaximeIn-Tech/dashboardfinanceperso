import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.footer import render_footer


def format_nombre(n):
    return f"{n:,.0f}".replace(",", " ")


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
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏦 Intérêts Composés",
        "🔥 Calculateur FI/RE",
        "🧮 Calculateur d'Impôts",
        "🏠 Acheter VS Louer",
    ]
)

# ============= ONGLET 1: INTÉRÊTS COMPOSÉS =============
with tab1:
    st.header("🏦 Calculateur d'Intérêts Composés")

    # Paramètres principaux
    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            st.markdown("## 💶 Capital et versements")
            st.caption("🔧 Paramétrez votre simulation d’investissement ci-dessous.")

            with st.expander("🧾 Capital de départ", expanded=True):
                capital_initial = st.number_input(
                    "Capital initial (€)",
                    min_value=0.0,
                    value=0.0,
                    step=100.0,
                    key="ic_capital",
                    format="%.0f",
                    help="Montant dont vous disposez au départ.",
                )

            with st.expander("🔁 Versements réguliers", expanded=True):
                versement_periodique = st.number_input(
                    "Versement périodique (€)",
                    min_value=0.0,
                    value=100.0,
                    step=10.0,
                    key="ic_versement",
                    format="%.0f",
                    help="Montant que vous ajoutez à chaque période.",
                )

                frequence_versement = st.selectbox(
                    "Fréquence des versements",
                    ["Mensuel", "Trimestriel", "Semestriel", "Annuel"],
                    key="ic_freq_versement",
                    help="À quelle fréquence vous versez ce montant.",
                )

            with st.expander("📈 Paramètres de croissance", expanded=True):
                taux_annuel = st.number_input(
                    "Taux d'intérêt annuel (%)",
                    min_value=0.0,
                    max_value=50.0,
                    value=5.0,
                    step=0.1,
                    key="ic_taux",
                    format="%.1f",
                    help="Taux de rendement estimé chaque année (hors inflation).",
                )

                duree_annees = st.number_input(
                    "Durée de placement (années)",
                    min_value=1,
                    max_value=50,
                    value=10,
                    step=1,
                    key="ic_duree",
                    help="Nombre total d'années pendant lesquelles vous investissez.",
                )

    with col2:
        st.markdown("## ⚙️ Paramètres de capitalisation")
        st.caption("⚡ Ajustez la mécanique d'accumulation des intérêts.")

        with st.expander("📊 Capitalisation", expanded=True):
            frequence_capitalisation = st.selectbox(
                "Fréquence de capitalisation des intérêts",
                ["Mensuelle", "Trimestrielle", "Semestrielle", "Annuelle", "Continue"],
                index=3,  # Annuelle par défaut
                key="ic_freq_capitalisation",
                help="Fréquence à laquelle les intérêts sont réintégrés pour générer des intérêts composés.",
            )

        with st.expander("📅 Moment des versements", expanded=True):
            moment_versement = st.selectbox(
                "Moment du versement",
                ["Début de période", "Fin de période"],
                index=1,  # Fin de période par défaut
                key="ic_moment_versement",
                help="Moment auquel les versements périodiques sont effectués dans chaque cycle.",
            )

    # Options avancées
    st.subheader("Options avancées")
    col1, col2, col3 = st.columns(3)

    # Fonction helper pour calculer la TMI
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


# ============= ONGLET 2: CALCULATEUR FIRE =============
with tab2:
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
        st.metric("💼 Revenus bruts", f"{format_nombre(revenus_imposables)} €")

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

# ============= ONGLET 4: ACHETER VS LOUER =============

with tab4:

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
st.title("🏠 Simulateur Acheter vs Louer")

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
        paiement_annuel_credit = mensualite_credit * 12 if annee <= duree_credit else 0
        interets_annuels = (
            soldes_pret[annee - 1] * taux_emprunt if annee <= duree_credit else 0
        )
        capital_rembourse = (
            paiement_annuel_credit - interets_annuels if annee <= duree_credit else 0
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
            value="Acheteur > Locataire" if diff_pct > 0 else "Locataire > Acheteur",
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

    # Traces principales
    fig.add_trace(
        go.Scatter(
            x=df["Année"],
            y=df["Portefeuille Locataire (€)"],
            mode="lines",
            name="💼 Portefeuille Locataire",
            line=dict(color="blue", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Année"],
            y=df["Valeur Nette Acheteur (€)"],
            mode="lines",
            name="🏡 Valeur Nette Acheteur",
            line=dict(color="green", width=3),
        )
    )

    # Shade : locataire gagnant
    fig.add_trace(
        go.Scatter(
            x=df["Année"].tolist() + df["Année"][::-1].tolist(),
            y=(
                np.maximum(
                    df["Portefeuille Locataire (€)"], df["Valeur Nette Acheteur (€)"]
                )
            ).tolist()
            + (
                np.minimum(
                    df["Portefeuille Locataire (€)"], df["Valeur Nette Acheteur (€)"]
                )[::-1]
            ).tolist(),
            fill="toself",
            fillcolor="rgba(0,0,255,0.1)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="Zone gagnée par le locataire",
        )
    )

    # Shade : acheteur gagnant (inversé)
    fig.add_trace(
        go.Scatter(
            x=df["Année"].tolist() + df["Année"][::-1].tolist(),
            y=(
                np.minimum(
                    df["Portefeuille Locataire (€)"], df["Valeur Nette Acheteur (€)"]
                )
            ).tolist()
            + (
                np.maximum(
                    df["Portefeuille Locataire (€)"], df["Valeur Nette Acheteur (€)"]
                )[::-1]
            ).tolist(),
            fill="toself",
            fillcolor="rgba(0,128,0,0.1)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="Zone gagnée par l'acheteur",
        )
    )

    # Ligne verticale du croisement
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
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Tableau comparatif", expanded=False):
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.info(
        """
    **💡 Interprétation :**
    - Le portefeuille locataire inclut l'apport investi et les économies réalisées chaque année.
    - La valeur nette acheteur tient compte de la revente du bien (avec frais) et du capital remboursé.
    - La ligne rouge verticale indique l'année où louer devient plus rentable qu'acheter (si applicable).
    """
    )


render_footer()
