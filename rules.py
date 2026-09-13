from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Operator(Enum):
    AND = "AND"
    OR = "OR"


@dataclass
class FuzzyRule:
    id: str
    antecedents: list               # [(var_name, term_name), ...]
    operator: Optional[Operator]    # None for single-antecedent rules
    consequent_term: str


_NR = 'Nivel del Río'
_PR = 'Precipitación'

RULES = [
    FuzzyRule('R1', [(_NR, 'Bajo')],                          None,         'Nula'),
    FuzzyRule('R2', [(_NR, 'Normal'),  (_PR, 'Seco')],        Operator.AND, 'Nula'),
    FuzzyRule('R3', [(_NR, 'Normal'),  (_PR, 'Moderado')],    Operator.AND, 'Preventiva'),
    FuzzyRule('R4', [(_NR, 'Normal'),  (_PR, 'Lluvia Fuerte')], Operator.AND, 'Amarilla'),
    FuzzyRule('R5', [(_NR, 'Alerta'),  (_PR, 'Seco')],        Operator.AND, 'Preventiva'),
    FuzzyRule('R6', [(_NR, 'Alerta'),  (_PR, 'Moderado')],    Operator.AND, 'Amarilla'),
    FuzzyRule('R7', [(_NR, 'Alerta'),  (_PR, 'Lluvia Fuerte')], Operator.AND, 'Roja'),
    FuzzyRule('R8', [(_NR, 'Crítico'), (_PR, 'Lluvia Fuerte')], Operator.OR,  'Roja'),
    FuzzyRule('R9', [(_NR, 'Crítico')],                        None,         'Roja'),
]

