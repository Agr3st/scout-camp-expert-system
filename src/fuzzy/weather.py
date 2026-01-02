import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from src.fuzzy.visualizations import plot_heatmap_slice
import pandas as pd
from datetime import datetime, timedelta, timezone


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
    def _create_variables():
        """Definicja zmiennych wejściowych i wyjściowych"""
        temperatura = ctrl.Antecedent(np.arange(0, 41, 1), "temperatura")
        wiatr = ctrl.Antecedent(np.arange(0, 25, 0.1), "wiatr")
        deszcz = ctrl.Antecedent(np.arange(0, 10, 0.1), "deszcz")

        # zmienna wyjsciowa
        zagrozenie = ctrl.Consequent(np.arange(0, 101, 1), "zagrozenie")

        return temperatura, wiatr, deszcz, zagrozenie

    @staticmethod
    def _set_membership_functions(temperatura, wiatr, deszcz, zagrozenie):
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
        # https://pl.wikipedia.org/wiki/Skala_Beauforta
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
        # https://pl.wikipedia.org/wiki/Deszcz
        deszcz["lekki"] = fuzz.trapmf(deszcz.universe, [0, 0, 1.5, 3.5])
        deszcz["umiarkowany"] = fuzz.trimf(deszcz.universe, [1.5, 5.0, 8.5])
        deszcz["ulewny"] = fuzz.trapmf(deszcz.universe, [6.5, 8.5, 10, 10])

        # ZAGROŻENIE: niskie, średnie, wysokie
        zagrozenie["niskie"] = fuzz.trapmf(zagrozenie.universe, [0, 0, 25, 40])
        zagrozenie["średnie"] = fuzz.trimf(zagrozenie.universe, [25, 50, 75])
        zagrozenie["wysokie"] = fuzz.trapmf(zagrozenie.universe, [60, 75, 100, 100])

    @staticmethod
    def _define_rules(temperatura, wiatr, deszcz, zagrozenie):
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

    def assess_risk(
        self, temperatura, wiatr, deszcz, weather_code
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

        return fuzzy_risk, final_risk

    def assess_risk_forecast_df(self, forecast_df: pd.DataFrame) -> pd.DataFrame:
        """
        Oblicza poziom zagrożenia dla prognozy godzinowej.

        Parametry:
            forecast_df (pd.DataFrame): DataFrame z kolumnami:
                - date
                - temperature_2m
                - weather_code
                - wind_speed_10m
                - rain

        Zwraca:
            pd.DataFrame z kolumnami:
                - date
                - fuzzy_risk
                - final_risk
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
                }
            )

        return pd.DataFrame(results)

    def assess_risk_next_hour(self, forecast_df: pd.DataFrame) -> dict:
        """
        Określa poziom zagrożenia dla najbliższej godziny od momentu wywołania.

        Parametry:
            forecast_df (pd.DataFrame): DataFrame z kolumnami:
                - date
                - temperature_2m
                - weather_code
                - wind_speed_10m
                - rain

        Zwraca:
            dict z kluczami:
                - target_time
                - fuzzy_risk
                - final_risk
        """

        now = datetime.now(timezone.utc)
        target_time = now + timedelta(hours=1)

        df = forecast_df.copy()
        # df["date"] = pd.to_datetime(df["date"])

        df["time_diff"] = (df["date"] - target_time).abs()
        row = df.loc[df["time_diff"].idxmin()]

        fuzzy_risk, final_risk = self.assess_risk(
            temperatura=row["temperature_2m"],
            wiatr=row["wind_speed_10m"],
            deszcz=row["rain"],
            weather_code=row["weather_code"],
        )

        return {
            "target_time": row["date"],
            "fuzzy_risk": fuzzy_risk,
            "final_risk": final_risk,
        }


if __name__ == "__main__":

    weather = WeatherLogicSystem()

    # ---- wizualizacja zmiennych ----
    # plot_membership_function(weather.temperatura, "temperatura.png")
    # plot_membership_function(weather.wiatr, "wiatr.png")
    # plot_membership_function(weather.deszcz, "deszcz.png")
    # plot_membership_function(weather.zagrozenie, "zagrozenie.png")

    try:

        # --- WIZUALIZACJA PEŁNEJ BAZY REGUŁ (TRZY ZESTAWY HEATMAP) ---

        print("\n--- ZESTAW 1: Wiatr vs. Temperatura (przy stałym Deszczu) ---")
        plot_heatmap_slice(
            weather.system,
            var_x_name="wiatr",
            var_y_name="temperatura",
            var_fixed_name="deszcz",
            fixed_values=[0.0, 5.0, 15.0],
            step_x=1.0,
            step_y=5.0,
            filename="wiatr_vs_temperatura_staly_deszcz.png",
        )

        """
        print("\n--- ZESTAW 2: Deszcz vs. Temperatura (przy stałym Wietrze) ---")
        plot_heatmap_slice(weather.system, 
                           var_x_name='deszcz', 
                           var_y_name='temperatura', 
                           var_fixed_name='wiatr', 
                           fixed_values=[1.0, 5.0, 14.0, 22.0], 
                           step_x=0.5, 
                           step_y=5.0,
                           filename="deszcz_vs_temperatura_staly_wiatr.png",)
        
        """
        """
        print("\n--- ZESTAW 3: Deszcz vs. Wiatr (przy stałej Temperaturze) ---")
        # Deszcz i Wiatr muszą mieć mały krok, Temp ustalamy na dwóch wartościach
        plot_heatmap_slice(weather.system, 
                           var_x_name='deszcz', 
                           var_y_name='wiatr', 
                           var_fixed_name='temperatura', 
                           fixed_values=[8.0, 22.0, 32.0], # Temperatura = {niska, średnia, wysoka}
                           step_x=0.5, 
                           step_y=1,
                            filename="deszcz_vs_wiatr_stala_temperatura.png",)
        """

    except Exception as e:
        print(e)
