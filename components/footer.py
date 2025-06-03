import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space


def render_footer():
    add_vertical_space(3)
    st.markdown("---")

    theme_base = st.get_option("theme.base")
    st.write("Thème actuel :", theme_base)

    if theme_base == "dark":
        bg_color = "#263238"
        border_color = "#81d4fa"
        text_color = "#81d4fa"
    else:
        bg_color = "#e3f2fd"
        border_color = "#2196f3"
        text_color = "#1976d2"

    st.markdown(
        f"""
    <div style="
        background: {bg_color};
        border-radius: 10px;
        padding: 20px;
        margin: 30px 0;
        text-align: center;
        border: 1px solid {border_color};
        color: {text_color};
        font-style: italic;
    ">
        <h5 style="margin-bottom: 10px;">📋 Note importante</h5>
        Ces conseils sont donnés à titre indicatif.<br>Consultez un conseiller fiscal pour une stratégie personnalisée.
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Footer HTML avec logos
    st.markdown(
        """
        <style>
        .footer-container {
            text-align: center;
            color: gray;
            font-size: 13px;
            margin-top: 20px;
        }
        .footer-container img {
            margin: 0 10px;
            width: 26px;
            vertical-align: middle;
            transition: transform 0.2s ease;
        }
        .footer-container img:hover {
            transform: scale(1.2);
        }
        </style>

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
