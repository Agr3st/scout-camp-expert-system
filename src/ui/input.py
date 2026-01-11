import folium
import streamlit as st
from streamlit_folium import st_folium

from src.orchestrators.organization_orchestrator import update_organization_risk
from src.orchestrators.terrain_orchestrator import update_terrain_risk
from src.orchestrators.weather_orchestrator import update_weather

POLAND_BOUNDS = {
    "south_west": [49.0, 14.1],
    "north_east": [54.9, 24.2],
}


st.title("Dane wejściowe systemu")

# PODSUMOWANIE
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

cfg = st.session_state.organization_df
if len(cfg) > 0:
    st.info(
        f"""
        **Liczba uczestników:** {cfg.iloc[0]['liczba_uczestnikow']}  
        **Doświadczenie kadry (ocena 0-10):** {cfg.iloc[0]['doswiadczenie_kadry']}  
        """
    )
else:
    st.warning("Dane organizacyjne nie zostały jeszcze ustawione.")

cfg = st.session_state.terrain_df
if len(cfg) > 0:
    st.info(
        f"""
        **Odległość od najbliższego schronienia:** {cfg.iloc[0]['odleglosc_od_schronienia']} m \n
        **Trudność terenu (ocena 0-10):** {cfg.iloc[0]['trudnosc_terenu']}  
        """
    )
else:
    st.warning("Dane terenowe nie zostały jeszcze ustawione.")

st.markdown("---")


# Lokalizacja
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
    if lat and lon:
        st.session_state.location.update(
            {
                "lat": lat,
                "lon": lon,
            }
        )
        st.success("Lokalizacja zapisana")
        # zapis -> trigger dla weather pipeline
        update_weather(lat, lon)
    else:
        st.info("Lokalizacja nie została jeszcze wybrana.")

# Dane organizacyjne
st.markdown("## Dane organizacyjne")
st.caption(
    "Wprowadź liczbę uczestników i oceń doświadczenie kadry."
    " Pozwoli to oszacować ryzyko związane z sytuacjami organizacyjnymi."
)

col1, col2 = st.columns(2)

with col1:
    liczba_uczestnikow = st.number_input(
        "Liczba uczestników",
        min_value=1,
        step=1,
        value=20,
        help="Liczba uczestników obozu (bez kadry).",
    )

with col2:
    doswiadczenie_kadry = st.slider(
        "Doświadczenie kadry",
        min_value=0,
        max_value=10,
        value=5,
        step=1,
        help="""0 – małe doświadczenie, 10 – duże doświadczenie. 
        Ogólna subiektywna ocena kadry. 
        Należy wziąć pod uwagę ile osób było na obozie harcerskim i ile razy, 
        umiejętności zarządzania i radzenia sobie w trudnych sytuacjach.""",
    )
if st.button("Zapisz dane", key="organization"):

    if liczba_uczestnikow and doswiadczenie_kadry:
        update_organization_risk(liczba_uczestnikow, doswiadczenie_kadry)
        st.success("Dane zostały zapisane.")

    else:
        st.info("Przed zapisaniem ustaw dane.")

# Dane terenowe
st.markdown("## Dane terenowe")
st.caption(
    "Wprowadź odległość do najbliższego schronienia i oceń trudność terenu."
    " Pozwoli to oszacować ryzyko związane z warunkami terenowymi."
)

col1, col2 = st.columns(2)

with col1:
    odleglosc_od_schronienia = st.number_input(
        "Odległość od schronienia [m]",
        min_value=1,
        step=1,
        value=100,
        help="Odległość od obozu do bezpiecznego miejsca schronienia.",
    )

with col2:
    trudnosc_terenu = st.slider(
        "Trudność terenu",
        min_value=0,
        max_value=10,
        value=5,
        step=1,
        help="""0 – mała, 10 – duża. 
        Ogólna subiektywna ocena trudności terenu. 
        Należy wziąć pod uwagę jakość dróg i ścieżek, górzystość, gęstość zalesienia
        i inne czynniki wpływające na trudność przemieszczania się.""",
    )
if st.button("Zapisz dane", key="terrain"):

    if odleglosc_od_schronienia and trudnosc_terenu:
        update_terrain_risk(odleglosc_od_schronienia, trudnosc_terenu)
        st.success("Dane zostały zapisane.")

    else:
        st.info("Przed zapisaniem ustaw dane.")
