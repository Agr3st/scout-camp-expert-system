import streamlit as st

from src.fuzzy.camp import CampRiskModule
from src.utils.logger import setup_logger
from src.utils.session import get_closest_hour_df_row

logger = setup_logger()


def update_camp_risk() -> None:

    logic = CampRiskModule()
    if check_camp_variables_existence():

        weather_risk_row = get_closest_hour_df_row(st.session_state["weather_risk_df"])
        zagrozenie = weather_risk_row["final_risk"]
        ryzyko_terenowe = st.session_state.terrain_df.iloc[0]["ryzyko_terenowe"]
        ryzyko_organizacyjne = st.session_state.organization_df.iloc[0][
            "ryzyko_organizacyjne"
        ]

        risk = logic.assess_risk(zagrozenie, ryzyko_terenowe, ryzyko_organizacyjne)
        st.session_state.camp_risk = risk
        st.session_state.camp_risk_linguistic = logic.interpret_camp_risk(risk)

        logger.info(
            f"Zaktualizowano ryzyko obozowe = {risk} na podstawie: "
            f"zagrozenie = {zagrozenie}; "
            f"ryzyko_terenowe = {ryzyko_terenowe}; "
            f"ryzyko_organizacyjne = {ryzyko_organizacyjne}"
        )


def check_camp_variables_existence() -> bool:
    """
    Sprawdza, czy wszystkie zmienne wyjściowe 1-poziomu są obliczone i przechowywane,
    przez co mogą zostać użyte do obliczenia zmiennej wyjściowej (ryzka obozowego) 2-poziomu.
    """
    try:
        weather_risk_row = get_closest_hour_df_row(st.session_state["weather_risk_df"])
        if (
            weather_risk_row["final_risk"]
            and st.session_state.terrain_df.iloc[0]["ryzyko_terenowe"]
            and st.session_state.organization_df.iloc[0]["ryzyko_organizacyjne"]
        ):
            return True
        logger.info(
            "Nie można obliczyć zmiennej 2-poziomu (ryzyko_obozowe). Brak zmiennych wejściowych."
        )
        return False
    except Exception as e:
        logger.info(f"Nie można obliczyć zmiennej 2-poziomu (ryzyko_obozowe): {e}")
        return False


def create_camp_ui_dicts() -> tuple[dict, dict]:
    """
    Tworzenie słowników dla zmiennych wejściowych i zmiennej wejściowej
    dla UI modułu 2-poziomu (Kokpit).
    """
    camp_inputs = {}
    output_risk = {}

    try:
        weather_risk_row = get_closest_hour_df_row(st.session_state["weather_risk_df"])

        camp_inputs.update(
            {
                "zagrozenie": {
                    "label": "Zagrożenie pogodowe",
                    "value": weather_risk_row["final_risk"],
                    "unit": "",
                    "linguistic": weather_risk_row["risk_linguistic"],
                }
            }
        )
    except Exception:
        pass

    try:
        camp_inputs.update(
            {
                "ryzyko_organizacyjne": {
                    "label": "Ryzyko organizacyjne",
                    "value": st.session_state.organization_df.iloc[0][
                        "ryzyko_organizacyjne"
                    ],
                    "unit": "",
                    "linguistic": st.session_state.organization_linguistic_df.iloc[0][
                        "ryzyko_organizacyjne_linguistic"
                    ],
                },
            }
        )
    except Exception:
        pass
    try:
        camp_inputs.update(
            {
                "ryzyko_terenowe": {
                    "label": "Ryzyko terenowe",
                    "value": st.session_state.terrain_df.iloc[0]["ryzyko_terenowe"],
                    "unit": "",
                    "linguistic": st.session_state.terrain_linguistic_df.iloc[0][
                        "ryzyko_terenowe_linguistic"
                    ],
                },
            }
        )

    except Exception:
        pass

    try:
        output_risk = {
            "value": st.session_state.camp_risk,
            "unit": "",
            "linguistic": st.session_state.camp_risk_linguistic,
        }
    except Exception:
        pass

    return camp_inputs, output_risk
