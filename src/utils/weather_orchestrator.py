from datetime import datetime, timedelta, timezone

import streamlit as st

from src.fuzzy.weather import WeatherLogicSystem
from src.scraper.open_meteo import get_hourly_weather_forecast
from src.utils.logger import setup_logger
from src.utils.session import get_closest_hour_df_row

logger = setup_logger()


def should_refresh_weather(interval_minutes: int = 30) -> bool:
    last_update = st.session_state.get("weather_forecast_last_update")

    if last_update is None:
        return True

    return datetime.now(timezone.utc) - last_update >= timedelta(
        minutes=interval_minutes
    )


def update_weather(lat: float, lon: float) -> None:
    logger.info(f"Pobieranie prognozy: lat={lat}, lon={lon}")

    forecast_df = get_hourly_weather_forecast(lat, lon)

    logic = WeatherLogicSystem()
    risk_df = logic.assess_risk_forecast_df(forecast_df)

    st.session_state["weather_forecast_df"] = forecast_df
    st.session_state["weather_risk_df"] = risk_df
    st.session_state["weather_forecast_last_update"] = datetime.now(timezone.utc)
    logger.info("Zaktualizowano dane pogodowe.")


@st.fragment(run_every="1m")
def refresh_weather(interval_minutes: int = 30) -> None:
    if st.session_state.location["lat"] and st.session_state.location["lon"]:
        if should_refresh_weather(interval_minutes=interval_minutes):
            update_weather(
                lat=st.session_state.location["lat"],
                lon=st.session_state.location["lon"],
            )


def create_weather_ui_dicts() -> tuple[dict, dict]:
    """
    Tworzenie słowników dla zmiennych wejściowych i zmiennej wejściowej
    dla UI modułu pogodowego.
    """
    weather_risk_row = get_closest_hour_df_row(st.session_state["weather_risk_df"])
    weather_forecast_row = get_closest_hour_df_row(
        st.session_state["weather_forecast_df"]
    )

    weather_inputs = {
        "temperatura": {
            "label": "Temperatura odczuwalna",
            "value": weather_forecast_row["temperature_2m"],
            "unit": "°C",
            "linguistic": weather_risk_row["temperature_linguistic"],
        },
        "wiatr": {
            "label": "Wiatr",
            "value": weather_forecast_row["wind_speed_10m"],
            "unit": "m/s",
            "linguistic": weather_risk_row["wind_linguistic"],
        },
        "deszcz": {
            "label": "Deszcz",
            "value": weather_forecast_row["rain"],
            "unit": "mm/h",
            "linguistic": weather_risk_row["rain_linguistic"],
        },
        "burza": {
            "label": "Burza",
            "value": weather_forecast_row["weather_code"],
            "unit": "weather_code",
            "linguistic": weather_risk_row["thunder_linguistic"],
        },
    }

    output_risk = {
        "value": int(weather_risk_row["final_risk"]),
        "unit": "/100 pkt",
        "linguistic": weather_risk_row["risk_linguistic"],
    }

    return weather_inputs, output_risk


def check_weather_variables_existence() -> None:
    if (
        st.session_state["weather_risk_df"] is not None
        and len(st.session_state["weather_risk_df"]) == 0
    ):
        st.info("Brak danych pogodowych. Ustaw lokalizację w zakładce Dane wejściowe.")
        st.stop()
