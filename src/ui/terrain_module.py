import streamlit as st

from src.orchestrators.terrain_orchestrator import (
    check_terrain_variables_existence,
    create_terrain_ui_dicts,
)
from src.utils.config import load_config
from src.utils.ui import variable_row

# load configuration
config = load_config("config.yaml")
linguistic_colors = config["linguistic_colors"]

st.title("Moduł Terenowy")

st.caption(
    "Ocena ryzyka terenowego na podstawie odległości do bezpiecznego schronienia i trudności terenu."
)

check_terrain_variables_existence()

terrain_inputs, output_risk = create_terrain_ui_dicts()

st.markdown("### Ryzyko terenowe")

variable_row(
    label="Poziom ryzyka terenowego",
    linguistic_value=output_risk["linguistic"],
    linguistic_color=linguistic_colors["ryzyko_terenowe"][output_risk["linguistic"]],
    numeric_label="Wartość liczbowa (0–100)",
    numeric_value=str(int(output_risk["value"])),
)

st.markdown("### Zmienne wejściowe")

for var_name, var in terrain_inputs.items():

    if var_name == "trudnosc_terenu":
        numeric_label = "Wartość liczbowa (0-10)"
    else:
        numeric_label = "Wartość liczbowa"
    numeric_value = f"{int(var['value'])} {var['unit']}"

    variable_row(
        label=var["label"],
        linguistic_value=var["linguistic"],
        linguistic_color=linguistic_colors[var_name][var["linguistic"]],
        numeric_label=numeric_label,
        numeric_value=numeric_value,
    )
