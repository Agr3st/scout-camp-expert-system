import pandas as pd
import streamlit as st

from src.fuzzy.organization import OrganizationRiskModule
from src.utils.logger import setup_logger

logger = setup_logger()


def update_organization_risk(liczba_uczestnikow: int, doswiadczenie_kadry: int) -> None:

    logic = OrganizationRiskModule()
    risk = logic.assess_risk(liczba_uczestnikow, doswiadczenie_kadry)

    st.session_state.organization_df = pd.DataFrame(
        [
            {
                "liczba_uczestnikow": int(liczba_uczestnikow),
                "doswiadczenie_kadry": int(doswiadczenie_kadry),
                "ryzyko_organizacyjne": risk,
            }
        ]
    )

    st.session_state.organization_linguistic_df = pd.DataFrame(
        [
            {
                "liczba_uczestnikow_linguistic": logic.interpret_participants(
                    liczba_uczestnikow
                ),
                "doswiadczenie_kadry_linguistic": logic.interpret_experience(
                    doswiadczenie_kadry
                ),
                "ryzyko_organizacyjne_linguistic": logic.interpret_risk(risk),
            }
        ]
    )

    logger.info("Zaktualizowano ryzyko organizacyjne.")


def create_organization_ui_dicts() -> tuple[dict, dict]:
    """
    Tworzenie słowników dla zmiennych wejściowych i zmiennej wejściowej
    dla UI modułu organizacyjnego.
    """

    organization_inputs = {
        "liczba_uczestnikow": {
            "label": "Liczba uczestników",
            "value": st.session_state.organization_df.iloc[0]["liczba_uczestnikow"],
            "unit": "",
            "linguistic": st.session_state.organization_linguistic_df.iloc[0][
                "liczba_uczestnikow_linguistic"
            ],
        },
        "doswiadczenie_kadry": {
            "label": "Doświadczenie kadry",
            "value": st.session_state.organization_df.iloc[0]["doswiadczenie_kadry"],
            "unit": "",
            "linguistic": st.session_state.organization_linguistic_df.iloc[0][
                "doswiadczenie_kadry_linguistic"
            ],
        },
    }

    output_risk = {
        "value": st.session_state.organization_df.iloc[0]["ryzyko_organizacyjne"],
        "unit": "",
        "linguistic": st.session_state.organization_linguistic_df.iloc[0][
            "ryzyko_organizacyjne_linguistic"
        ],
    }

    return organization_inputs, output_risk


def check_organization_variables_existence() -> None:
    if len(st.session_state["organization_df"]) == 0:
        st.info("Brak danych organizacyjnych. Ustaw je w zakładce Dane wejściowe.")
        st.stop()
