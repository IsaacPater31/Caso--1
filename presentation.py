import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import RadioButtons


def plot_variable(ax, variable, crisp_value=None, fuzzified=None):
    x = np.linspace(*variable.universe, 500)
    for term_name, mf in variable.terms.items():
        y = mf(x)
        line, = ax.plot(x, y, label=term_name, linewidth=1.5)
        if fuzzified and fuzzified.get(term_name, 0) > 0:
            degree = fuzzified[term_name]
            y_cap = np.minimum(y, degree)
            ax.fill_between(x, 0, y_cap, alpha=0.12, color=line.get_color())
            ax.plot(crisp_value, degree, 'o', color=line.get_color(), markersize=5, zorder=5)
            ax.plot([variable.universe[0], crisp_value], [degree, degree],
                    '--', color=line.get_color(), alpha=0.5, linewidth=0.8)
    if crisp_value is not None:
        ax.axvline(crisp_value, color='k', linestyle='--', linewidth=1,
                   alpha=0.7, label=f'x = {crisp_value}')
    ax.set_title(variable.name, fontsize=10, fontweight='bold')
    ax.set_ylabel('μ')
    ax.set_ylim(-0.05, 1.1)
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3)


def plot_implied_sets(ax, inference_result):
    y = inference_result.y_universe
    for ar, mu in inference_result.implied_sets:
        label = f"{ar.rule.id}: {ar.consequent_mf.name} (α={ar.firing_strength:.3f})"
        ax.fill_between(y, 0, mu, alpha=0.2, label=label)
        ax.plot(y, mu, linewidth=1.2)
    method = inference_result.inference_method.capitalize()
    ax.set_title(f'Conjuntos Implicados — {method}', fontsize=10, fontweight='bold')
    ax.set_xlabel('Alerta de Emergencia (%)')
    ax.set_ylabel('μ')
    ax.set_ylim(-0.05, 1.1)
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3)


_DEFUZZ_STYLES = {
    'centroide':      ('red',   '--', 'Centroide'),
    'centro_maximos': ('green', ':',  'Centro de Máximos'),
}


def plot_aggregation(ax, inference_result, defuzz_values=None):
    y = inference_result.y_universe
    mu = inference_result.mu_aggregated
    ax.fill_between(y, 0, mu, alpha=0.3, color='steelblue', label='Agregación')
    ax.plot(y, mu, color='steelblue', linewidth=1.5)

    if defuzz_values:
        for key, val in defuzz_values.items():
            if not np.isnan(val):
                color, ls, label = _DEFUZZ_STYLES.get(key, ('gray', '--', key))
                ax.axvline(val, color=color, linestyle=ls, linewidth=2,
                           label=f'{label} = {val:.2f}%')

    method = inference_result.inference_method.capitalize()
    ax.set_title(f'Agregación y Desfusificación — {method}', fontsize=10, fontweight='bold')
    ax.set_xlabel('Alerta de Emergencia (%)')
    ax.set_ylabel('μ')
    ax.set_ylim(-0.05, 1.1)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)


def _build_report_text(inference_result, defuzz_values):
    c = defuzz_values.get('centroide', float('nan'))
    m = defuzz_values.get('centro_maximos', float('nan'))
    method = inference_result.inference_method.capitalize()

    lines = [
        f"MÉTODO: {method.upper()}",
        "=" * 28,
        "",
        "▶ ENTRADAS:",
    ]
    for key, value in inference_result.crisp_inputs.items():
        lines.append(f"  {key}: {value}")

    lines += ["", "▶ FUSIFICACIÓN (Activas):"]
    for terms in inference_result.fuzzified.values():
        for term, degree in terms.items():
            if degree > 0:
                lines.append(f"  [{term}]: {degree:.4f}")

    lines += ["", "▶ REGLAS DISPARADAS:"]
    if not inference_result.activated_rules:
        lines.append("  (Ninguna regla)")
    else:
        for activated_rule in inference_result.activated_rules:
            lines.append(f"  {activated_rule.rule.id} -> "
                         f"{activated_rule.consequent_mf.name} "
                         f"(α={activated_rule.firing_strength:.3f})")

    lines += [
        "",
        "▶ DESFUSIFICACIÓN:",
        f"  Centroide:      {c:.2f} %",
        f"  Centro Máximos: {m:.2f} %",
    ]
    return "\n".join(lines)


def build_dashboard(all_results, input_variables):
    methods = list(all_results.keys())

    fig = plt.figure(figsize=(16, 8))
    fig.suptitle(
        'Sistema de Alerta Temprana — Canal del Dique\n'
        'Inferencia Difusa (Mamdani / Larsen)',
        fontsize=13, fontweight='bold'
    )

    grid = GridSpec(2, 3, figure=fig,
                    width_ratios=[1, 1, 0.75],
                    hspace=0.38, wspace=0.28,
                    left=0.05, right=0.98, top=0.88, bottom=0.08)

    first_result = all_results[methods[0]][0]
    ax_x1 = fig.add_subplot(grid[0, 0])
    ax_x2 = fig.add_subplot(grid[0, 1])
    plot_variable(ax_x1, input_variables[0],
                  crisp_value=first_result.crisp_inputs.get(input_variables[0].name),
                  fuzzified=first_result.fuzzified.get(input_variables[0].name))
    plot_variable(ax_x2, input_variables[1],
                  crisp_value=first_result.crisp_inputs.get(input_variables[1].name),
                  fuzzified=first_result.fuzzified.get(input_variables[1].name))

    ax_impl = fig.add_subplot(grid[1, 0])
    ax_agg = fig.add_subplot(grid[1, 1])

    grid_right = grid[:, 2].subgridspec(2, 1, height_ratios=[0.20, 0.80], hspace=0.18)
    ax_radio = fig.add_subplot(grid_right[0])
    ax_text = fig.add_subplot(grid_right[1])

    ax_radio.set_facecolor('#f0f4f8')
    radio = RadioButtons(ax_radio, labels=[method.capitalize() for method in methods],
                         active=0, activecolor='steelblue')
    ax_radio.set_title('Método de Inferencia', fontsize=9, fontweight='bold', pad=4)

    ax_text.axis('off')
    bbox_props = dict(boxstyle="square,pad=0.8", fc="#f8f9fa", ec="#dee2e6", lw=1.2)
    text_artist = ax_text.text(
        0.02, 0.98,
        _build_report_text(*all_results[methods[0]]),
        fontsize=9, family='monospace',
        verticalalignment='top', bbox=bbox_props, linespacing=1.55,
        transform=ax_text.transAxes,
    )

    def redraw(method_label):
        method_key = method_label.lower()
        result, defuzz = all_results[method_key]
        ax_impl.cla()
        ax_agg.cla()
        plot_implied_sets(ax_impl, result)
        plot_aggregation(ax_agg, result, defuzz)
        text_artist.set_text(_build_report_text(result, defuzz))
        fig.canvas.draw_idle()

    radio.on_clicked(redraw)
    fig._radio = radio
    redraw(methods[0].capitalize())

    return fig


def get_inputs():
    if len(sys.argv) >= 3:
        try:
            return float(sys.argv[1]), float(sys.argv[2])
        except ValueError:
            print("  [ERROR] Los parametros por linea de comandos no son numeros validos.")
            print("  Iniciando modo interactivo...\n")

    print("\n" + "=" * 62)
    print("  INGRESO DE SENSORES - SISTEMA ALERTA TEMPRANA")
    print("=" * 62)
    print("  Ingrese las mediciones usando punto para los decimales.\n")

    x1 = _get_float_input("  > Nivel del Rio (rango 0-10) [m]: ", 0.0, 10.0)
    x2 = _get_float_input("  > Precipitacion Acumulada (rango 0-200) [mm/24h]: ", 0.0, 200.0)
    return x1, x2


def _get_float_input(prompt, min_val, max_val):
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                print("  [ERROR] La entrada no puede estar vacia. Intente de nuevo.")
                continue
            val = float(user_input)
            if val < min_val or val > max_val:
                print(f"  [ALERTA] Valor {val} fuera del rango tipico [{min_val} a {max_val}]. El sistema usara la condicion extrema.")
            return val
        except ValueError:
            print("  [ERROR] Entrada invalida. Ingrese solo numeros (ej. 7.3). Intente de nuevo.")

