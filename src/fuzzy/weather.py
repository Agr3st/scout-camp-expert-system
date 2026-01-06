import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from skfuzzy.control import Antecedent, Consequent, Rule

TEMP_MIN = 0
TEMP_MAX = 40
WIATR_MIN = 0
WIATR_MAX = 25
DESZCZ_MIN = 0
DESZCZ_MAX = 10
THUNDER_PENALTY = 20  # zmienna jakościowa (dodawane 20 pkt do finalnego zagrożenia)
THUNDER_WEATHER_CODES = [
    95,
    96,
    99,
]  # kody dla burzy zgodnie z: https://open-meteo.com/en/docs#weather_variable_documentation


class WeatherLogicSystem:

    def __init__(self):
        self.temperatura, self.wiatr, self.deszcz, self.zagrozenie = (
            self._create_variables()
        )
        self._set_membership_functions(
            self.temperatura, self.wiatr, self.deszcz, self.zagrozenie
        )
        self.rules = self._define_rules(
            self.temperatura, self.wiatr, self.deszcz, self.zagrozenie
        )
        self.system = ctrl.ControlSystem(self.rules)

    @staticmethod
    def _create_variables() -> tuple[Antecedent, Antecedent, Antecedent, Consequent]:
        """Definicja zmiennych wejściowych i wyjściowych"""
        temperatura = ctrl.Antecedent(np.arange(0, 41, 1), "temperatura")
        wiatr = ctrl.Antecedent(np.arange(0, 25, 0.1), "wiatr")
        deszcz = ctrl.Antecedent(np.arange(0, 10, 0.1), "deszcz")

        # zmienna wyjsciowa
        zagrozenie = ctrl.Consequent(np.arange(0, 101, 1), "zagrozenie")

        return temperatura, wiatr, deszcz, zagrozenie

    @staticmethod
    def _set_membership_functions(
        temperatura: Antecedent,
        wiatr: Antecedent,
        deszcz: Antecedent,
        zagrozenie: Consequent,
    ) -> None:
        """Funkcje przynależności."""

        # TEMPERATURA: niska, umiarkowana, wysoka
        temperatura["niska"] = fuzz.trapmf(
            temperatura.universe, [0, 0, 10, 18]
        )  # niska to 10-
        temperatura["umiarkowana"] = fuzz.trimf(
            temperatura.universe, [10, 20, 30]
        )  # umiarkowana to 15-25
        temperatura["wysoka"] = fuzz.trapmf(
            temperatura.universe, [22, 30, 40, 40]
        )  # wysoka to 30+

        # WIATR: słaby, umiarkowany, silny, wichura
        wiatr["słaby"] = fuzz.trapmf(
            wiatr.universe, [0, 0, 1.6, 5.5]
        )  # 0-2, początek w 0, koniec cała 3.
        wiatr["umiarkowany"] = fuzz.trimf(
            wiatr.universe, [1.6, 4.5, 10.7]
        )  # 3-4, początek od całej 2 do końca całej 5
        wiatr["silny"] = fuzz.trimf(
            wiatr.universe, [5.5, 13.1, 20.7]
        )  # 5-7, początek od początku 4, koniec do końca 8
        # wiatr['wichura'] = fuzz.trimf(wiatr.universe, [13.9, 17.2, 25])
        wiatr["wichura"] = fuzz.trapmf(
            wiatr.universe, [10.8, 20.7, 25, 25]
        )  # 8+, początek od początku 6., środek w końcu 8, dalej bez końca

        # DESZCZ: lekki, umiarkowany, ulewny
        deszcz["lekki"] = fuzz.trapmf(deszcz.universe, [0, 0, 1.5, 3.5])
        deszcz["umiarkowany"] = fuzz.trimf(deszcz.universe, [1.5, 5.0, 8.5])
        deszcz["ulewny"] = fuzz.trapmf(deszcz.universe, [6.5, 8.5, 10, 10])

        # ZAGROŻENIE: niskie, średnie, wysokie
        zagrozenie["niskie"] = fuzz.trapmf(zagrozenie.universe, [0, 0, 25, 40])
        zagrozenie["średnie"] = fuzz.trimf(zagrozenie.universe, [25, 50, 75])
        zagrozenie["wysokie"] = fuzz.trapmf(zagrozenie.universe, [60, 75, 100, 100])

    @staticmethod
    def _define_rules(
        temperatura: Antecedent,
        wiatr: Antecedent,
        deszcz: Antecedent,
        zagrozenie: Consequent,
    ) -> list[Rule]:
        """Baza reguł."""
        rules = [
            # TEMPERATURA NISKA
            ctrl.Rule(
                temperatura["niska"] & wiatr["słaby"] & deszcz["lekki"],
                zagrozenie["niskie"],
            ),
            ctrl.Rule(
                temperatura["niska"] & wiatr["słaby"] & deszcz["umiarkowany"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["niska"] & wiatr["słaby"] & deszcz["ulewny"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["niska"] & wiatr["umiarkowany"] & deszcz["lekki"],
                zagrozenie["niskie"],
            ),
            ctrl.Rule(
                temperatura["niska"] & wiatr["umiarkowany"] & deszcz["umiarkowany"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["niska"] & wiatr["umiarkowany"] & deszcz["ulewny"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["niska"] & wiatr["silny"] & deszcz["lekki"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["niska"] & wiatr["silny"] & deszcz["umiarkowany"],
                zagrozenie["wysokie"],
            ),
            ctrl.Rule(
                temperatura["niska"] & wiatr["silny"] & deszcz["ulewny"],
                zagrozenie["wysokie"],
            ),
            ctrl.Rule(
                temperatura["niska"] & wiatr["wichura"] & deszcz["lekki"],
                zagrozenie["wysokie"],
            ),  #
            ctrl.Rule(
                temperatura["niska"] & wiatr["wichura"] & deszcz["umiarkowany"],
                zagrozenie["wysokie"],
            ),  #
            ctrl.Rule(
                temperatura["niska"] & wiatr["wichura"] & deszcz["ulewny"],
                zagrozenie["wysokie"],
            ),  #
            # TEMPERATURA UMIARKOWANA
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["słaby"] & deszcz["lekki"],
                zagrozenie["niskie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["słaby"] & deszcz["umiarkowany"],
                zagrozenie["niskie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["słaby"] & deszcz["ulewny"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["umiarkowany"] & deszcz["lekki"],
                zagrozenie["niskie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"]
                & wiatr["umiarkowany"]
                & deszcz["umiarkowany"],
                zagrozenie["niskie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["umiarkowany"] & deszcz["ulewny"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["silny"] & deszcz["lekki"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["silny"] & deszcz["umiarkowany"],
                zagrozenie["wysokie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["silny"] & deszcz["ulewny"],
                zagrozenie["wysokie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["wichura"] & deszcz["lekki"],
                zagrozenie["wysokie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["wichura"] & deszcz["umiarkowany"],
                zagrozenie["wysokie"],
            ),
            ctrl.Rule(
                temperatura["umiarkowana"] & wiatr["wichura"] & deszcz["ulewny"],
                zagrozenie["wysokie"],
            ),
            # TEMPERATURA WYSOKA
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["słaby"] & deszcz["lekki"],
                zagrozenie["wysokie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["słaby"] & deszcz["umiarkowany"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["słaby"] & deszcz["ulewny"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["umiarkowany"] & deszcz["lekki"],
                zagrozenie["wysokie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["umiarkowany"] & deszcz["umiarkowany"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["umiarkowany"] & deszcz["ulewny"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["silny"] & deszcz["lekki"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["silny"] & deszcz["umiarkowany"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["silny"] & deszcz["ulewny"],
                zagrozenie["średnie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["wichura"] & deszcz["lekki"],
                zagrozenie["wysokie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["wichura"] & deszcz["umiarkowany"],
                zagrozenie["wysokie"],
            ),
            ctrl.Rule(
                temperatura["wysoka"] & wiatr["wichura"] & deszcz["ulewny"],
                zagrozenie["wysokie"],
            ),
        ]

        return rules

    @staticmethod
    def _apply_binary_effects(risk_value: float, weather_code: int) -> float:
        """
        Podbija wynik o określony procent jeśli występuje burza.
        """
        if weather_code in THUNDER_WEATHER_CODES:
            risk_value += THUNDER_PENALTY

        return min(risk_value, 100)

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

    def interpret_temperature(self, value: float) -> str:
        return self._interpret(
            variable=self.temperatura,
            labels=["niska", "umiarkowana", "wysoka"],
            value=value,
        )

    def interpret_wind(self, value: float) -> str:
        return self._interpret(
            variable=self.wiatr,
            labels=["słaby", "umiarkowany", "silny", "wichura"],
            value=value,
        )

    def interpret_rain(self, value: float) -> str:
        """
        UWAGA:
        W razie braku deszczu dodawana jest dodatkowa etykieta - 'brak',
        której nie wykorzystuje się do obliczeń w systemie logiki.
        """
        if value == 0.0:
            return "brak"
        return self._interpret(
            variable=self.deszcz,
            labels=["lekki", "umiarkowany", "ulewny"],
            value=value,
        )

    def interpret_risk(self, value: float) -> str:
        return self._interpret(
            variable=self.zagrozenie,
            labels=["niskie", "średnie", "wysokie"],
            value=value,
        )

    def interpret_weather_code(self, code: int) -> str:
        return "tak" if int(code) in THUNDER_WEATHER_CODES else "nie"

    def assess_risk(
        self,
        temperatura: float,
        wiatr: float,
        deszcz: float,
        weather_code: int,
        visualize=False,
    ) -> tuple[float, float]:
        """
        Oblicza ryzyko na podstawie wartości wejściowych oraz flagi burzy.
        Zwraca krotkę (fuzzy_risk, final_risk).
        """
        sim = ctrl.ControlSystemSimulation(self.system)

        sim.input["temperatura"] = float(temperatura)
        sim.input["wiatr"] = float(wiatr)
        sim.input["deszcz"] = float(deszcz)

        sim.compute()

        fuzzy_risk = float(sim.output["zagrozenie"])

        final_risk = self._apply_binary_effects(fuzzy_risk, weather_code)

        if visualize:
            print("=== WIZUALIZACJA WNIOSKOWANIA ===")
            print(f"Temperatura: {temperatura}")
            print(f"Wiatr: {wiatr}")
            print(f"Deszcz: {deszcz}")
            print(f"Zagrożenie (fuzzy): {fuzzy_risk:.2f}")
            print(f"Zagrożenie (final): {final_risk:.2f}")

            # Wykresy aktywacji zmiennych wejściowych
            self.temperatura.view(sim=sim)
            self.wiatr.view(sim=sim)
            self.deszcz.view(sim=sim)

            # Wykres zmiennej wyjściowej z zaznaczonym wynikiem
            self.zagrozenie.view(sim=sim)

            plt.show()

        return fuzzy_risk, final_risk

    def assess_risk_forecast_df(self, forecast_df: pd.DataFrame) -> pd.DataFrame:
        """
        Oblicza poziom zagrożenia dla prognozy godzinowej
        i dodaje interpretacje lingwistyczne.
        """

        results = []

        for _, row in forecast_df.iterrows():

            fuzzy_risk, final_risk = self.assess_risk(
                temperatura=row["temperature_2m"],
                wiatr=row["wind_speed_10m"],
                deszcz=row["rain"],
                weather_code=row["weather_code"],
            )

            results.append(
                {
                    "date": row["date"],
                    "fuzzy_risk": fuzzy_risk,
                    "final_risk": final_risk,
                    "temperature_linguistic": self.interpret_temperature(
                        row["temperature_2m"]
                    ),
                    "wind_linguistic": self.interpret_wind(row["wind_speed_10m"]),
                    "rain_linguistic": self.interpret_rain(row["rain"]),
                    "thunder_linguistic": self.interpret_weather_code(
                        row["weather_code"]
                    ),
                    "risk_linguistic": self.interpret_risk(final_risk),
                }
            )

        return pd.DataFrame(results)
