import numpy as np
from dataclasses import dataclass


def trapezoidal(x, a, b, c, d):
    x = np.asarray(x, dtype=float)
    scalar = x.ndim == 0
    x = np.atleast_1d(x)
    y = np.zeros_like(x)

    # Rising edge (a → b)
    if b > a:
        mask = (x > a) & (x < b)
        y[mask] = (x[mask] - a) / (b - a)

    # Flat top [b, c]
    y[(x >= b) & (x <= c)] = 1.0

    # Falling edge (c → d)
    if d > c:
        mask = (x > c) & (x < d)
        y[mask] = (d - x[mask]) / (d - c)

    return float(y[0]) if scalar else y


@dataclass
class MembershipFunction:
    name: str
    params: tuple  # (a, b, c, d) — trapezoidal vertices

    def __call__(self, x):
        return trapezoidal(x, *self.params)


@dataclass
class LinguisticVariable:
    name: str
    universe: tuple  # (min, max)
    terms: dict      # {term_name: MembershipFunction}

