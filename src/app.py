import streamlit as st

from src.utils.session import init_session_state
from src.utils.weather_orchestrator import refresh_weather

init_session_state()

cockpit_page = st.Page(
    "ui/cockpit.py", title="Kokpit", icon=":material/home:", default=True
)
weather_module_page = st.Page(
    "ui/weather_module.py",
    title="Moduł Pogodowy",
    icon=":material/partly_cloudy_day:",
)
organization_module_page = st.Page(
    "ui/organization_module.py",
    title="Moduł Organizacyjny",
    icon=":material/crown:",
)
terrain_module_page = st.Page(
    "ui/terrain_module.py",
    title="Moduł Terenowy",
    icon=":material/map:",
)
input_page = st.Page("ui/input.py", title="Dane wejściowe", icon=":material/upload:")
info_page = st.Page("ui/info.py", title="O systemie", icon=":material/info:")
session_data_page = st.Page(
    "ui/session_data.py", title="Dane sesji", icon=":material/browse_activity:"
)

pg = st.navigation(
    [
        cockpit_page,
        weather_module_page,
        organization_module_page,
        terrain_module_page,
        input_page,
        info_page,
        session_data_page,
    ]
)
pg.run()


# orkiestrator modułu pogodowego
with st.container():
    refresh_weather(interval_minutes=30)
