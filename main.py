import sys
import io
import matplotlib.pyplot as plt

from fuzzy_flood_alert.variables import INPUT_VARIABLES, OUTPUT_VARIABLE
from fuzzy_flood_alert.rules import RULES
from fuzzy_flood_alert.engine import run_inference
from fuzzy_flood_alert.defuzzification import centroid, center_of_maxima
from fuzzy_flood_alert.plotting import plot_full_report

# Windows cp1252 console can't print box-drawing chars; force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def _get_inputs():
    if len(sys.argv) >= 3:
        return float(sys.argv[1]), float(sys.argv[2])
    x1 = float(input("Nivel del Rio [0-10] (m): "))
    x2 = float(input("Precipitacion Acumulada [0-200] (mm/24h): "))
    return x1, x2


def _print_header(x1, x2):
    print(f"\n{'=' * 62}")
    print(f"  Sistema de Alerta Temprana por Inundacion - Canal del Dique")
    print(f"  Nivel del Rio = {x1} m  |  Precipitacion = {x2} mm/24h")
    print(f"{'=' * 62}")


def _print_fuzzification(fuzzified):
    print("\n-- Fusificacion -----------------------------")
    for var_name, terms in fuzzified.items():
        active = {t: d for t, d in terms.items() if d > 0}
        print(f"  {var_name}:")
        if not active:
            print("    (ningun termino activado)")
        for term, degree in active.items():
            print(f"    mu_{term} = {degree:.4f}")


def _print_rules(activated_rules):
    print("\n-- Reglas Activadas -------------------------")
    if not activated_rules:
        print("  (ninguna regla activada)")
        return
    for ar in activated_rules:
        ants = ' '.join(f"({v}: {t})" for v, t in ar.rule.antecedents)
        op = f" [{ar.rule.operator.value}] " if ar.rule.operator else " "
        print(f"  {ar.rule.id}: {ants}{op}-> {ar.consequent_mf.name}"
              f"  [alpha = {ar.firing_strength:.4f}]")


def _print_summary_table(all_results):
    print(f"\n{'=' * 62}")
    print(f"  {'Metodo':<20} {'Centroide':>15} {'Centro Maximos':>18}")
    print(f"  {'-' * 56}")
    for method, (_, defuzz) in all_results.items():
        c = defuzz['centroide']
        m = defuzz['centro_maximos']
        print(f"  {method.capitalize():<20} {c:>14.4f}% {m:>17.4f}%")
    print(f"{'=' * 62}\n")


def main():
    x1, x2 = _get_inputs()
    crisp_inputs = {
        INPUT_VARIABLES[0].name: x1,
        INPUT_VARIABLES[1].name: x2,
    }

    _print_header(x1, x2)

    all_results = {}
    for method in ('mamdani', 'larsen'):
        result = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES,
                               crisp_inputs, method)
        c = centroid(result.y_universe, result.mu_aggregated)
        m = center_of_maxima(result.y_universe, result.mu_aggregated)
        defuzz = {'centroide': c, 'centro_maximos': m}
        all_results[method] = (result, defuzz)

        print(f"\n{'-' * 62}")
        print(f"  METODO: {method.upper()}")
        print(f"{'-' * 62}")
        _print_fuzzification(result.fuzzified)
        _print_rules(result.activated_rules)
        print(f"\n  > Centroide       = {c:.4f}%")
        print(f"  > Centro Maximos  = {m:.4f}%")

    _print_summary_table(all_results)

    for method, (result, defuzz) in all_results.items():
        plot_full_report(result, defuzz, INPUT_VARIABLES, OUTPUT_VARIABLE)
    plt.show()


if __name__ == '__main__':
    main()
