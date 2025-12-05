# Resolución de Sudoku mediante Algoritmos Genéticos y Computación Evolutiva

Este repositorio contiene el desarrollo y análisis comparativo de tres estrategias de Inteligencia Artificial para la resolución del Sudoku, modelado como un Problema de Satisfacción de Restricciones (CSP). Se explora la evolución desde una implementación manual hasta el uso de algoritmos multi-objetivo avanzados (NSGA-III).

**Autor:** Victoria Elizabeth Juárez Morales  
**Curso:** Programación Avanzada (Dr. Said Polanco Martagón)  
**Maestría en Ingeniería - Universidad Politécnica de Victoria**

---

##  Estructura del Proyecto

El proyecto se divide en tres enfoques evolutivos distintos para resolver el mismo tablero de Sudoku:

1.  **`desde_cero.py`**: Implementación manual (Python puro sin librerías de IA).
2.  **`con_deap.py`**: Implementación optimizada con librería **DEAP** (Mono-objetivo).
3.  **`NSGAIII.py`**: Enfoque Multi-objetivo con selección **NSGA-III**.

---

## 1. Implementación Manual (`desde_cero.py`)

Diseñada para comprender la lógica fundamental de los operadores genéticos (selección por torneo, cruce y mutación) sin dependencia de librerías externas. Utiliza objetos y listas nativas de Python.

> ** Parámetros de Control:** Para garantizar una comparativa justa con la versión de librería, se utilizaron los **mismos hiperparámetros** que en la implementación con DEAP:
> * **Tamaño de Población:** 600 individuos.
> * **Probabilidad de Mutación:** 0.1 (10%).

###  Análisis de Resultados
* **Tiempo de Ejecución:** Variable (1 a 4 minutos).
* **Comportamiento:** Alta inestabilidad estocástica. Depende enteramente de la "suerte" en la generación inicial.
* **Cuello de Botella:** La gestión de memoria en Python puro (creación y destrucción de objetos `Individuo`) y la clonación profunda (`deepcopy`) limitan la velocidad de las generaciones.
* **Conclusión:** Funcional para fines didácticos, pero computacionalmente costosa. A igualdad de condiciones (Población 600), es notablemente más lenta que la versión optimizada.

![Resultado Manual](img/cero.png)

---

## 2. Implementación con Librería DEAP (`con_deap.py`)

Uso de **Distributed Evolutionary Algorithms in Python (DEAP)** para optimizar la gestión de memoria y estructuras de datos bajo un enfoque clásico (mono-objetivo). El objetivo único es minimizar la suma de errores (Columnas + Cajas).

> **⚙️ Parámetros de Control:** Configuración idéntica a la versión manual (**Población: 600**, **Mutación: 10%**) para medir la diferencia pura de rendimiento computacional.

###  Análisis de Resultados
* **Tiempo Promedio:** **Rápido (40 segundos a 1.5 minutos).**
* **Variabilidad:** Al ser un proceso estocástico, el número de intentos requeridos fluctúa, pero el sistema de reinicio rápido permite encontrar solución en pocos minutos.
* **Justificación Técnica:** La eficiencia interna de DEAP (usando Numpy y C bajo la capa) permite procesar los mismos 600 individuos mucho más rápido que la versión manual. Esto hace viable la estrategia de **"Fuerza Bruta Inteligente"**: si un intento no converge en 150 generaciones, se reinicia inmediatamente hasta encontrar una semilla favorable.

![Resultado DEAP](img/deap.png)

---

## 3. Enfoque Multi-objetivo NSGA-III (`NSGAIII.py`)

Implementación avanzada utilizando el algoritmo **Non-dominated Sorting Genetic Algorithm III**. Se transformó el Sudoku de un problema mono-objetivo a uno multi-objetivo para mantener diversidad genética.

###  Adaptación Técnica
* **Objetivos Divididos:** Minimizar errores en **Filas**, **Columnas** y **Cajas** independientemente. Esto permite al algoritmo atacar defectos específicos sin destruir estructuras correctas.
* **Estrategia de "Intensidad Compensada":** Para respetar la restricción académica de **Probabilidad de Mutación = 0.1 (10%)**, se diseñó un operador personalizado que realiza **4 cambios (swaps)** internos cada vez que se activa la mutación, compensando la baja frecuencia con alta intensidad.

###  Análisis de Resultados
* **Tiempo Promedio:** Variable (~2 minutos con suerte, hasta 10+ minutos).
* **Variabilidad de Convergencia:** El algoritmo es robusto buscando el Frente de Pareto (0,0,0). Puede resolverlo en intentos tempranos (Intento #4) o extenderse mucho más (Intento #41) dependiendo de la complejidad del mínimo local donde caiga.
* **Ventaja:** Mantiene la diversidad poblacional mejor que los métodos tradicionales, evitando la convergencia prematura a soluciones erróneas, aunque a un costo computacional mayor.

![Resultado NSGA-III](img/nsgaIII.png)

---

##  Conclusión General y Veredicto

Tras analizar las tres estrategias, se concluye que **la implementación con DEAP (Mono-objetivo) es la más eficiente para este problema específico**.

Aunque **NSGA-III** demostró ser una herramienta poderosa capaz de resolver el problema mediante la descomposición de objetivos, el Sudoku es inherentemente un problema de satisfacción de restricciones única (llegar a 0 errores total). El uso de NSGA-III añade una sobrecarga computacional (cálculo de frentes de Pareto y puntos de referencia) que, aunque académica y técnicamente interesante, resulta en un "Overkill" para este caso. **DEAP estándar** ofreció la mejor relación entre simplicidad de código y velocidad de convergencia.

| Método | Configuración | Tiempo Aprox. | Estabilidad | Observación |
| :--- | :--- | :--- | :--- | :--- |
| **Manual** | Pob: 600 / Mut: 10% | 1 - 4 min | Baja | Alta dependencia del azar inicial. Procesamiento limitado por Python puro. |
| **DEAP** | Pob: 600 / Mut: 10% | **40s - 1.5 min** | **Óptima** | **Mejor rendimiento a igualdad de parámetros. Velocidad superior gracias a optimización.** |
| **NSGA-III** | Pob: 1000 / Mut: 10% | 2 - 10+ min | Muy Alta | Excelente exploración teórica, pero con sobrecarga computacional innecesaria para Sudoku. |