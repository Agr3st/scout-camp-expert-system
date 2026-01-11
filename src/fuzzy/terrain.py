import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from skfuzzy.control import Antecedent, Consequent, Rule

from src.fuzzy.base import BaseFuzzyModule
from src.utils.config import load_config

MAX_DISTANCE = 2000
MIN_DISTANCE = 0


class TerrainRiskModule(BaseFuzzyModule):

    def __init__(self):
        (
            self.odleglosc_od_schronienia,
            self.trudnosc_terenu,
            self.ryzyko_terenowe,
        ) = self._create_variables()
        self._set_membership_functions(
            self.odleglosc_od_schronienia,
            self.trudnosc_terenu,
            self.ryzyko_terenowe,
        )
        self.rules_config = load_config().get("terrain_rules", {})
        self.rules = self._define_rules(
            self.odleglosc_od_schronienia,
            self.trudnosc_terenu,
            self.ryzyko_terenowe,
        )
        self.system = ctrl.ControlSystem(self.rules)

    @staticmethod
    def _create_variables() -> tuple[Antecedent, Antecedent, Consequent]:
        """Definicja zmiennych wejściowych i wyjściowych"""
        odleglosc_od_schronienia = ctrl.Antecedent(
            np.arange(MIN_DISTANCE, MAX_DISTANCE + 1, 1), "odleglosc_od_schronienia"
        )  # w metrach
        trudnosc_terenu = ctrl.Antecedent(np.arange(0, 11, 1), "trudnosc_terenu")

        # zmienna wyjsciowa
        ryzyko_terenowe = ctrl.Consequent(np.arange(0, 101, 1), "ryzyko_terenowe")

        return odleglosc_od_schronienia, trudnosc_terenu, ryzyko_terenowe

    @staticmethod
    def _set_membership_functions(
        odleglosc_od_schronienia: Antecedent,
        trudnosc_terenu: Antecedent,
        ryzyko_terenowe: Consequent,
    ) -> None:
        """Funkcje przynależności."""

        odleglosc_od_schronienia["mała"] = fuzz.trapmf(
            odleglosc_od_schronienia.universe, [0, 0, 250, 1000]
        )
        odleglosc_od_schronienia["średnia"] = fuzz.trimf(
            odleglosc_od_schronienia.universe, [250, 1000, 1750]
        )
        odleglosc_od_schronienia["duża"] = fuzz.trapmf(
            odleglosc_od_schronienia.universe, [1000, 1750, 2000, 2000]
        )

        trudnosc_terenu["mała"] = fuzz.trapmf(trudnosc_terenu.universe, [0, 0, 1, 5])
        trudnosc_terenu["średnia"] = fuzz.trimf(trudnosc_terenu.universe, [1, 5, 9])
        trudnosc_terenu["duża"] = fuzz.trapmf(trudnosc_terenu.universe, [5, 9, 10, 10])

        ryzyko_terenowe["niskie"] = fuzz.trapmf(
            ryzyko_terenowe.universe, [0, 0, 20, 50]
        )
        ryzyko_terenowe["średnie"] = fuzz.trimf(ryzyko_terenowe.universe, [20, 50, 80])
        ryzyko_terenowe["wysokie"] = fuzz.trapmf(
            ryzyko_terenowe.universe, [50, 80, 100, 100]
        )

    def _define_rules(
        self,
        odleglosc_od_schronienia: Antecedent,
        trudnosc_terenu: Antecedent,
        ryzyko_terenowe: Consequent,
    ) -> list[Rule]:

        variable_map = {
            "odleglosc_od_schronienia": odleglosc_od_schronienia,
            "trudnosc_terenu": trudnosc_terenu,
            "ryzyko_terenowe": ryzyko_terenowe,
        }

        rules = []

        for rule_def in self.rules_config:
            conditions = []

            for var_name, label in rule_def["if"].items():
                conditions.append(variable_map[var_name][label])

            antecedent = conditions[0]
            for cond in conditions[1:]:
                antecedent &= cond

            consequent_label = rule_def["then"]["ryzyko_terenowe"]
            consequent = ryzyko_terenowe[consequent_label]

            rules.append(ctrl.Rule(antecedent, consequent))

        return rules

    def interpret_distance(self, value: int) -> str:
        if value >= 0:
            value = min(value, MAX_DISTANCE)
        else:
            value = max(value, MIN_DISTANCE)
        return self._interpret(
            variable=self.odleglosc_od_schronienia,
            labels=["mała", "średnia", "duża"],
            value=value,
        )

    def interpret_terrain_difficulty(self, value: int) -> str:
        return self._interpret(
            variable=self.trudnosc_terenu,
            labels=["mała", "średnia", "duża"],
            value=value,
        )

    def interpret_risk(self, value: float) -> str:
        return self._interpret(
            variable=self.ryzyko_terenowe,
            labels=["niskie", "średnie", "wysokie"],
            value=value,
        )

    def assess_risk(
        self,
        odleglosc_od_schronienia: int,
        trudnosc_terenu: int,
        visualize=False,
    ) -> float:
        """
        Oblicza ryzyko na podstawie wartości zmiennych wejściowych.
        """
        sim = ctrl.ControlSystemSimulation(self.system)

        sim.input["odleglosc_od_schronienia"] = int(odleglosc_od_schronienia)
        sim.input["trudnosc_terenu"] = int(trudnosc_terenu)

        sim.compute()

        risk = sim.output["ryzyko_terenowe"]

        if visualize:
            print("=== WIZUALIZACJA WNIOSKOWANIA ===")
            print(f"odleglosc_od_schronienia: {odleglosc_od_schronienia}")
            print(f"trudnosc_terenu: {trudnosc_terenu}")
            print(f"Ryzyko terenowe: {risk}")

            # Wykresy aktywacji zmiennych wejściowych
            self.odleglosc_od_schronienia.view(sim=sim)
            self.trudnosc_terenu.view(sim=sim)

            # Wykres zmiennej wyjściowej z zaznaczonym wynikiem
            self.ryzyko_terenowe.view(sim=sim)

            plt.show()

        return risk
