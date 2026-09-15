import matplotlib.pyplot as plt

from variables import INPUT_VARIABLES, OUTPUT_VARIABLE
from rules import RULES
from engine import run_inference
from defuzzification import centroid, center_of_maxima
from presentation import build_dashboard, get_inputs


def main():
    x1, x2 = get_inputs()
    crisp_inputs = {
        INPUT_VARIABLES[0].name: x1,
        INPUT_VARIABLES[1].name: x2,
    }

    all_results = {}
    for method in ('mamdani', 'larsen'):
        result = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp_inputs, method)
        c = centroid(result.y_universe, result.mu_aggregated)
        m = center_of_maxima(result.y_universe, result.mu_aggregated)
        defuzz = {'centroide': c, 'centro_maximos': m}
        all_results[method] = (result, defuzz)

    fig = build_dashboard(all_results, INPUT_VARIABLES)
    plt.show()


if __name__ == '__main__':
    main()
