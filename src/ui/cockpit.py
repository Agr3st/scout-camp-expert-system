import streamlit as st

from src.orchestrators.camp_orchestrator import (
    create_camp_ui_dicts,
)
from src.utils.config import load_config
from src.utils.ui import variable_row

# load configuration
config = load_config("config.yaml")
linguistic_colors = config["linguistic_colors"]

st.title("🏠 Kokpit")
st.caption("Moduł 2. poziomu.")

camp_inputs, output_risk = create_camp_ui_dicts()

if st.session_state.camp_risk:
    st.markdown("### Ryzyko obozowe")
    st.caption(
        "Rozmyta miara bezpieczeństwa funkcjonowania obozu, "
        "wyznaczana na podstawie analizy czynników pogodowych, organizacyjnych i terenowych (poniższe zmienne wejściowe)."
    )
    variable_row(
        label="Poziom ryzyka obozowego",
        linguistic_value=output_risk["linguistic"],
        linguistic_color=linguistic_colors["ryzyko_obozowe"][output_risk["linguistic"]],
        numeric_label="Wartość liczbowa (0–100)",
        numeric_value=str(int(output_risk["value"])),
    )
else:
    st.info(
        "Nie można obliczyć ryzyka obozowego (zmiennej 2-poziomu), "
        "ponieważ wymagane są wszystkie zmienne wejściowe: "
        "zagrożenie pogodowe, ryzyko organizacyjne, ryzyko terenowe."
    )


if camp_inputs:
    st.markdown("### Zmienne wejściowe")
    st.caption(
        "Zmienne wyjściowe 1. poziomu, "
        "będące wejściem do obliczenia ryzyka obozowego."
    )

    for var_name, var in camp_inputs.items():

        numeric_label = "Wartość liczbowa (0-100)"
        numeric_value = f"{int(var['value'])} {var['unit']}"

        variable_row(
            label=var["label"],
            linguistic_value=var["linguistic"],
            linguistic_color=linguistic_colors[var_name][var["linguistic"]],
            numeric_label=numeric_label,
            numeric_value=numeric_value,
        )
