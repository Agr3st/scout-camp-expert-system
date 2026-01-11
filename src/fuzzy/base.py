from abc import ABC, abstractmethod
from typing import Dict, List

import skfuzzy as fuzz
from skfuzzy import control as ctrl
from skfuzzy.control import Antecedent, Consequent, Rule


class BaseFuzzyModule(ABC):
    """
    Klasa bazowa dla modułów systemu logiki rozmytej.
    """

    def __init__(self):
        pass

    def _interpret(
        self, variable: Antecedent | Consequent, labels: list[str], value: float
    ) -> str:
        """
        Zwraca etykietę lingwistyczną o najwyższym stopniu przynależności.

        Parametry:
            variable : skfuzzy.control.Antecedent lub Consequent
            labels   : lista nazw zbiorów lingwistycznych
            value    : wartość liczbowa

        Zwraca:
            str: etykieta lingwistyczna (np. 'umiarkowany')
        """
        memberships = {
            label: fuzz.interp_membership(
                variable.universe,
                variable[label].mf,
                value,
            )
            for label in labels
        }

        return max(memberships, key=memberships.get)
