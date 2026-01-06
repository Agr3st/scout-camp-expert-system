import folium
import streamlit as st
from streamlit_folium import st_folium

from src.utils.weather_orchestrator import update_weather

POLAND_BOUNDS = {
    "south_west": [49.0, 14.1],
    "north_east": [54.9, 24.2],
}

st.title("Dane wejściowe systemu")
st.markdown("## Lokalizacja")
st.caption(
    "Wybierz lokalizację obozu – dane zostaną użyte do pobrania prognozy "
    "i oceny zagrożenia pogodowego."
)

# METODA WYBORU
method = st.radio(
    "Sposób wyboru lokalizacji:",
    ["Wybór z mapy", "Wprowadzenie ręczne"],
    horizontal=True,
)
lat = st.session_state.location["lat"]
lon = st.session_state.location["lon"]


# OPCJA 1: MAPA
if method == "Wybór z mapy":

    default_location = [52.0, 19.0]  # Polska

    # Jeśli wcześniej wybrano punkt – centrowanie mapy na nim
    if st.session_state.location["lat"] is not None:
        default_location = [
            st.session_state.location["lat"],
            st.session_state.location["lon"],
        ]

    m = folium.Map(location=default_location, zoom_start=6, max_bounds=True)
    m.fit_bounds([POLAND_BOUNDS["south_west"], POLAND_BOUNDS["north_east"]])

    # Jeśli mamy zapisane LAT/LON → dodaj pinezkę
    if st.session_state.location["lat"] is not None:
        folium.Marker(
            location=[
                st.session_state.location["lat"],
                st.session_state.location["lon"],
            ],
            tooltip="Wybrana lokalizacja",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(m)

    map_data = st_folium(m, height=450, width=700)

    # Obsługa kliknięcia
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]

        st.success(f"Wybrano lokalizację: {lat:.4f}, {lon:.4f}")


# OPCJA 2: RĘCZNIE
else:

    col1, col2 = st.columns(2)

    with col1:
        lat = st.number_input(
            "Szerokość geograficzna (LAT)",
            min_value=-90.0,
            max_value=90.0,
            value=st.session_state.location["lat"] or 52.0,
            step=0.0001,
            format="%.4f",
        )

    with col2:
        lon = st.number_input(
            "Długość geograficzna (LON)",
            min_value=-180.0,
            max_value=180.0,
            value=st.session_state.location["lon"] or 19.0,
            step=0.0001,
            format="%.4f",
        )

# zapis lokalizacji
if st.button("Zapisz lokalizację"):
    st.session_state.location.update(
        {
            "lat": lat,
            "lon": lon,
        }
    )
    st.success("Lokalizacja zapisana")
    # zapis -> trigger dla weather pipeline
    update_weather(lat, lon)

# PODSUMOWANIE
st.markdown("---")
st.markdown("### Aktualna konfiguracja")

cfg = st.session_state.location

if cfg["lat"] is not None:
    st.info(
        f"""
        **LAT:** {cfg['lat']:.4f}  
        **LON:** {cfg['lon']:.4f}  
        """
    )
else:
    st.warning("Lokalizacja nie została jeszcze ustawiona.")
