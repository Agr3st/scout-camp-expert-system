from zoneinfo import ZoneInfo

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

# ostatnia aktualizacja
dt = st.session_state.weather_forecast_last_update

if dt is not None:
    dt_pl = dt.astimezone(ZoneInfo("Europe/Warsaw"))
    st.markdown(f"🕒 **Ostatnia aktualizacja:** {dt_pl.strftime('%d.%m.%Y %H:%M:%S')}")

# elementy
weather_inputs, output_risk = create_weather_ui_dicts()

st.markdown("### Stopień zagrożenia")

variable_row(
    label="Poziom zagrożenia pogodowego",
    linguistic_value=output_risk["linguistic"],
    linguistic_color=linguistic_colors["zagrozenie"][output_risk["linguistic"]],
    numeric_label="Wartość liczbowa (0–100)",
    numeric_value=str(output_risk["value"]),
)

st.markdown("### Zmienne wejściowe")

for var_name, var in weather_inputs.items():

    if var_name == "burza":
        numeric_label = "Kod pogodowy"
        numeric_value = str(int(var["value"]))
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
st.markdown("### Wykresy zmienności w czasie")

st.markdown("#### Poziom zagrożenia")
st.line_chart(
    st.session_state["weather_risk_df"].set_index("date")[["final_risk"]],
    x_label="Godzina",
    y_label="Poziom zagrożenia",
)

st.markdown("#### Temperatura odczuwalna")

st.line_chart(
    st.session_state["weather_forecast_df"].set_index("date")[["temperature_2m"]],
    x_label="Godzina",
    y_label="Temperatura",
)

st.markdown("#### Prędkość wiatru")

st.line_chart(
    st.session_state["weather_forecast_df"].set_index("date")[["wind_speed_10m"]],
    x_label="Godzina",
    y_label="Prędkość wiatru",
)

st.markdown("#### Opady deszczu")

st.line_chart(
    st.session_state["weather_forecast_df"].set_index("date")[["rain"]],
    x_label="Godzina",
    y_label="Deszcz",
)
