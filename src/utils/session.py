from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st


def init_session_state() -> None:
    """
    Inicjalizuje wszystkie wymagane klucze w session_state.
    """

    # Weather module
    if "location" not in st.session_state:
        st.session_state.location = {
            "lat": None,
            "lon": None,
        }

    if "weather_forecast_df" not in st.session_state:
        st.session_state.weather_forecast_df = pd.DataFrame()

    if "weather_forecast_last_update" not in st.session_state:
        st.session_state.weather_forecast_last_update = None

    if "weather_risk_df" not in st.session_state:
        st.session_state.weather_risk_df = pd.DataFrame()

    # Organization module
    if "organization_df" not in st.session_state:
        st.session_state.organization_df = pd.DataFrame(
            columns=[
                "liczba_uczestnikow",
                "doswiadczenie_kadry",
                "ryzyko_organizacyjne",
            ]
        )

    if "organization_linguistic_df" not in st.session_state:
        st.session_state.organization_linguistic_df = pd.DataFrame(
            columns=[
                "liczba_uczestnikow_linguistic",
                "doswiadczenie_kadry_linguistic",
                "ryzyko_organizacyjne_linguistic",
            ]
        )

    # Terrain module
    if "terrain_df" not in st.session_state:
        st.session_state.terrain_df = pd.DataFrame(
            columns=[
                "odleglosc_od_schronienia",
                "trudnosc_terenu",
                "ryzyko_terenowe",
            ]
        )

    if "terrain_linguistic_df" not in st.session_state:
        st.session_state.terrain_linguistic_df = pd.DataFrame(
            columns=[
                "odleglosc_od_schronienia_linguistic",
                "trudnosc_terenu_linguistic",
                "ryzyko_terenowe_linguistic",
            ]
        )

    # Camp risk module (2-level)
    if "camp_risk" not in st.session_state:
        st.session_state.camp_risk = None
    if "camp_risk_linguistic" not in st.session_state:
        st.session_state.camp_risk_linguistic = None


def get_closest_hour_df_row(df: pd.DataFrame) -> pd.Series:
    """
    Zwraca wiersz z pd.DataFrame dla najbliższej godziny polskiego czasu.
    Automatycznie obsługuje zaokrąglanie (np. 14:29 -> 14:00, 14:33 -> 15:00).
    Strefa czasowa Europe/Berlin ze względu na ograniczenia Open Meteo API.
    """
    tz = ZoneInfo("Europe/Berlin")
    now = datetime.now(tz)

    closest_idx = (df["date"] - now).abs().idxmin()

    return df.iloc[closest_idx]
