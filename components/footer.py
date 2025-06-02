import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space


def render_footer():
    add_vertical_space(3)
    st.markdown("---")

    # Avertissement légal
    st.info(
        "🚫 Ceci n'est pas un conseil en investissement. Les informations présentées sont fournies à titre indicatif uniquement."
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
