import streamlit as st
from streamlit_theme import st_theme


def format_nombre(n):
    return f"{n:,.0f}".replace(",", " ")


# Chargement CSS
def load_css():
    with open("assets/styles.css") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def info_card(title: str, content: str, type: str = "info"):
    colors = {
        "info": {"border": "#1f77b4", "bg": "#f0f8ff", "icon": "ℹ️"},
        "warning": {"border": "#ffae42", "bg": "#fff8e1", "icon": "⚠️"},
        "success": {"border": "#2ca02c", "bg": "#e6f4ea", "icon": "✅"},
        "danger": {"border": "#d62728", "bg": "#fdecea", "icon": "❌"},
        "neutral": {"border": "#888", "bg": "#f7f7f7", "icon": "📌"},
    }

    style = colors.get(type, colors["info"])

    st.markdown(
        f"""
    <div style="
        border-left: 6px solid {style['border']};
        background-color: {style['bg']};
        padding: 1em;
        border-radius: 0.5em;
        margin-bottom: 1em;
    ">
        <strong>{style['icon']} {title}</strong><br>
        <span style="font-size: 0.95em; line-height: 1.5;">
            {content}
        </span>
    </div>
    """,
        unsafe_allow_html=True,
    )


# TODO : Refactor le code pour qu'il fonctionne avec les st.info etc et en fonction du thème.

# def custom_alert(message: str, alert_type: str = "info"):
#     """
#     Affiche une alerte stylée custom dans Streamlit (sans icône, bord arrondi, couleurs pastel).

#     Args:
#         message (str): Le texte de l'alerte, peut contenir du HTML basique.
#         alert_type (str): Type d'alerte : info, success, warning, error.
#     """

#     alert_type = alert_type.lower()
#     if alert_type not in {"info", "success", "warning", "error"}:
#         alert_type = "info"

#     html = f"""
#     <div class="custom-alert {alert_type}">
#         <div>{message}</div>
#     </div>
#     """
#     st.markdown(html, unsafe_allow_html=True)
