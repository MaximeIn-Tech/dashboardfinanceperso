import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space

# Charge le fichier CSS au lancement
with open("assets/styles.css") as f:
    css = f.read()

# Injecte le CSS dans la page Streamlit (une seule fois, en haut de ton app ou dans une fonction d'init)
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_footer():
    add_vertical_space(3)
    st.markdown("---")

    # Note finale avec style adaptatif
    st.markdown(
        """
        <div class="note-finale">
            <h5 class="note-titre">
                📋 Note importante
            </h5>
            <p class="note-texte">
                Ces conseils sont donnés à titre indicatif.
                Consultez un conseiller fiscal pour une stratégie personnalisée.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Footer HTML avec logos
    st.markdown(
        """
        <div class="footer-container">
            <p>❤️ Ce site a été créé avec amour par <strong>Maxime</strong></p>
            <a href="https://github.com/MaximeIn-Tech" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/733/733553.png" alt="GitHub">
            </a>
            <a href="https://www.linkedin.com/in/maximehamou" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn">
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
