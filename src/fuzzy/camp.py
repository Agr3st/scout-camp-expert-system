"""
2-level module - overall camp risk
"""

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from skfuzzy.control import Antecedent, Consequent, Rule

from src.fuzzy.base import BaseFuzzyModule
from src.utils.config import load_config


class CampRiskModule(BaseFuzzyModule):

    def __init__(self):
        (
            self.zagrozenie,
            self.ryzyko_organizacyjne,
            self.ryzyko_terenowe,
            self.ryzyko_obozowe,
        ) = self._create_variables()
        self._set_membership_functions(
            self.zagrozenie,
            self.ryzyko_organizacyjne,
            self.ryzyko_terenowe,
            self.ryzyko_obozowe,
        )
        self.rules_config = load_config().get("camp_rules", {})
        self.rules = self._define_rules(
            self.zagrozenie,
            self.ryzyko_organizacyjne,
            self.ryzyko_terenowe,
            self.ryzyko_obozowe,
        )
        self.system = ctrl.ControlSystem(self.rules)

    @staticmethod
    def _create_variables() -> tuple[Antecedent, Antecedent, Antecedent, Consequent]:
        """Definicja zmiennych wejściowych i wyjściowych"""
        zagrozenie = ctrl.Antecedent(np.arange(0, 101, 1), "zagrozenie")
        ryzyko_organizacyjne = ctrl.Antecedent(
            np.arange(0, 101, 1), "ryzyko_organizacyjne"
        )
        ryzyko_terenowe = ctrl.Antecedent(np.arange(0, 101, 1), "ryzyko_terenowe")

        # zmienna wyjsciowa
        ryzyko_obozowe = ctrl.Consequent(np.arange(0, 101, 1), "ryzyko_obozowe")

        return zagrozenie, ryzyko_organizacyjne, ryzyko_terenowe, ryzyko_obozowe

    @staticmethod
    def _set_membership_functions(
        zagrozenie: Antecedent,
        ryzyko_organizacyjne: Antecedent,
        ryzyko_terenowe: Antecedent,
        ryzyko_obozowe: Consequent,
    ) -> None:
        """Funkcje przynależności."""

        zagrozenie["niskie"] = fuzz.trapmf(zagrozenie.universe, [0, 0, 20, 50])
        zagrozenie["średnie"] = fuzz.trimf(zagrozenie.universe, [20, 50, 80])
        zagrozenie["wysokie"] = fuzz.trapmf(zagrozenie.universe, [50, 80, 100, 100])

        ryzyko_organizacyjne["niskie"] = fuzz.trapmf(
            ryzyko_organizacyjne.universe, [0, 0, 20, 50]
        )
        ryzyko_organizacyjne["średnie"] = fuzz.trimf(
            ryzyko_organizacyjne.universe, [20, 50, 80]
        )
        ryzyko_organizacyjne["wysokie"] = fuzz.trapmf(
            ryzyko_organizacyjne.universe, [50, 80, 100, 100]
        )

        ryzyko_terenowe["niskie"] = fuzz.trapmf(
            ryzyko_terenowe.universe, [0, 0, 20, 50]
        )
        ryzyko_terenowe["średnie"] = fuzz.trimf(ryzyko_terenowe.universe, [20, 50, 80])
        ryzyko_terenowe["wysokie"] = fuzz.trapmf(
            ryzyko_terenowe.universe, [50, 80, 100, 100]
        )

        ryzyko_obozowe["niskie"] = fuzz.trapmf(ryzyko_obozowe.universe, [0, 0, 20, 50])
        ryzyko_obozowe["średnie"] = fuzz.trimf(ryzyko_obozowe.universe, [20, 50, 80])
        ryzyko_obozowe["wysokie"] = fuzz.trapmf(
            ryzyko_obozowe.universe, [50, 80, 100, 100]
        )

    def _define_rules(
        self,
        zagrozenie: Antecedent,
        ryzyko_organizacyjne: Antecedent,
        ryzyko_terenowe: Antecedent,
        ryzyko_obozowe: Consequent,
    ) -> list[Rule]:

        variable_map = {
            "zagrozenie": zagrozenie,
            "ryzyko_organizacyjne": ryzyko_organizacyjne,
            "ryzyko_terenowe": ryzyko_terenowe,
            "ryzyko_obozowe": ryzyko_obozowe,
        }

        rules = []

        for rule_def in self.rules_config:
            conditions = []

            for var_name, label in rule_def["if"].items():
                conditions.append(variable_map[var_name][label])

            antecedent = conditions[0]
            for cond in conditions[1:]:
                antecedent &= cond

            consequent_label = rule_def["then"]["ryzyko_obozowe"]
            consequent = ryzyko_obozowe[consequent_label]

            rules.append(ctrl.Rule(antecedent, consequent))

        return rules

    def interpret_camp_risk(self, value: float) -> str:
        return self._interpret(
            variable=self.ryzyko_obozowe,
            labels=["niskie", "średnie", "wysokie"],
            value=value,
        )

    def assess_risk(
        self,
        zagrozenie: float,
        ryzyko_organizacyjne: float,
        ryzyko_terenowe: float,
        visualize=False,
    ) -> tuple[float, float]:
        """
        Oblicza ryzyko obozowe na podstawie wartości wejściowych.
        """
        sim = ctrl.ControlSystemSimulation(self.system)

        sim.input["zagrozenie"] = float(zagrozenie)
        sim.input["ryzyko_organizacyjne"] = float(ryzyko_organizacyjne)
        sim.input["ryzyko_terenowe"] = float(ryzyko_terenowe)

        sim.compute()

        risk = float(sim.output["ryzyko_obozowe"])

        if visualize:
            print("=== WIZUALIZACJA WNIOSKOWANIA ===")
            print(f"Temperatura: {zagrozenie}")
            print(f"ryzyko_organizacyjne: {ryzyko_organizacyjne}")
            print(f"ryzyko_terenowe: {ryzyko_terenowe}")
            print(f"Ryzyko obozowe: {risk}")

            # Wykresy aktywacji zmiennych wejściowych
            self.zagrozenie.view(sim=sim)
            self.ryzyko_organizacyjne.view(sim=sim)
            self.ryzyko_terenowe.view(sim=sim)

            # Wykres zmiennej wyjściowej z zaznaczonym wynikiem
            self.ryzyko_obozowe.view(sim=sim)

            plt.show()

        return risk
