import streamlit as st

from src.orchestrators.organization_orchestrator import (
    check_organization_variables_existence,
    create_organization_ui_dicts,
)
from src.utils.config import load_config
from src.utils.ui import variable_row

# load configuration
config = load_config("config.yaml")
linguistic_colors = config["linguistic_colors"]

st.title("Moduł organizacyjny")

st.caption(
    "Ocena ryzyka organizacyjnego na podstawie liczby osób i doświadczenia kadry."
)

check_organization_variables_existence()

organization_inputs, output_risk = create_organization_ui_dicts()

st.markdown("### Ryzyko organizacyjne")

variable_row(
    label="Poziom ryzyka organizacyjnego",
    linguistic_value=output_risk["linguistic"],
    linguistic_color=linguistic_colors["ryzyko_organizacyjne"][
        output_risk["linguistic"]
    ],
    numeric_label="Wartość liczbowa (0–100)",
    numeric_value=str(output_risk["value"]),
)

st.markdown("### Zmienne wejściowe")

for var_name, var in organization_inputs.items():

    if var_name == "doswiadczenie_kadry":
        numeric_label = "Wartość liczbowa (0-10)"
    else:
        numeric_label = "Wartość liczbowa"
    numeric_value = f"{var['value']} {var['unit']}"

    variable_row(
        label=var["label"],
        linguistic_value=var["linguistic"],
        linguistic_color=linguistic_colors[var_name][var["linguistic"]],
        numeric_label=numeric_label,
        numeric_value=numeric_value,
    )
