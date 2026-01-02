import matplotlib
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np

UNIT_MAP = {"temperatura": "[°C]", "deszcz": "[mm/h]", "wiatr": "[m/s]"}


def plot_membership_function(variable, filename=None):
    """
    Wizualizuje i (opcjonalnie) zapisuje wykres funkcji przynależności danej zmiennej.
    variable: zmienna logiczna
    filename: nazwa pliku, zapisywany do katalogu `plots/`
    """
    matplotlib.use("Agg")  # non-interactive, temporally
    variable.view()

    ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()

    if ax.get_legend() is not None:
        ax.get_legend().remove()

    ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=len(labels),
        frameon=False,
        fontsize=10,
    )

    plt.ylabel("Przynależność")
    plt.tight_layout()
    plt.show()
    if filename:
        plt.savefig(f"plots/{filename}", dpi=200)
        print(f"Zapisano wykres w: plots/{filename}")
    plt.close()


def plot_heatmap_slice(
    system,
    var_x_name,
    var_y_name,
    var_fixed_name,
    fixed_values,
    step_x=1.0,
    step_y=1.0,
    filename=None,
):
    """
    Tworzy serię map cieplnych dla dwóch zmiennych (X, Y) przy stałych wartościach trzeciej (Fixed).
    Opcjonalnie zapisuje figurę do katalogu plots pod nazwą filename.
    """
    matplotlib.use("Agg")  # non-interactive, temporally
    sim = ctrl.ControlSystemSimulation(system)

    all_antecedents = {a.label: a for a in sim.ctrl.antecedents}

    var_x = all_antecedents[var_x_name]
    var_y = all_antecedents[var_y_name]

    x_range = np.arange(var_x.universe.min(), var_x.universe.max() + step_x, step_x)
    y_range = np.arange(var_y.universe.min(), var_y.universe.max() + step_y, step_y)

    if len(x_range) == 0 or len(y_range) == 0:
        print(
            f"Błąd: Zakresy dla {var_x_name} lub {var_y_name} są puste po dyskretyzacji."
        )
        return

    max_risk = 100
    num_plots = len(fixed_values)

    fig, axes = plt.subplots(1, num_plots, figsize=(6 * num_plots, 6), sharey=True)
    if num_plots == 1:
        axes = [axes]

    print(
        f"\nGenerowanie Heatmap: {var_x_name} (X) x {var_y_name} (Y) | Stały {var_fixed_name}..."
    )

    # Używamy itertools.product, aby stworzyć listę wszystkich kombinacji (w, t)
    # i owijamy ją w tqdm dla paska postępu

    final_im = None

    for k, fixed_val in enumerate(fixed_values):
        Z = np.zeros((len(y_range), len(x_range)), dtype=float)

        # Tworzymy listę wszystkich indeksów (i, j) i iterujemy przez nią z tqdm
        # total_iterations = len(y_range) * len(x_range)

        # Używamy enumerate na y_range i x_range, aby uzyskać indeksy macierzy Z

        # Tworzymy generator wszystkich par (indeks_y, indeks_x) i owijamy go w tqdm
        # Pasek postępu będzie wyświetlał nazwę stałej zmiennej
        progress_bar_label = f"Obliczanie dla {var_fixed_name}: {fixed_val:.1f} {UNIT_MAP.get(var_fixed_name, '')}"

        for i, y_val in tqdm(
            enumerate(y_range), total=len(y_range), desc=progress_bar_label, leave=False
        ):
            for j, x_val in enumerate(x_range):
                sim.input[var_x_name] = x_val
                sim.input[var_y_name] = y_val
                sim.input[var_fixed_name] = fixed_val

                try:
                    sim.compute()
                    Z[i, j] = sim.output["zagrozenie"]
                except Exception:
                    Z[i, j] = 0.0

        im = axes[k].imshow(
            Z,
            extent=[x_range.min(), x_range.max(), y_range.min(), y_range.max()],
            origin="lower",
            aspect="auto",
            cmap="jet",
            vmin=0,
            vmax=max_risk,
        )
        final_im = im

        axes[k].set_title(
            f'{var_fixed_name.capitalize()}: {fixed_val:.1f} {UNIT_MAP.get(var_fixed_name, "")}'
        )
        axes[k].set_xlabel(f'{var_x_name.capitalize()} {UNIT_MAP.get(var_x_name, "")}')

        if k == 0:
            axes[k].set_ylabel(
                f'{var_y_name.capitalize()} {UNIT_MAP.get(var_y_name, "")}'
            )

    fig.colorbar(
        final_im,
        ax=axes.ravel().tolist(),
        orientation="horizontal",
        shrink=0.6,
        pad=0.15,
        label="Poziom Zagrożenia (0-100)",
    )

    fig.suptitle(
        f"Wizualizacja Bazy Reguł: {var_x_name.capitalize()} vs. {var_y_name.capitalize()}",
        fontsize=14,
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.35)

    plt.show()
    if filename:
        plt.savefig(f"plots/{filename}", dpi=200)
        print(f"Zapisano wykres w: plots/{filename}")
    plt.close()
