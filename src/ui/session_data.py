from datetime import datetime

import pandas as pd
import streamlit as st

st.title("Dane sesji")
st.caption("Podgląd wszystkich danych przechowywanych w bieżącej sesji Streamlit.")


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def render_dict(title: str, data: dict):
    with st.expander(title, expanded=True):
        for key, value in data.items():
            st.markdown(f"**{key}:** `{value}`")


def render_dataframe(title: str, df: pd.DataFrame):
    with st.expander(title, expanded=True):
        if df.empty:
            st.info("DataFrame jest pusty")
        else:
            st.dataframe(df, width="stretch")
            st.caption(f"Liczba wierszy: {len(df)}")


def render_value(title: str, value):
    with st.expander(title, expanded=True):
        if value is None:
            st.warning("Brak danych (None)")
        elif isinstance(value, datetime):
            st.markdown(f"🕒 `{value.isoformat()}`")
        else:
            st.code(str(value))


# -------------------------------------------------
# RAW SESSION STATE
# -------------------------------------------------
with st.expander("🧪 Surowy st.session_state (debug)", expanded=False):
    st.json({k: str(v) for k, v in st.session_state.items()})


st.markdown("## Moduł pogodowy")
# -------------------------------------------------
# LOCATION
# -------------------------------------------------
if "location" in st.session_state:
    render_dict("📍 Lokalizacja", st.session_state.location)

# -------------------------------------------------
# WEATHER FORECAST
# -------------------------------------------------
if "weather_forecast_df" in st.session_state:
    render_dataframe(
        "🌦️ Prognoza pogody (weather_forecast_df)",
        st.session_state.weather_forecast_df,
    )

if "weather_forecast_last_update" in st.session_state:
    render_value(
        "⏱️ Ostatnia aktualizacja prognozy",
        st.session_state.weather_forecast_last_update,
    )

# -------------------------------------------------
# WEATHER RISK
# -------------------------------------------------
if "weather_risk_df" in st.session_state:
    render_dataframe(
        "⚠️ Ocena ryzyka pogodowego (weather_risk_df)",
        st.session_state.weather_risk_df,
    )


st.markdown("## Moduł organizacyjny")

if "organization_df" in st.session_state:
    render_dataframe(
        "Dane organizacyjne i ocena ryzyka",
        st.session_state.organization_df,
    )

if "organization_linguistic_df" in st.session_state:
    render_dataframe(
        "Dane organizacyjne i ocena ryzyka - wartości lingwistyczne",
        st.session_state.organization_linguistic_df,
    )
