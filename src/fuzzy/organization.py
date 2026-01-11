import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from skfuzzy.control import Antecedent, Consequent, Rule

from src.fuzzy.base import BaseFuzzyModule
from src.utils.config import load_config


class OrganizationRiskModule(BaseFuzzyModule):

    def __init__(self):
        self.liczba_uczestnikow, self.doswiadczenie_kadry, self.ryzyko_organizacyjne = (
            self._create_variables()
        )
        self._set_membership_functions(
            self.liczba_uczestnikow, self.doswiadczenie_kadry, self.ryzyko_organizacyjne
        )
        self.rules_config = load_config().get("organization_rules", {})
        self.rules = self._define_rules(
            self.liczba_uczestnikow, self.doswiadczenie_kadry, self.ryzyko_organizacyjne
        )
        self.system = ctrl.ControlSystem(self.rules)

    @staticmethod
    def _create_variables() -> tuple[Antecedent, Antecedent, Consequent]:
        """Definicja zmiennych wejściowych i wyjściowych"""
        liczba_uczestnikow = ctrl.Antecedent(np.arange(0, 121, 1), "liczba_uczestnikow")
        doswiadczenie_kadry = ctrl.Antecedent(
            np.arange(0, 11, 1), "doswiadczenie_kadry"
        )

        # zmienna wyjsciowa
        ryzyko_organizacyjne = ctrl.Consequent(
            np.arange(0, 101, 1), "ryzyko_organizacyjne"
        )

        return liczba_uczestnikow, doswiadczenie_kadry, ryzyko_organizacyjne

    @staticmethod
    def _set_membership_functions(
        liczba_uczestnikow: Antecedent,
        doswiadczenie_kadry: Antecedent,
        ryzyko_organizacyjne: Consequent,
    ) -> None:
        """Funkcje przynależności."""

        liczba_uczestnikow["mała"] = fuzz.trapmf(
            liczba_uczestnikow.universe, [0, 0, 20, 60]
        )
        liczba_uczestnikow["średnia"] = fuzz.trimf(
            liczba_uczestnikow.universe, [20, 60, 100]
        )
        liczba_uczestnikow["duża"] = fuzz.trapmf(
            liczba_uczestnikow.universe, [60, 100, 120, 120]
        )

        doswiadczenie_kadry["małe"] = fuzz.trapmf(
            doswiadczenie_kadry.universe, [0, 0, 1, 5]
        )
        doswiadczenie_kadry["średnie"] = fuzz.trimf(
            doswiadczenie_kadry.universe, [1, 5, 9]
        )
        doswiadczenie_kadry["duże"] = fuzz.trapmf(
            doswiadczenie_kadry.universe, [5, 9, 10, 10]
        )

        ryzyko_organizacyjne["niskie"] = fuzz.trapmf(
            ryzyko_organizacyjne.universe, [0, 0, 20, 50]
        )
        ryzyko_organizacyjne["średnie"] = fuzz.trimf(
            ryzyko_organizacyjne.universe, [20, 50, 80]
        )
        ryzyko_organizacyjne["wysokie"] = fuzz.trapmf(
            ryzyko_organizacyjne.universe, [50, 80, 100, 100]
        )

    def _define_rules(
        self,
        liczba_uczestnikow: Antecedent,
        doswiadczenie_kadry: Antecedent,
        ryzyko_organizacyjne: Consequent,
    ) -> list[Rule]:

        variable_map = {
            "liczba_uczestnikow": liczba_uczestnikow,
            "doswiadczenie_kadry": doswiadczenie_kadry,
            "ryzyko_organizacyjne": ryzyko_organizacyjne,
        }

        rules = []

        for rule_def in self.rules_config:
            conditions = []

            for var_name, label in rule_def["if"].items():
                conditions.append(variable_map[var_name][label])

            antecedent = conditions[0]
            for cond in conditions[1:]:
                antecedent &= cond

            consequent_label = rule_def["then"]["ryzyko_organizacyjne"]
            consequent = ryzyko_organizacyjne[consequent_label]

            rules.append(ctrl.Rule(antecedent, consequent))

        return rules

    def interpret_participants(self, value: int) -> str:
        return self._interpret(
            variable=self.liczba_uczestnikow,
            labels=["mała", "średnia", "duża"],
            value=value,
        )

    def interpret_experience(self, value: int) -> str:
        return self._interpret(
            variable=self.doswiadczenie_kadry,
            labels=["małe", "średnie", "duże"],
            value=value,
        )

    def interpret_risk(self, value: float) -> str:
        return self._interpret(
            variable=self.ryzyko_organizacyjne,
            labels=["niskie", "średnie", "wysokie"],
            value=value,
        )

    def assess_risk(
        self,
        liczba_uczestnikow: int,
        doswiadczenie_kadry: int,
        visualize=False,
    ) -> int:
        """
        Oblicza ryzyko na podstawie wartości wejściowych.
        """
        sim = ctrl.ControlSystemSimulation(self.system)

        sim.input["liczba_uczestnikow"] = int(liczba_uczestnikow)
        sim.input["doswiadczenie_kadry"] = int(doswiadczenie_kadry)

        sim.compute()

        risk = int(sim.output["ryzyko_organizacyjne"])

        if visualize:
            print("=== WIZUALIZACJA WNIOSKOWANIA ===")
            print(f"liczba_uczestnikow: {liczba_uczestnikow}")
            print(f"doswiadczenie_kadry: {doswiadczenie_kadry}")
            print(f"Ryzyko organizacyjne: {risk}")

            # Wykresy aktywacji zmiennych wejściowych
            self.liczba_uczestnikow.view(sim=sim)
            self.doswiadczenie_kadry.view(sim=sim)

            # Wykres zmiennej wyjściowej z zaznaczonym wynikiem
            self.ryzyko_organizacyjne.view(sim=sim)

            plt.show()

        return risk
