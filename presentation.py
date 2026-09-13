import sys
import io


def _fix_stdout_encoding():
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def print_header(x1, x2):
    print(f"\n{'=' * 62}")
    print("  Sistema de Alerta Temprana por Inundacion - Canal del Dique")
    print(f"  Nivel del Rio = {x1} m  |  Precipitacion = {x2} mm/24h")
    print(f"{'=' * 62}")


def print_fuzzification(fuzzified):
    print("\n-- Fusificacion -----------------------------")
    for var_name, terms in fuzzified.items():
        active = {t: d for t, d in terms.items() if d > 0}
        print(f"  {var_name}:")
        if not active:
            print("    (ningun termino activado)")
        for term, degree in active.items():
            print(f"    mu_{term} = {degree:.4f}")


def print_rules(activated_rules):
    print("\n-- Reglas Activadas -------------------------")
    if not activated_rules:
        print("  (ninguna regla activada)")
        return
    for ar in activated_rules:
        ants = ' '.join(f"({v}: {t})" for v, t in ar.rule.antecedents)
        op = f" [{ar.rule.operator.value}] " if ar.rule.operator else " "
        print(f"  {ar.rule.id}: {ants}{op}-> {ar.consequent_mf.name}"
              f"  [alpha = {ar.firing_strength:.4f}]")


def print_method_results(method, result, c, m):
    print(f"\n{'-' * 62}")
    print(f"  METODO: {method.upper()}")
    print(f"{'-' * 62}")
    print_fuzzification(result.fuzzified)
    print_rules(result.activated_rules)
    print(f"\n  > Centroide       = {c:.4f}%")
    print(f"  > Centro Maximos  = {m:.4f}%")


def print_summary_table(all_results):
    print(f"\n{'=' * 62}")
    print(f"  {'Metodo':<20} {'Centroide':>15} {'Centro Maximos':>18}")
    print(f"  {'-' * 56}")
    for method, (_, defuzz) in all_results.items():
        c = defuzz['centroide']
        m = defuzz['centro_maximos']
        print(f"  {method.capitalize():<20} {c:>14.4f}% {m:>17.4f}%")
    print(f"{'=' * 62}\n")


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

