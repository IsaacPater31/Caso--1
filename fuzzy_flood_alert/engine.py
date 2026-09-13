import numpy as np
from dataclasses import dataclass
from .membership import LinguisticVariable, MembershipFunction
from .rules import FuzzyRule, Operator


@dataclass
class ActivatedRule:
    rule: FuzzyRule
    firing_strength: float
    consequent_mf: MembershipFunction


@dataclass
class InferenceResult:
    crisp_inputs: dict
    fuzzified: dict
    activated_rules: list
    y_universe: np.ndarray
    implied_sets: list          # [(ActivatedRule, np.ndarray)]
    mu_aggregated: np.ndarray
    inference_method: str


# ── Fusificación ──────────────────────────────────────────────

def fuzzify(input_variables, crisp_inputs):
    return {
        var.name: {t: mf(crisp_inputs[var.name]) for t, mf in var.terms.items()}
        for var in input_variables
    }


# ── Evaluación de reglas ──────────────────────────────────────

def _firing_strength(rule, fuzzified):
    degrees = [fuzzified[var][term] for var, term in rule.antecedents]
    if len(degrees) == 1:
        return degrees[0]
    if rule.operator == Operator.AND:
        return min(degrees)
    return max(degrees)


def _evaluate_rules(rules, fuzzified, output_variable):
    activated = []
    for rule in rules:
        strength = _firing_strength(rule, fuzzified)
        if strength > 0:
            mf = output_variable.terms[rule.consequent_term]
            activated.append(ActivatedRule(rule, strength, mf))
    return activated


# ── Implicación ───────────────────────────────────────────────

def _implicate(activated_rule, y, method):
    mu_base = activated_rule.consequent_mf(y)
    alpha = activated_rule.firing_strength
    if method == 'mamdani':
        return np.minimum(alpha, mu_base)
    return alpha * mu_base  # larsen


# ── Agregación ────────────────────────────────────────────────

def _aggregate(mu_arrays):
    return np.maximum.reduce(mu_arrays)


# ── Pipeline completo ─────────────────────────────────────────

def run_inference(input_variables, output_variable, rules, crisp_inputs,
                  method='mamdani', resolution=0.5):
    fuzzified = fuzzify(input_variables, crisp_inputs)
    activated = _evaluate_rules(rules, fuzzified, output_variable)

    u_min, u_max = output_variable.universe
    n = int(round((u_max - u_min) / resolution)) + 1
    y = np.linspace(u_min, u_max, n)

    implied_sets = []
    mu_arrays = []
    for ar in activated:
        mu = _implicate(ar, y, method)
        implied_sets.append((ar, mu))
        mu_arrays.append(mu)

    mu_agg = _aggregate(mu_arrays) if mu_arrays else np.zeros_like(y)

    return InferenceResult(
        crisp_inputs=crisp_inputs,
        fuzzified=fuzzified,
        activated_rules=activated,
        y_universe=y,
        implied_sets=implied_sets,
        mu_aggregated=mu_agg,
        inference_method=method,
    )

