import pandas as pd
import streamlit as st

from src.fuzzy.terrain import TerrainRiskModule
from src.utils.logger import setup_logger

logger = setup_logger()


def update_terrain_risk(odleglosc_od_schronienia: int, trudnosc_terenu: int) -> None:

    logic = TerrainRiskModule()
    risk = logic.assess_risk(odleglosc_od_schronienia, trudnosc_terenu)

    st.session_state.terrain_df = pd.DataFrame(
        [
            {
                "odleglosc_od_schronienia": int(odleglosc_od_schronienia),
                "trudnosc_terenu": int(trudnosc_terenu),
                "ryzyko_terenowe": risk,
            }
        ]
    )

    st.session_state.terrain_linguistic_df = pd.DataFrame(
        [
            {
                "odleglosc_od_schronienia_linguistic": logic.interpret_distance(
                    odleglosc_od_schronienia
                ),
                "trudnosc_terenu_linguistic": logic.interpret_terrain_difficulty(
                    trudnosc_terenu
                ),
                "ryzyko_terenowe_linguistic": logic.interpret_risk(risk),
            }
        ]
    )

    logger.info("Zaktualizowano ryzyko terenowe.")


def create_terrain_ui_dicts() -> tuple[dict, dict]:
    """
    Tworzenie słowników dla zmiennych wejściowych i zmiennej wejściowej
    dla UI modułu terenowego.
    """

    terrain_inputs = {
        "odleglosc_od_schronienia": {
            "label": "Odległość od schronienia",
            "value": st.session_state.terrain_df.iloc[0]["odleglosc_od_schronienia"],
            "unit": "m",
            "linguistic": st.session_state.terrain_linguistic_df.iloc[0][
                "odleglosc_od_schronienia_linguistic"
            ],
        },
        "trudnosc_terenu": {
            "label": "Trudność terenu",
            "value": st.session_state.terrain_df.iloc[0]["trudnosc_terenu"],
            "unit": "",
            "linguistic": st.session_state.terrain_linguistic_df.iloc[0][
                "trudnosc_terenu_linguistic"
            ],
        },
    }

    output_risk = {
        "value": st.session_state.terrain_df.iloc[0]["ryzyko_terenowe"],
        "unit": "",
        "linguistic": st.session_state.terrain_linguistic_df.iloc[0][
            "ryzyko_terenowe_linguistic"
        ],
    }

    return terrain_inputs, output_risk


def check_terrain_variables_existence() -> None:
    if len(st.session_state["terrain_df"]) == 0:
        st.info("Brak danych terenowych. Ustaw je w zakładce Dane wejściowe.")
        st.stop()
