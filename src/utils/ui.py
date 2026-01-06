import streamlit as st


def linguistic_chip(label: str, color: str) -> str:
    return f"""
    <span style="
        padding:4px 10px;
        border-radius:10px;
        background-color:{color};
        color:white;
        font-weight:600;
        font-size:0.85rem;
        display:inline-block;
    ">
        {label}
    </span>
    """


def variable_row(
    *,
    label: str,
    linguistic_value: str,
    linguistic_color: str,
    numeric_label: str,
    numeric_value: str,
) -> None:
    """
    Uniwersalny wiersz prezentujący zmienną systemu eksperckiego.
    """

    with st.container(border=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"**{label}**")
            chip_html = linguistic_chip(linguistic_value, linguistic_color)
            st.markdown(chip_html, unsafe_allow_html=True)

        with col2:
            st.metric(label=numeric_label, value=numeric_value)
