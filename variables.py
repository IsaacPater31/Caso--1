from membership import MembershipFunction as MF, LinguisticVariable as LV

_INF = float('inf')

# ── Entrada X1: Nivel del Río [0, 10] metros ──────────────────
NIVEL_RIO = LV('Nivel del Río', (0, 10), {
    'Bajo':    MF('Bajo',    (-_INF, -_INF, 2, 4)),
    'Normal':  MF('Normal',  (3, 5, 5, 7)),
    'Alerta':  MF('Alerta',  (6, 7.5, 7.5, 9)),
    'Crítico': MF('Crítico', (8, 10, _INF, _INF)),
})

# ── Entrada X2: Precipitación Acumulada [0, 200] mm/24h ───────
PRECIPITACION = LV('Precipitación', (0, 200), {
    'Seco':     MF('Seco',     (-_INF, -_INF, 40, 80)),
    'Moderado': MF('Moderado', (60, 100, 100, 140)),
    'Fuerte':   MF('Fuerte',   (110, 160, _INF, _INF)),
})

# ── Salida Y: Alerta de Emergencia [0, 100] % ─────────────────
ALERTA = LV('Alerta de Emergencia', (0, 100), {
    'Nula':       MF('Nula',       (-_INF, -_INF, 10, 25)),
    'Preventiva': MF('Preventiva', (20, 35, 35, 50)),
    'Amarilla':   MF('Amarilla',   (45, 60, 60, 75)),
    'Roja':       MF('Roja',       (70, 90, _INF, _INF)),
})

INPUT_VARIABLES = [NIVEL_RIO, PRECIPITACION]
OUTPUT_VARIABLE = ALERTA

