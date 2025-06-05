import streamlit as st


def format_nombre(n):
    return f"{n:,.0f}".replace(",", " ")


# Chargement CSS
def load_css():
    with open("assets/styles.css") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
