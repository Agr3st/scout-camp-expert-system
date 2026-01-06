import streamlit as st

from src.utils.config import load_config
from src.utils.ui import variable_row
from src.utils.weather_orchestrator import (
    check_weather_variables_existence,
    create_weather_ui_dicts,
)

# load configuration
config = load_config("config.yaml")
linguistic_colors = config["linguistic_colors"]


st.title("🌦️ Moduł pogodowy")

st.caption(
    "Ocena zagrożenia pogodowego dla najbliższej godziny "
    "na podstawie prognozy meteorologicznej oraz logiki rozmytej."
)

check_weather_variables_existence()

weather_inputs, output_risk = create_weather_ui_dicts()

st.markdown("### Stopień zagrożenia")

variable_row(
    label="Poziom zagrożenia pogodowego",
    linguistic_value=output_risk["linguistic"],
    linguistic_color=linguistic_colors["zagrożenie"][output_risk["linguistic"]],
    numeric_label="Wartość liczbowa (0–100)",
    numeric_value=str(output_risk["value"]),
)

st.markdown("### Zmienne wejściowe")

for var_name, var in weather_inputs.items():

    if var_name == "burza":
        numeric_label = "Kod pogodowy"
        numeric_value = str(var["value"])
    else:
        numeric_label = "Wartość liczbowa"
        numeric_value = f"{var['value']:.1f} {var['unit']}"

    variable_row(
        label=var["label"],
        linguistic_value=var["linguistic"],
        linguistic_color=linguistic_colors[var_name][var["linguistic"]],
        numeric_label=numeric_label,
        numeric_value=numeric_value,
    )

# wykres
st.markdown("### Wykres poziomu zagrożenia")

st.line_chart(
    st.session_state["weather_risk_df"].set_index("date")[["final_risk"]],
    x_label="Godzina",
    y_label="Poziom zagrożenia",
)
