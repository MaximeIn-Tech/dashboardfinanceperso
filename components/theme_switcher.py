import streamlit as st


def theme_switcher():
    # Définition des thèmes
    themes = {
        "Light": {
            "colors": {
                "background": "#ffffff",
                "text": "#000000",
                "primary": "#1f77b4",
            },
            "emoji": "🌞",
        },
        "Dark": {
            "colors": {
                "background": "#0e1117",
                "text": "#fafafa",
                "primary": "#ff9800",
            },
            "emoji": "🌙",
        },
    }

    # Choix du thème par l'utilisateur
    selected_theme = st.radio(
        label="Choisissez un thème",
        options=["Light", "Dark"],
        horizontal=True,
        label_visibility="collapsed",
        key="theme_switch",
    )

    current = themes[selected_theme]

    # CSS dynamique selon le thème sélectionné
    injected_css = f"""
    <style>
        html, body, [class*="stApp"] {{
            background-color: {current['colors']['background']} !important;
            color: {current['colors']['text']} !important;
        }}

        .custom-theme-toggle {{
            position: fixed;
            top: 0.5rem;
            right: 1.5rem;
            z-index: 9999;
            background-color: transparent;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
        }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
    </style>

    <div class="custom-theme-toggle">
        {current["emoji"]}
    </div>
    """

    st.markdown(injected_css, unsafe_allow_html=True)

    return current
