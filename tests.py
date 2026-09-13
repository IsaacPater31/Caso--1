"""
Test suite exhaustivo para el Sistema de Alerta Temprana por Inundacion.
Cubre: membership, variables, rules, engine, defuzzification.
"""
import sys
import math
import numpy as np

sys.path.insert(0, '.')

from fuzzy_flood_alert.membership import trapezoidal, MembershipFunction, LinguisticVariable
from fuzzy_flood_alert.variables import (
    NIVEL_RIO, PRECIPITACION, ALERTA, INPUT_VARIABLES, OUTPUT_VARIABLE
)
from fuzzy_flood_alert.rules import RULES, Operator, FuzzyRule
from fuzzy_flood_alert.engine import (
    fuzzify, run_inference, ActivatedRule, InferenceResult
)
from fuzzy_flood_alert.defuzzification import centroid, center_of_maxima

PASS = 0
FAIL = 0


def check(condition, label):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label}")


def approx(a, b, tol=1e-6):
    if math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) < tol


# ================================================================
#  1. MEMBERSHIP FUNCTIONS — trapezoidal primitive
# ================================================================
def test_trapezoidal_scalar():
    print("\n=== 1. Trapezoidal — scalar I/O ===")
    # Standard trapezoid (1, 3, 5, 7)
    check(approx(trapezoidal(0, 1, 3, 5, 7), 0.0),   "x<a -> 0")
    check(approx(trapezoidal(1, 1, 3, 5, 7), 0.0),    "x=a -> 0")
    check(approx(trapezoidal(2, 1, 3, 5, 7), 0.5),    "rising midpoint -> 0.5")
    check(approx(trapezoidal(3, 1, 3, 5, 7), 1.0),    "x=b -> 1")
    check(approx(trapezoidal(4, 1, 3, 5, 7), 1.0),    "flat top -> 1")
    check(approx(trapezoidal(5, 1, 3, 5, 7), 1.0),    "x=c -> 1")
    check(approx(trapezoidal(6, 1, 3, 5, 7), 0.5),    "falling midpoint -> 0.5")
    check(approx(trapezoidal(7, 1, 3, 5, 7), 0.0),    "x=d -> 0")
    check(approx(trapezoidal(8, 1, 3, 5, 7), 0.0),    "x>d -> 0")
    # Returns float for scalar input
    check(isinstance(trapezoidal(4, 1, 3, 5, 7), float), "scalar -> float")


def test_trapezoidal_array():
    print("\n=== 2. Trapezoidal — array I/O ===")
    x = np.array([0, 2, 4, 6, 8])
    y = trapezoidal(x, 1, 3, 5, 7)
    check(isinstance(y, np.ndarray), "array -> ndarray")
    check(y.shape == (5,), "shape preserved")
    expected = [0.0, 0.5, 1.0, 0.5, 0.0]
    check(np.allclose(y, expected), "values match expected")


def test_trapezoidal_left_shoulder():
    print("\n=== 3. Trapezoidal — left shoulder ===")
    INF = float('inf')
    # Bajo: (-inf, -inf, 2, 4)
    check(approx(trapezoidal(0, -INF, -INF, 2, 4), 1.0),   "x=0 -> 1 (flat)")
    check(approx(trapezoidal(2, -INF, -INF, 2, 4), 1.0),   "x=c=2 -> 1")
    check(approx(trapezoidal(3, -INF, -INF, 2, 4), 0.5),   "x=3 -> 0.5 (falling)")
    check(approx(trapezoidal(4, -INF, -INF, 2, 4), 0.0),   "x=d=4 -> 0")
    check(approx(trapezoidal(5, -INF, -INF, 2, 4), 0.0),   "x>d -> 0")


def test_trapezoidal_right_shoulder():
    print("\n=== 4. Trapezoidal — right shoulder ===")
    INF = float('inf')
    # Critico: (8, 10, inf, inf)
    check(approx(trapezoidal(7, 8, 10, INF, INF), 0.0),   "x<a -> 0")
    check(approx(trapezoidal(8, 8, 10, INF, INF), 0.0),    "x=a -> 0")
    check(approx(trapezoidal(9, 8, 10, INF, INF), 0.5),    "rising midpoint -> 0.5")
    check(approx(trapezoidal(10, 8, 10, INF, INF), 1.0),   "x=b -> 1")
    check(approx(trapezoidal(100, 8, 10, INF, INF), 1.0),  "x>>b -> 1 (flat)")


def test_trapezoidal_triangle():
    print("\n=== 5. Trapezoidal — triangle (b==c) ===")
    # Normal: (3, 5, 5, 7)
    check(approx(trapezoidal(3, 3, 5, 5, 7), 0.0),   "x=a -> 0")
    check(approx(trapezoidal(4, 3, 5, 5, 7), 0.5),    "rising midpoint -> 0.5")
    check(approx(trapezoidal(5, 3, 5, 5, 7), 1.0),    "peak -> 1")
    check(approx(trapezoidal(6, 3, 5, 5, 7), 0.5),    "falling midpoint -> 0.5")
    check(approx(trapezoidal(7, 3, 5, 5, 7), 0.0),    "x=d -> 0")


# ================================================================
#  2. VARIABLE DEFINITIONS — match document equations
# ================================================================
def test_nivel_rio_equations():
    print("\n=== 6. X1: Nivel del Rio — document equations ===")
    mfs = NIVEL_RIO.terms

    # Bajo
    check(approx(mfs['Bajo'](0), 1.0),   "Bajo(0) = 1")
    check(approx(mfs['Bajo'](2), 1.0),   "Bajo(2) = 1 [x<=2]")
    check(approx(mfs['Bajo'](3), 0.5),   "Bajo(3) = (4-3)/2 = 0.5")
    check(approx(mfs['Bajo'](4), 0.0),   "Bajo(4) = 0")
    check(approx(mfs['Bajo'](5), 0.0),   "Bajo(5) = 0")

    # Normal
    check(approx(mfs['Normal'](3), 0.0),  "Normal(3) = 0")
    check(approx(mfs['Normal'](4), 0.5),  "Normal(4) = (4-3)/2 = 0.5")
    check(approx(mfs['Normal'](5), 1.0),  "Normal(5) = 1 [peak]")
    check(approx(mfs['Normal'](6), 0.5),  "Normal(6) = (7-6)/2 = 0.5")
    check(approx(mfs['Normal'](7), 0.0),  "Normal(7) = 0")

    # Alerta
    check(approx(mfs['Alerta'](6), 0.0),          "Alerta(6) = 0")
    check(approx(mfs['Alerta'](6.75), 0.5),       "Alerta(6.75) = 0.5")
    check(approx(mfs['Alerta'](7.5), 1.0),        "Alerta(7.5) = 1 [peak]")
    check(approx(mfs['Alerta'](8.25), 0.5),       "Alerta(8.25) = 0.5")
    check(approx(mfs['Alerta'](9), 0.0),          "Alerta(9) = 0")

    # Critico
    check(approx(mfs['Crítico'](8), 0.0),  "Critico(8) = 0")
    check(approx(mfs['Crítico'](9), 0.5),  "Critico(9) = (9-8)/2 = 0.5")
    check(approx(mfs['Crítico'](10), 1.0), "Critico(10) = 1")


def test_precipitacion_equations():
    print("\n=== 7. X2: Precipitacion — document equations ===")
    mfs = PRECIPITACION.terms

    # Seco
    check(approx(mfs['Seco'](0), 1.0),    "Seco(0) = 1")
    check(approx(mfs['Seco'](40), 1.0),   "Seco(40) = 1 [x<=40]")
    check(approx(mfs['Seco'](60), 0.5),   "Seco(60) = (80-60)/40 = 0.5")
    check(approx(mfs['Seco'](80), 0.0),   "Seco(80) = 0")
    check(approx(mfs['Seco'](100), 0.0),  "Seco(100) = 0")

    # Moderado
    check(approx(mfs['Moderado'](60), 0.0),   "Moderado(60) = 0")
    check(approx(mfs['Moderado'](80), 0.5),   "Moderado(80) = (80-60)/40 = 0.5")
    check(approx(mfs['Moderado'](100), 1.0),  "Moderado(100) = 1 [peak]")
    check(approx(mfs['Moderado'](120), 0.5),  "Moderado(120) = (140-120)/40 = 0.5")
    check(approx(mfs['Moderado'](140), 0.0),  "Moderado(140) = 0")

    # Fuerte
    check(approx(mfs['Fuerte'](110), 0.0),  "Fuerte(110) = 0")
    check(approx(mfs['Fuerte'](135), 0.5),  "Fuerte(135) = (135-110)/50 = 0.5")
    check(approx(mfs['Fuerte'](160), 1.0),  "Fuerte(160) = 1")
    check(approx(mfs['Fuerte'](200), 1.0),  "Fuerte(200) = 1")


def test_alerta_equations():
    print("\n=== 8. Y: Alerta de Emergencia — document equations ===")
    mfs = ALERTA.terms

    # Nula
    check(approx(mfs['Nula'](0), 1.0),    "Nula(0) = 1")
    check(approx(mfs['Nula'](10), 1.0),   "Nula(10) = 1 [y<=10]")
    check(approx(mfs['Nula'](17.5), 0.5), "Nula(17.5) = (25-17.5)/15 = 0.5")
    check(approx(mfs['Nula'](25), 0.0),   "Nula(25) = 0")

    # Preventiva
    check(approx(mfs['Preventiva'](20), 0.0),  "Preventiva(20) = 0")
    check(approx(mfs['Preventiva'](27.5), 0.5),"Preventiva(27.5) = 0.5")
    check(approx(mfs['Preventiva'](35), 1.0),  "Preventiva(35) = 1 [peak]")
    check(approx(mfs['Preventiva'](42.5), 0.5),"Preventiva(42.5) = 0.5")
    check(approx(mfs['Preventiva'](50), 0.0),  "Preventiva(50) = 0")

    # Amarilla
    check(approx(mfs['Amarilla'](45), 0.0),  "Amarilla(45) = 0")
    check(approx(mfs['Amarilla'](52.5), 0.5),"Amarilla(52.5) = 0.5")
    check(approx(mfs['Amarilla'](60), 1.0),  "Amarilla(60) = 1 [peak]")
    check(approx(mfs['Amarilla'](67.5), 0.5),"Amarilla(67.5) = 0.5")
    check(approx(mfs['Amarilla'](75), 0.0),  "Amarilla(75) = 0")

    # Roja
    check(approx(mfs['Roja'](70), 0.0),  "Roja(70) = 0")
    check(approx(mfs['Roja'](80), 0.5),  "Roja(80) = (80-70)/20 = 0.5")
    check(approx(mfs['Roja'](90), 1.0),  "Roja(90) = 1")
    check(approx(mfs['Roja'](100), 1.0), "Roja(100) = 1")


# ================================================================
#  3. RULES — structural integrity
# ================================================================
def test_rules_structure():
    print("\n=== 9. Rules — structural integrity ===")
    check(len(RULES) == 9, "9 rules defined")

    # R1: single antecedent, no operator
    check(RULES[0].id == 'R1', "R1 id")
    check(RULES[0].operator is None, "R1 single antecedent (no operator)")
    check(RULES[0].consequent_term == 'Nula', "R1 -> Nula")

    # R6: AND operator
    check(RULES[5].id == 'R6', "R6 id")
    check(RULES[5].operator == Operator.AND, "R6 AND operator")
    check(RULES[5].consequent_term == 'Amarilla', "R6 -> Amarilla")

    # R8: OR operator
    check(RULES[7].id == 'R8', "R8 id")
    check(RULES[7].operator == Operator.OR, "R8 OR operator")
    check(RULES[7].consequent_term == 'Roja', "R8 -> Roja")

    # R9: single antecedent
    check(RULES[8].id == 'R9', "R9 id")
    check(RULES[8].operator is None, "R9 single antecedent")

    # All consequent_terms exist in output variable
    for r in RULES:
        check(r.consequent_term in ALERTA.terms,
              f"{r.id} consequent '{r.consequent_term}' exists in output var")


# ================================================================
#  4. ENGINE — fuzzification
# ================================================================
def test_fuzzification_scenario():
    print("\n=== 10. Fuzzification — document scenario X1=7.3, X2=115 ===")
    crisp = {'Nivel del Rio': 7.3, 'Precipitacion': 115}
    # Use actual variable names
    crisp = {INPUT_VARIABLES[0].name: 7.3, INPUT_VARIABLES[1].name: 115}
    fuzz = fuzzify(INPUT_VARIABLES, crisp)

    # X1 = 7.3
    x1f = fuzz[INPUT_VARIABLES[0].name]
    check(approx(x1f['Bajo'], 0.0),              "X1: Bajo = 0")
    check(approx(x1f['Normal'], 0.0),             "X1: Normal = 0 [7.3 >= 7]")
    check(approx(x1f['Alerta'], 1.3/1.5),         "X1: Alerta = (7.3-6)/1.5 = 0.8667")
    check(approx(x1f['Crítico'], 0.0),            "X1: Critico = 0 [7.3 <= 8]")

    # X2 = 115
    x2f = fuzz[INPUT_VARIABLES[1].name]
    check(approx(x2f['Seco'], 0.0),               "X2: Seco = 0")
    check(approx(x2f['Moderado'], 25.0/40.0),     "X2: Moderado = (140-115)/40 = 0.625")
    check(approx(x2f['Fuerte'], 5.0/50.0),        "X2: Fuerte = (115-110)/50 = 0.1")


# ================================================================
#  5. ENGINE — rule activation
# ================================================================
def test_rule_activation_scenario():
    print("\n=== 11. Rule activation — X1=7.3, X2=115 ===")
    crisp = {INPUT_VARIABLES[0].name: 7.3, INPUT_VARIABLES[1].name: 115}
    result = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp, 'mamdani')

    ids = {ar.rule.id for ar in result.activated_rules}
    # Expected active: R6, R7, R8
    check('R6' in ids, "R6 activated (Alerta AND Moderado)")
    check('R7' in ids, "R7 activated (Alerta AND Fuerte)")
    check('R8' in ids, "R8 activated (Critico OR Fuerte)")
    # Expected inactive
    for rid in ('R1', 'R2', 'R3', 'R4', 'R5', 'R9'):
        check(rid not in ids, f"{rid} NOT activated")

    # Firing strengths
    strengths = {ar.rule.id: ar.firing_strength for ar in result.activated_rules}
    check(approx(strengths['R6'], min(1.3/1.5, 25.0/40.0)),
          f"R6 alpha = min(0.8667, 0.625) = 0.625")
    check(approx(strengths['R7'], min(1.3/1.5, 5.0/50.0)),
          f"R7 alpha = min(0.8667, 0.1) = 0.1")
    check(approx(strengths['R8'], max(0.0, 5.0/50.0)),
          f"R8 alpha = max(0, 0.1) = 0.1")


# ================================================================
#  6. ENGINE — Mamdani vs Larsen implication
# ================================================================
def test_implication_methods():
    print("\n=== 12. Implication — Mamdani vs Larsen ===")
    crisp = {INPUT_VARIABLES[0].name: 7.3, INPUT_VARIABLES[1].name: 115}

    # Mamdani
    res_m = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp, 'mamdani')
    for ar, mu in res_m.implied_sets:
        max_val = np.max(mu)
        check(max_val <= ar.firing_strength + 1e-9,
              f"Mamdani {ar.rule.id}: max(mu) <= alpha ({max_val:.4f} <= {ar.firing_strength:.4f})")

    # Larsen
    res_l = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp, 'larsen')
    for ar, mu in res_l.implied_sets:
        max_val = np.max(mu)
        check(approx(max_val, ar.firing_strength, tol=1e-4),
              f"Larsen {ar.rule.id}: max(mu) ~= alpha ({max_val:.4f} ~= {ar.firing_strength:.4f})")

    # Mamdani clips -> flat top; Larsen scales -> preserves shape
    # For R6 (Amarilla, alpha=0.625): Mamdani has plateau, Larsen has a peak
    r6_m = [mu for ar, mu in res_m.implied_sets if ar.rule.id == 'R6'][0]
    r6_l = [mu for ar, mu in res_l.implied_sets if ar.rule.id == 'R6'][0]
    plateau_count_m = np.sum(np.isclose(r6_m, 0.625))
    plateau_count_l = np.sum(np.isclose(r6_l, 0.625))
    check(plateau_count_m > plateau_count_l,
          f"Mamdani R6 has wider plateau ({plateau_count_m}) than Larsen ({plateau_count_l})")


# ================================================================
#  7. ENGINE — aggregation
# ================================================================
def test_aggregation():
    print("\n=== 13. Aggregation — max operator ===")
    crisp = {INPUT_VARIABLES[0].name: 7.3, INPUT_VARIABLES[1].name: 115}
    result = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp, 'mamdani')

    # Aggregation = pointwise max of all implied sets
    manual_agg = np.zeros_like(result.y_universe)
    for _, mu in result.implied_sets:
        manual_agg = np.maximum(manual_agg, mu)
    check(np.allclose(result.mu_aggregated, manual_agg),
          "mu_aggregated == pointwise max of implied sets")

    # Max of aggregated should be max firing strength (0.625 from R6)
    check(approx(np.max(result.mu_aggregated), 0.625, tol=1e-4),
          f"max(aggregated) = 0.625 [from R6]")


# ================================================================
#  8. DEFUZZIFICATION — centroid
# ================================================================
def test_centroid():
    print("\n=== 14. Centroid — known cases ===")
    # Symmetric triangle centered at 50
    y = np.linspace(0, 100, 201)
    mu = np.maximum(0, 1 - np.abs(y - 50) / 25)  # triangle peak at 50
    c = centroid(y, mu)
    check(approx(c, 50.0, tol=0.01), f"symmetric triangle centroid = {c:.4f} ~= 50")

    # Uniform distribution
    mu_flat = np.ones_like(y)
    c_flat = centroid(y, mu_flat)
    check(approx(c_flat, 50.0, tol=0.01), f"uniform centroid = {c_flat:.4f} ~= 50")

    # All zeros -> NaN
    mu_zero = np.zeros_like(y)
    c_zero = centroid(y, mu_zero)
    check(math.isnan(c_zero), "all-zero -> NaN")

    # Single point mass at y=80
    mu_point = np.zeros_like(y)
    idx_80 = np.argmin(np.abs(y - 80))
    mu_point[idx_80] = 1.0
    c_point = centroid(y, mu_point)
    check(approx(c_point, 80.0, tol=0.5), f"point mass at 80 centroid = {c_point:.2f}")


# ================================================================
#  9. DEFUZZIFICATION — center of maxima
# ================================================================
def test_center_of_maxima():
    print("\n=== 15. Center of Maxima — known cases ===")
    y = np.linspace(0, 100, 201)

    # Single peak at y=60
    mu = np.maximum(0, 1 - np.abs(y - 60) / 15)
    com = center_of_maxima(y, mu)
    check(approx(com, 60.0, tol=0.5), f"single peak CoM = {com:.4f} ~= 60")

    # Flat plateau from 30 to 70
    mu_plat = np.zeros_like(y)
    mu_plat[(y >= 30) & (y <= 70)] = 0.8
    com_plat = center_of_maxima(y, mu_plat)
    check(approx(com_plat, 50.0, tol=0.5), f"plateau [30,70] CoM = {com_plat:.4f} ~= 50")

    # Two equal-height peaks at 20 and 80
    mu_two = np.zeros_like(y)
    mu_two[np.argmin(np.abs(y - 20))] = 1.0
    mu_two[np.argmin(np.abs(y - 80))] = 1.0
    com_two = center_of_maxima(y, mu_two)
    check(approx(com_two, 50.0, tol=0.5), f"two peaks (20,80) CoM = {com_two:.4f} ~= 50")

    # All zeros -> NaN
    com_zero = center_of_maxima(y, np.zeros_like(y))
    check(math.isnan(com_zero), "all-zero -> NaN")


# ================================================================
# 10. INTEGRATION — full pipeline, document scenario
# ================================================================
def test_full_pipeline_scenario():
    print("\n=== 16. Full pipeline — X1=7.3, X2=115 (all 4 combos) ===")
    crisp = {INPUT_VARIABLES[0].name: 7.3, INPUT_VARIABLES[1].name: 115}

    results = {}
    for method in ('mamdani', 'larsen'):
        r = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp, method)
        c = centroid(r.y_universe, r.mu_aggregated)
        m = center_of_maxima(r.y_universe, r.mu_aggregated)
        results[method] = {'centroide': c, 'centro_maximos': m}

        check(not math.isnan(c), f"{method}: centroid is not NaN ({c:.4f})")
        check(not math.isnan(m), f"{method}: CoM is not NaN ({m:.4f})")
        check(0 <= c <= 100, f"{method}: centroid in [0,100] ({c:.4f})")
        check(0 <= m <= 100, f"{method}: CoM in [0,100] ({m:.4f})")

    # Centroid: expect value in the Amarilla zone (~55-65%) since R6 dominates
    for method in ('mamdani', 'larsen'):
        c = results[method]['centroide']
        check(45 < c < 75, f"{method}: centroid in Amarilla zone ({c:.4f})")

    # Mamdani centroid != Larsen centroid (methods differ)
    cm = results['mamdani']['centroide']
    cl = results['larsen']['centroide']
    check(not approx(cm, cl, tol=0.01),
          f"Mamdani centroid ({cm:.4f}) != Larsen centroid ({cl:.4f})")

    print(f"\n  [INFO] Mamdani+Centroide = {results['mamdani']['centroide']:.4f}%")
    print(f"  [INFO] Mamdani+CoM      = {results['mamdani']['centro_maximos']:.4f}%")
    print(f"  [INFO] Larsen+Centroide  = {results['larsen']['centroide']:.4f}%")
    print(f"  [INFO] Larsen+CoM        = {results['larsen']['centro_maximos']:.4f}%")


# ================================================================
# 11. EDGE CASES
# ================================================================
def test_edge_extreme_low():
    print("\n=== 17. Edge case — X1=0, X2=0 (extreme low) ===")
    crisp = {INPUT_VARIABLES[0].name: 0, INPUT_VARIABLES[1].name: 0}
    result = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp, 'mamdani')

    fuzz = result.fuzzified
    check(approx(fuzz[INPUT_VARIABLES[0].name]['Bajo'], 1.0), "X1=0: Bajo=1")
    check(approx(fuzz[INPUT_VARIABLES[1].name]['Seco'], 1.0), "X2=0: Seco=1")

    ids = {ar.rule.id for ar in result.activated_rules}
    check('R1' in ids, "R1 activated (Bajo -> Nula)")
    check('R2' not in ids, "R2 NOT activated (Normal=0 AND Seco=1)")

    # Actually R2 requires Normal>0, which is 0 for x1=0. So R2 should NOT fire.
    # Let me re-check: R1 fires (Bajo=1). R2 requires Normal AND Seco, Normal(0)=0, so R2 doesn't fire.
    # But R1 has only X1 antecedent, so R1 fires with strength 1.0.

    c = centroid(result.y_universe, result.mu_aggregated)
    check(c < 20, f"Extreme low -> Nula zone centroid = {c:.4f}")


def test_edge_extreme_high():
    print("\n=== 18. Edge case — X1=10, X2=200 (extreme high) ===")
    crisp = {INPUT_VARIABLES[0].name: 10, INPUT_VARIABLES[1].name: 200}
    result = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp, 'mamdani')

    fuzz = result.fuzzified
    check(approx(fuzz[INPUT_VARIABLES[0].name]['Crítico'], 1.0), "X1=10: Critico=1")
    check(approx(fuzz[INPUT_VARIABLES[1].name]['Fuerte'], 1.0),  "X2=200: Fuerte=1")

    c = centroid(result.y_universe, result.mu_aggregated)
    check(c > 70, f"Extreme high -> Roja zone centroid = {c:.4f}")


def test_edge_no_activation():
    print("\n=== 19. Edge case — single-term activation zones ===")
    # X1=5 (peak of Normal), X2=100 (peak of Moderado)
    crisp = {INPUT_VARIABLES[0].name: 5, INPUT_VARIABLES[1].name: 100}
    result = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp, 'mamdani')

    ids = {ar.rule.id for ar in result.activated_rules}
    check('R3' in ids, "R3 fires (Normal=1 AND Moderado=1) -> Preventiva")
    strengths = {ar.rule.id: ar.firing_strength for ar in result.activated_rules}
    if 'R3' in strengths:
        check(approx(strengths['R3'], 1.0),
              f"R3 alpha = min(1, 1) = 1.0 (actual: {strengths['R3']:.4f})")


def test_universe_discretization():
    print("\n=== 20. Universe discretization ===")
    crisp = {INPUT_VARIABLES[0].name: 7.3, INPUT_VARIABLES[1].name: 115}
    result = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp,
                           'mamdani', resolution=0.5)
    # [0, 100] at 0.5 step -> 201 points
    check(len(result.y_universe) == 201,
          f"201 points at 0.5 resolution (actual: {len(result.y_universe)})")
    check(approx(result.y_universe[0], 0.0), "y[0] = 0")
    check(approx(result.y_universe[-1], 100.0), "y[-1] = 100")
    check(approx(result.y_universe[1] - result.y_universe[0], 0.5, tol=1e-10),
          "step = 0.5")


def test_resolution_independence():
    print("\n=== 21. Resolution independence ===")
    crisp = {INPUT_VARIABLES[0].name: 7.3, INPUT_VARIABLES[1].name: 115}

    # Compare centroid at different resolutions
    r_coarse = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp,
                              'mamdani', resolution=1.0)
    r_fine = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp,
                            'mamdani', resolution=0.1)

    c_coarse = centroid(r_coarse.y_universe, r_coarse.mu_aggregated)
    c_fine = centroid(r_fine.y_universe, r_fine.mu_aggregated)
    check(approx(c_coarse, c_fine, tol=0.5),
          f"Centroid stable across resolutions ({c_coarse:.4f} vs {c_fine:.4f})")


def test_inference_result_types():
    print("\n=== 22. InferenceResult — type integrity ===")
    crisp = {INPUT_VARIABLES[0].name: 7.3, INPUT_VARIABLES[1].name: 115}
    result = run_inference(INPUT_VARIABLES, OUTPUT_VARIABLE, RULES, crisp, 'mamdani')

    check(isinstance(result, InferenceResult), "returns InferenceResult")
    check(isinstance(result.fuzzified, dict), "fuzzified is dict")
    check(isinstance(result.activated_rules, list), "activated_rules is list")
    check(isinstance(result.y_universe, np.ndarray), "y_universe is ndarray")
    check(isinstance(result.mu_aggregated, np.ndarray), "mu_aggregated is ndarray")
    check(result.inference_method == 'mamdani', "method stored correctly")
    for ar in result.activated_rules:
        check(isinstance(ar, ActivatedRule), f"{ar.rule.id}: is ActivatedRule")
    for ar, mu in result.implied_sets:
        check(isinstance(mu, np.ndarray), f"{ar.rule.id}: implied set is ndarray")
        check(mu.shape == result.y_universe.shape,
              f"{ar.rule.id}: implied shape matches universe")


# ================================================================
# 12. MEMBERSHIP EDGE CASES — boundary values
# ================================================================
def test_membership_boundary_overlaps():
    print("\n=== 23. MF boundary overlaps ===")
    mfs = NIVEL_RIO.terms
    # At x=3: Bajo should be 0.5, Normal should be 0
    check(approx(mfs['Bajo'](3), 0.5), "x=3: Bajo=0.5")
    check(approx(mfs['Normal'](3), 0.0), "x=3: Normal=0 [boundary]")

    # At x=7: Normal=0, Alerta should be (7-6)/1.5 = 0.6667
    check(approx(mfs['Normal'](7), 0.0), "x=7: Normal=0")
    check(approx(mfs['Alerta'](7), 1.0/1.5, tol=1e-4), "x=7: Alerta=0.6667")

    # Sum of memberships across all terms at any point
    for x_val in [0, 2, 3, 5, 7, 8, 9, 10]:
        total = sum(mf(x_val) for mf in mfs.values())
        check(total <= 2.0 + 1e-9,
              f"x={x_val}: sum(mu) = {total:.4f} <= 2 (no triple overlap)")


# ================================================================
# RUN ALL TESTS
# ================================================================
if __name__ == '__main__':
    test_trapezoidal_scalar()
    test_trapezoidal_array()
    test_trapezoidal_left_shoulder()
    test_trapezoidal_right_shoulder()
    test_trapezoidal_triangle()
    test_nivel_rio_equations()
    test_precipitacion_equations()
    test_alerta_equations()
    test_rules_structure()
    test_fuzzification_scenario()
    test_rule_activation_scenario()
    test_implication_methods()
    test_aggregation()
    test_centroid()
    test_center_of_maxima()
    test_full_pipeline_scenario()
    test_edge_extreme_low()
    test_edge_extreme_high()
    test_edge_no_activation()
    test_universe_discretization()
    test_resolution_independence()
    test_inference_result_types()
    test_membership_boundary_overlaps()

    print(f"\n{'=' * 50}")
    print(f"  RESULTS:  {PASS} passed, {FAIL} failed")
    print(f"{'=' * 50}")
    sys.exit(1 if FAIL > 0 else 0)

