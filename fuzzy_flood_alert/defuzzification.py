import numpy as np


def centroid(y, mu):
    total = np.sum(mu)
    if total == 0:
        return float('nan')
    return float(np.sum(y * mu) / total)


def center_of_maxima(y, mu):
    peak = np.max(mu)
    if peak == 0:
        return float('nan')
    indices = np.where(np.isclose(mu, peak))[0]
    return float((y[indices[0]] + y[indices[-1]]) / 2)

