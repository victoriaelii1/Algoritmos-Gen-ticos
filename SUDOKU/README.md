# Resolución de Sudoku mediante Algoritmos Genéticos y Computación Evolutiva

Este repositorio contiene el desarrollo y análisis comparativo de tres estrategias de Inteligencia Artificial para la resolución del Sudoku, modelado como un Problema de Satisfacción de Restricciones (CSP). Se explora la evolución desde una implementación manual hasta el uso de algoritmos multi-objetivo avanzados (NSGA-III).

**Autor:** Victoria Elizabeth Juárez Morales  
**Curso:** Programación Avanzada (Dr. Said Polanco Martagón)  
**Maestría en Ingeniería - Universidad Politécnica de Victoria**

---

##  Estructura del Proyecto

El proyecto se divide en tres enfoques evolutivos:

1.  **`desde_cero.py`**: Implementación manual (Python puro).
2.  **`con_deap.py`**: Implementación optimizada con librería DEAP.
3.  **`NSGAIII.py`**: Enfoque Multi-objetivo con selección NSGA-III.

---

## 1. Implementación Manual (`desde_cero.py`)

Diseñada para comprender la lógica fundamental de los operadores genéticos (selección por torneo, cruce y mutación) sin dependencia de librerías externas.

### 📊 Análisis de Resultados
* **Tiempo de Ejecución:** Variable (10 a 25+ minutos).
* **Comportamiento:** Alta inestabilidad estocástica.
* **Cuello de Botella:** La clonación de objetos (`copy.deepcopy`) y la falta de optimización nativa de Python saturan el procesador.
* **Conclusión:** Funcional para fines didácticos, pero computacionalmente costosa debido a la dificultad para escapar de óptimos locales con una tasa de mutación baja (0.1).

![Resultado Manual](img/cero.png)

---

## 2. Implementación con Librería DEAP (`con_deap.py`)

Uso de **Distributed Evolutionary Algorithms in Python (DEAP)** para optimizar la gestión de memoria y estructuras de datos.

### 📊 Análisis de Resultados
* **Tiempo Promedio:** ~1.5 minutos.
* **Estrategia:** Multi-start con Población Masiva (2,000 individuos).
* **Evaluaciones:** ~1.5 millones de individuos procesados en 90 segundos.
* **Justificación Técnica:** La eficiencia de DEAP permitió maximizar la diversidad genética inicial, contrarrestando la restricción de baja mutación. La convergencia es explosiva (entre 3 y 16 generaciones tras encontrar una población favorable).

![Resultado DEAP](img/deap.png)

---

## 3. Enfoque Multi-objetivo NSGA-III (`NSGAIII.py`)

Implementación avanzada utilizando el algoritmo **Non-dominated Sorting Genetic Algorithm III**. Se transformó el Sudoku de un problema mono-objetivo a uno multi-objetivo.

###  Adaptación Técnica
* **Objetivos Divididos:** Minimizar errores en **Filas**, **Columnas** y **Cajas** independientemente. Esto permite al algoritmo atacar defectos específicos sin destruir estructuras correctas.
* **Estrategia de "Intensidad Compensada":** Para respetar la restricción académica de **Probabilidad de Mutación = 0.1 (10%)**, se diseñó un operador personalizado que realiza **4 cambios (swaps)** internos cada vez que se activa la mutación. Esto otorga la agresividad necesaria para salir de estancamientos sin violar los parámetros.

###  Análisis de Resultados
* **Tiempo Promedio:** ~2 minutos.
* **Convergencia:** Solución óptima encontrada consistentemente en intentos tempranos (ej. Intento #4 o #6) y generaciones cortas (50-135).
* **Ventaja:** Al buscar el "Frente de Pareto" ideal (0,0,0), NSGA-III mantiene una diversidad de soluciones "equilibradas" mucho mayor que el algoritmo genético tradicional.

![Resultado NSGA-III](img/nsgaIII.png)

---

##  Conclusión General

La implementación con librerías especializadas y enfoques multi-objetivo validó que el "cuello de botella" del problema no era la lógica evolutiva, sino la eficiencia del lenguaje y la estrategia de búsqueda.

| Método | Tiempo Aprox. | Estabilidad | Observación |
| :--- | :--- | :--- | :--- |
| **Manual** | 10 - 25 min | Baja | Alta dependencia del azar inicial. |
| **DEAP** | ~1.5 min | Alta | Fuerza bruta optimizada eficiente. |
| **NSGA-III** | ~2 min | Muy Alta | Mejor capacidad para resolver conflictos locales. |