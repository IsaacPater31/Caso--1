# Taller Práctico Evaluativo: Corte 1 - Lógica Difusa y Sistemas Basados en Conocimiento

## Lineamientos Generales y Rúbrica de Evaluación

El presente taller práctico evaluativo tiene como propósito medir sus habilidades conceptuales, matemáticas y de programación en el marco del razonamiento bajo incertidumbre (Softcomputing) y los Sistemas Basados en Conocimiento (SBC).

### Distribución de Puntajes (10% total de la asignatura)

| Componente Evaluado | Criterios Detallados de Revisión | Peso |
| :--- | :--- | :--- |
| **Memorias de Cálculo Escritas (Teórico)** | Desarrollo matemático paso a paso, justificación analítica de cada fórmula de membresía, desfusificación por centroide/máximos y cálculo completo de propagación de factores de certeza. | 50% |
| **Implementación Computacional** | Código fuente funcional, estructurado, modular y parametrizable (en Python o MATLAB) para ambos casos. El código debe poder evaluar cualquier valor nítido ingresado en tiempo de ejecución de manera interactiva. | 35% |
| **Calidad del Reporte y Presentación** | Redacción técnica profesional, orden, claridad metodológica y cumplimiento riguroso de las pautas de presentación. | 15% |

### Pautas de Entrega Adicionales:
- El taller debe ser desarrollado en parejas (grupos de máximo 2 personas).
- Las memorias de cálculo teóricas deben entregarse en un documento digital ordenado o PDF.
- El software debe subirse a la plataforma académica classroom en un archivo comprimido (.zip) con los scripts correspondientes y un instructivo simple de ejecución (README).
- Se penalizará el plagio de código o la copia de soluciones con nota de 0.0 sin derecho a recuperación.

---

## CASO 1 (Lógica Difusa): Sistema de Alerta Temprana por Inundación en el Canal del Dique (Bajo Magdalena)

### El Problema
El Canal del Dique es una de las ramificaciones fluviales más críticas de la cuenca del Bajo Magdalena. Debido a la alta variabilidad del clima y al impacto de las temporadas de lluvias, el IDEAM y las administraciones locales requieren un sistema inteligente para automatizar la Alerta de Evacuación de las poblaciones ribereñas. Para esto, se diseñará un Algoritmo Difuso (AD) de tipo Mamdani con dos variables lingüísticas de entrada y una variable de salida.

### Variables del Sistema

| Rol | Nombre de la Variable | Universo de Discurso | Términos Lingüísticos (Conjuntos) |
| :--- | :--- | :--- | :--- |
| **Entrada X1** | Nivel del Río | [0, 10] metros | Bajo, Normal, Alerta, Crítico |
| **Entrada X2** | Precipitación Acumulada | [0, 200] mm en 24h | Seco, Moderado, Lluvia Fuerte |
| **Salida Y** | Nivel de Alerta de Emergencia| [0, 100]% | Nula, Preventiva, Alerta Amarilla, Alerta Roja |

### Ecuaciones de Membresía (Grados de Pertenencia µ)
*Nota: Se han normalizado las notaciones de las ecuaciones descritas en el documento original para mayor rigor matemático.*

#### Variable de Entrada X1: Nivel del Río (x)
**Bajo:**
- $\mu_{Bajo}(x) = 1$ si $x \leq 2$
- $\mu_{Bajo}(x) = (4-x)/2$ si $2 < x \leq 4$
- $\mu_{Bajo}(x) = 0$ si $x > 4$

**Normal:**
- $\mu_{Normal}(x) = 0$ si $x \leq 3$ o $x \geq 7$
- $\mu_{Normal}(x) = (x-3)/2$ si $3 < x \leq 5$
- $\mu_{Normal}(x) = (7-x)/2$ si $5 < x < 7$

**Alerta:**
- $\mu_{Alerta}(x) = 0$ si $x \leq 6$ o $x \geq 9$
- $\mu_{Alerta}(x) = (x-6)/1.5$ si $6 < x \leq 7.5$
- $\mu_{Alerta}(x) = (9-x)/1.5$ si $7.5 < x < 9$

**Crítico:**
- $\mu_{Critico}(x) = 0$ si $x \leq 8$
- $\mu_{Critico}(x) = (x-8)/2$ si $8 < x \leq 10$
- $\mu_{Critico}(x) = 1$ si $x > 10$

#### Variable de Entrada X2: Precipitación Acumulada (x)
**Seco:**
- $\mu_{Seco}(x) = 1$ si $x \leq 40$
- $\mu_{Seco}(x) = (80-x)/40$ si $40 < x \leq 80$
- $\mu_{Seco}(x) = 0$ si $x > 80$

**Moderado:**
- $\mu_{Moderado}(x) = 0$ si $x \leq 60$ o $x \geq 140$
- $\mu_{Moderado}(x) = (x-60)/40$ si $60 < x \leq 100$
- $\mu_{Moderado}(x) = (140-x)/40$ si $100 < x < 140$

**Fuerte (Lluvia Fuerte):**
- $\mu_{Fuerte}(x) = 0$ si $x \leq 110$
- $\mu_{Fuerte}(x) = (x-110)/50$ si $110 < x \leq 160$
- $\mu_{Fuerte}(x) = 1$ si $x > 160$

#### Variable de Salida Y: Alerta de Emergencia (y)
**Nula:**
- $\mu_{Nula}(y) = 1$ si $y \leq 10$
- $\mu_{Nula}(y) = (25-y)/15$ si $10 < y \leq 25$
- $\mu_{Nula}(y) = 0$ si $y > 25$

**Preventiva:**
- $\mu_{Preventiva}(y) = 0$ si $y \leq 20$ o $y \geq 50$
- $\mu_{Preventiva}(y) = (y-20)/15$ si $20 < y \leq 35$
- $\mu_{Preventiva}(y) = (50-y)/15$ si $35 < y < 50$

**Alerta Amarilla:**
- $\mu_{Amarilla}(y) = 0$ si $y \leq 45$ o $y \geq 75$
- $\mu_{Amarilla}(y) = (y-45)/15$ si $45 < y \leq 60$
- $\mu_{Amarilla}(y) = (75-y)/15$ si $60 < y < 75$

**Alerta Roja:**
- $\mu_{Roja}(y) = 0$ si $y \leq 70$
- $\mu_{Roja}(y) = (y-70)/20$ si $70 < y \leq 90$
- $\mu_{Roja}(y) = 1$ si $y > 90$

### Base de Reglas Borrosas (BRB)
A partir de las directrices de expertos en gestión del riesgo e hidrología, se ha modelado la siguiente base de 9 reglas lingüísticas para el control de la emergencia en la cuenca:

| ID | Regla de Inferencia |
| :--- | :--- |
| **R1** | SI Nivel del Río es Bajo ENTONCES Alerta de Emergencia es Nula |
| **R2** | SI Nivel del Río es Normal Y Precipitación es Seco ENTONCES Alerta de Emergencia es Nula |
| **R3** | SI Nivel del Río es Normal Y Precipitación es Moderado ENTONCES Alerta de Emergencia es Preventiva |
| **R4** | SI Nivel del Río es Normal Y Precipitación es Lluvia Fuerte ENTONCES Alerta de Emergencia es Alerta Amarilla |
| **R5** | SI Nivel del Río es Alerta Y Precipitación es Seco ENTONCES Alerta de Emergencia es Preventiva |
| **R6** | SI Nivel del Río es Alerta Y Precipitación es Moderado ENTONCES Alerta de Emergencia es Alerta Amarilla |
| **R7** | SI Nivel del Río es Alerta Y Precipitación es Lluvia Fuerte ENTONCES Alerta de Emergencia es Alerta Roja |
| **R8** | SI Nivel del Río es Critico O Precipitación es Lluvia Fuerte ENTONCES Alerta de Emergencia es Alerta Roja |
| **R9** | SI Nivel del Río es Crítico ENTONCES Alerta de Emergencia es Alerta Roja |

### Escenario de Evaluación y Preguntas Teórico-Prácticas
Asuma que en un día de tormenta severa, la estación automática del Canal del Dique reporta los siguientes valores físicos nítidos:
- **Nivel del Río (X1) = 7.3 metros**
- **Precipitación Acumulada (X2) = 115 mm en 24 horas**

A partir de estas condiciones, responda detalladamente los siguientes puntos:

1. **FUSIFICACIÓN ANALÍTICA:** Calcule matemáticamente el grado de pertenencia de los valores de entrada en todos los conjuntos difusos donde tengan una membresía mayor que cero. Indique claramente qué términos lingüísticos se activan y con qué valores decimales de precisión.
2. **ANÁLISIS DE INFERENCIA COMPARATIVA:** Determine de forma analítica cuáles de las 9 reglas de la base de datos se activan. Calcule de forma paralela el valor del consecuente para cada una de las reglas aplicando los dos métodos de inferencia vistos en la materia:
   - a) Inferencia tipo Mamdani (Recorte de la función de salida por operador Mínimo).
   - b) Inferencia tipo Larsen (Escalado de la función de salida por operador Producto).
3. **AGREGACIÓN BORROSA:** Grafique y exprese de forma analítica la función de membresía del conjunto borroso agregado global de salida (Y_agregado) para ambos métodos (Mamdani y Larsen) considerando las operaciones de combinación de reglas concurrentes.
4. **DESFUSIFICACIÓN DETALLADA:** Encuentre el valor nítido real final de la Alerta de Emergencia (porcentaje entre 0% y 100%) aplicando los dos métodos de desfusificación principales:
   - a) Método del Centro de Áreas (Centroide) aplicando la discretización del universo de discurso de 0.5% en 0.5% (con memorias de cálculo en tabla o mediante el cálculo de la integral geométrica).
   - b) Método del Centro de Máximos (CoM).
   - *Nota:* Compare las cuatro combinaciones posibles (Mamdani+Centroide, Mamdani+CoM, Larsen+Centroide, Larsen+CoM) y justifique el impacto de la elección metodológica en la toma de decisiones de protección civil.
5. **IMPLEMENTACIÓN DE SOFTWARE:** Desarrolle un script en Python (o plantilla parametrizada en MATLAB) que implemente el algoritmo difuso completo de este caso. Su código no debe estar limitado al escenario de evaluación; debe recibir cualquier valor de entrada del universo de discurso, calcular la inferencia y graficar las funciones de membresía de entrada, las reglas activadas, la agregación resultante y la línea del centroide de desfusificación. Se evaluará la elegancia y documentación del algoritmo.
