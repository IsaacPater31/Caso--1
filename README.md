# Sistema de Alerta Temprana por Inundación — Canal del Dique

## El problema

El Canal del Dique se desborda con facilidad cuando el río sube y llueve fuerte al mismo tiempo, y las poblaciones ribereñas del Bajo Magdalena dependen de que alguien decida a tiempo si hay que evacuar. Ese "a tiempo" es el problema: el nivel del río y la lluvia acumulada no dan una alerta binaria de sí o no, dan grados. Un río en 7.3 metros no es "normal" ni "crítico", está a medio camino entre alerta y crítico. Este programa toma esos dos números —nivel del río y precipitación acumulada— y calcula qué tan alta debe ser la alerta, de 0% a 100%, usando lógica difusa en vez de umbrales fijos.

## Qué hace

Le das el nivel del río (0 a 10 metros) y la lluvia acumulada en 24 horas (0 a 200 mm), y el sistema:

1. **Traduce los números a lenguaje de riesgo.** Calcula qué tan "bajo", "normal", "alerta" o "crítico" está el río, y qué tan "seco", "moderado" o de "lluvia fuerte" es la precipitación. Un mismo valor puede pertenecer a dos categorías a la vez (por ejemplo, un río puede estar 87% en "alerta" y algo en "crítico"), y el sistema calcula esos porcentajes.
2. **Aplica las reglas de los expertos.** Hay 9 reglas tipo "si el río está en alerta y la lluvia es fuerte, entonces la alerta de emergencia es roja". El sistema revisa cuáles reglas aplican con los valores que diste y con qué fuerza aplica cada una.
3. **Combina las reglas en dos versiones distintas**, para que puedas comparar:
   - **Mamdani**: recorta la respuesta de cada regla según su fuerza.
   - **Larsen**: la escala en vez de recortarla.
4. **Convierte todo eso en un solo número final** (el porcentaje de alerta), también de dos formas distintas:
   - **Centroide**: el promedio ponderado de toda la zona de riesgo combinada.
   - **Centro de máximos**: el punto medio de la franja de mayor alerta.
5. **Muestra todo en pantalla y en gráficas**: qué tan activado quedó cada término, qué reglas se dispararon y con qué fuerza, cómo se ve la zona de alerta combinada, y dónde cae el valor final. Puedes alternar entre Mamdani y Larsen con un botón sin volver a correr el programa.

El programa no está atado a los valores del taller (7.3 m y 115 mm) — acepta cualquier lectura dentro del rango del río (0-10 m) y de la lluvia (0-200 mm).

## Cómo correrlo

**Opción rápida (Windows):** haz doble clic en `run.bat`. Instala lo que falte y abre el programa solo.

**Opción rápida (Mac/Linux):**
```bash
./run.sh
```

**Manual, si ya tienes Python:**
```bash
pip install -r requirements.txt
python main.py
```

El programa te va a pedir el nivel del río y la precipitación por consola. También puedes pasárselos directo al ejecutarlo:
```bash
python main.py 7.3 115
```
(nivel del río en metros, luego precipitación en mm)

Necesitas Python 3.8 o más reciente. `run.bat`/`run.sh` crean un entorno virtual e instalan `numpy` y `matplotlib` automáticamente; si lo corres manual, instálalos tú con el `requirements.txt`.
