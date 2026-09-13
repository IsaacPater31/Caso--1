import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


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
        label = f"{ar.rule.id}: {ar.consequent_mf.name} (α={ar.firing_strength:.4f})"
        ax.fill_between(y, 0, mu, alpha=0.2, label=label)
        ax.plot(y, mu, linewidth=1.2)
    method = inference_result.inference_method.capitalize()
    ax.set_title(f'Conjuntos implicados — {method}', fontsize=10, fontweight='bold')
    ax.set_xlabel('Alerta de Emergencia (%)')
    ax.set_ylabel('μ')
    ax.set_ylim(-0.05, 1.1)
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3)


def plot_aggregation(ax, inference_result, defuzz_values=None):
    y = inference_result.y_universe
    mu = inference_result.mu_aggregated
    ax.fill_between(y, 0, mu, alpha=0.3, color='steelblue', label='Agregación')
    ax.plot(y, mu, color='steelblue', linewidth=1.5)

    styles = {
        'centroide':       ('red',   '--', 'Centroide'),
        'centro_maximos':  ('green', ':',  'Centro de Máximos'),
    }
    if defuzz_values:
        for key, val in defuzz_values.items():
            if not np.isnan(val):
                color, ls, label = styles.get(key, ('gray', '--', key))
                ax.axvline(val, color=color, linestyle=ls, linewidth=2,
                           label=f'{label} = {val:.2f}%')

    method = inference_result.inference_method.capitalize()
    ax.set_title(f'Agregación y Desfusificación — {method}', fontsize=10, fontweight='bold')
    ax.set_xlabel('Alerta de Emergencia (%)')
    ax.set_ylabel('μ')
    ax.set_ylim(-0.05, 1.1)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)


def plot_full_report(inference_result, defuzz_values, input_variables, output_variable):
    method = inference_result.inference_method.capitalize()
    
    fig = plt.figure(figsize=(15, 8))
    fig.suptitle(f'Dashboard de Inferencia Difusa — Método: {method}',
                 fontsize=14, fontweight='bold')

    gs = GridSpec(2, 3, figure=fig, width_ratios=[1, 1, 0.75], hspace=0.35, wspace=0.25)

    # Fila 0: Funciones de membresia de entrada
    for i, var in enumerate(input_variables):
        ax = fig.add_subplot(gs[0, i])
        fuzz = inference_result.fuzzified.get(var.name)
        crisp = inference_result.crisp_inputs.get(var.name)
        plot_variable(ax, var, crisp, fuzz)

    # Fila 1: Reglas activadas y Desfusificacion
    plot_implied_sets(fig.add_subplot(gs[1, 0]), inference_result)
    plot_aggregation(fig.add_subplot(gs[1, 1]), inference_result, defuzz_values)

    # Columna Derecha (Span vertical): Panel de Texto Analitico
    ax_text = fig.add_subplot(gs[:, 2])
    ax_text.axis('off')
    
    txt = "REPORTE ANALITICO\n"
    txt += "="*30 + "\n\n"
    
    txt += "▶ ENTRADAS:\n"
    for k, v in inference_result.crisp_inputs.items():
        txt += f"  • {k}: {v}\n"
    
    txt += "\n▶ FUSIFICACION (Activas):\n"
    for var_name, terms in inference_result.fuzzified.items():
        active = {t: d for t, d in terms.items() if d > 0}
        for t, d in active.items():
            txt += f"  • {var_name} [{t}]: {d:.4f}\n"
            
    txt += "\n▶ REGLAS DISPARADAS:\n"
    if not inference_result.activated_rules:
        txt += "  (Ninguna regla)\n"
    else:
        for ar in inference_result.activated_rules:
            txt += f"  • {ar.rule.id} -> {ar.consequent_mf.name} (α={ar.firing_strength:.3f})\n"
            
    txt += "\n▶ RESULTADO DESFUSIFICADO:\n"
    c = defuzz_values.get('centroide', float('nan'))
    m = defuzz_values.get('centro_maximos', float('nan'))
    txt += f"  • Centroide:      {c:.2f} %\n"
    txt += f"  • Centro Maximos: {m:.2f} %\n"

    bbox_props = dict(boxstyle="square,pad=1.2", fc="#f8f9fa", ec="#dee2e6", lw=1.5)
    ax_text.text(0.05, 0.95, txt, fontsize=10, family='monospace',
                 verticalalignment='top', bbox=bbox_props, linespacing=1.6)

    fig.subplots_adjust(top=0.90, bottom=0.1, left=0.05, right=0.98)
    return fig

