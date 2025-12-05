import random
import numpy as np
from deap import base, creator, tools, algorithms

# ===================================================================
# 1. CONFIGURACIÓN Y PARÁMETROS
# ===================================================================

# --- PARÁMETROS EVOLUTIVOS ---
TAMANO_POBLACION = 600    # Población alta para compensar baja mutación
MAX_GENERACIONES = 200    # Generaciones cortas (si no sale rápido, mejor reiniciar)
INTENTOS_MAXIMOS = 100    # Reintentar muchas veces automáticamente

PROB_CRUCE = 0.8          # Alta probabilidad de mezcla (Recombinación)
PROB_MUTACION = 0.1       # <--- (10%)

# --- EL TABLERO (TU PROBLEMA) ---
TABLERO_INICIAL = [
    [0, 6, 0, 1, 0, 4, 0, 5, 0],
    [0, 0, 8, 3, 0, 5, 6, 0, 0],
    [2, 0, 0, 0, 0, 0, 0, 0, 1],
    [8, 0, 0, 4, 0, 7, 0, 0, 6],
    [0, 0, 6, 0, 0, 0, 3, 0, 0],
    [7, 0, 0, 9, 0, 1, 0, 0, 4],
    [5, 0, 0, 0, 0, 0, 0, 0, 2],
    [0, 0, 7, 2, 0, 6, 9, 0, 0],
    [0, 4, 0, 5, 0, 8, 0, 7, 0]
]

# Pre-calculamos los índices fijos (pistas) para no borrarlos nunca
INDICES_FIJOS = []
for r in range(9):
    fila_fijos = set()
    for c in range(9):
        if TABLERO_INICIAL[r][c] != 0:
            fila_fijos.add(c)
    INDICES_FIJOS.append(fila_fijos)

# ===================================================================
# 2. HERRAMIENTAS VISUALES
# ===================================================================
def imprimir_tablero_bonito(ind):
    # Convertimos el individuo a array numpy para facilitar impresión
    tablero = np.array(ind)
    print(" -----------------------")
    for i, fila in enumerate(tablero):
        if i > 0 and i % 3 == 0:
            print("|-------+-------+-------|")
        linea = "| "
        for j, val in enumerate(fila):
            linea += f"{val} "
            if (j + 1) % 3 == 0 and j < 8:
                linea += "| "
        linea += "|"
        print(linea)
    print(" -----------------------")

# ===================================================================
# 3. CONFIGURACIÓN DE DEAP (NSGA-III)
# ===================================================================

# 3 Objetivos: Min(Filas), Min(Cols), Min(Cajas)
creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()

def crear_individuo_sudoku():
    """
    Crea un tablero donde las FILAS ya son perfectas (sin repetidos).
    Esto reduce el problema a arreglar solo Columnas y Cajas.
    """
    genes = []
    for r in range(9):
        fila_origen = TABLERO_INICIAL[r]
        presentes = [x for x in fila_origen if x != 0]
        faltantes = [x for x in range(1, 10) if x not in presentes]
        random.shuffle(faltantes)
        
        fila_nueva = []
        for val in fila_origen:
            if val != 0:
                fila_nueva.append(val)
            else:
                fila_nueva.append(faltantes.pop())
        genes.append(fila_nueva)
    return creator.Individual(genes)

toolbox.register("individual", crear_individuo_sudoku)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluar_nsga3(individuo):
    grid = np.array(individuo)
    
    # 1. Filas (Siempre será 0 por construcción, pero NSGA-3 lo requiere)
    row_errors = 0 

    # 2. Columnas
    col_errors = 0
    for c in range(9):
        col_errors += (9 - len(set(grid[:, c])))

    # 3. Cajas 3x3
    box_errors = 0
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            box = grid[i:i+3, j:j+3].flatten()
            box_errors += (9 - len(set(box)))

    return row_errors, col_errors, box_errors

toolbox.register("evaluate", evaluar_nsga3)

# --- OPERADORES GENÉTICOS ---

# CRUCE: Uniforme
# Mezcla las filas de Padre A y Padre B independientemente.
# Es mejor que TwoPoint para este tipo de representación.
toolbox.register("mate", tools.cxUniform, indpb=0.5)

# MUTACIÓN "FUERTE" (Compensada)
# Esta función se ejecuta solo cuando el algoritmo decide mutar (10% de las veces).
# Pero cuando entra aquí, hacemos MULTIPLES cambios para aprovechar la oportunidad.
def mutar_sudoku_fuerte(individual, indpb):
    
    INTENSIDAD = 4 # Número de swaps que haremos de una sola vez
    
    for _ in range(INTENSIDAD):
        # Elegimos una fila al azar
        fila_idx = random.randint(0, 8)
        fila = individual[fila_idx]
        
        # Identificamos qué celdas se pueden mover (no son pistas)
        indices_prohibidos = INDICES_FIJOS[fila_idx]
        movibles = [i for i in range(9) if i not in indices_prohibidos]
        
        # Si hay al menos 2 números para intercambiar, lo hacemos
        if len(movibles) >= 2:
            idx1, idx2 = random.sample(movibles, 2)
            # Swap (Intercambio)
            fila[idx1], fila[idx2] = fila[idx2], fila[idx1]

    return (individual,)

# Registramos la mutación. El 'indpb' aquí es simbólico para la función interna,
# la probabilidad real de llamada la define el main en PROB_MUTACION.
toolbox.register("mutate", mutar_sudoku_fuerte, indpb=0.1)

# SELECCIÓN NSGA-III
# p=12 es un valor estándar recomendado para 3 objetivos
ref_points = tools.uniform_reference_points(nobj=3, p=12)
toolbox.register("select", tools.selNSGA3, ref_points=ref_points)

# ===================================================================
# 4. LOOP PRINCIPAL CON REINICIOS
# ===================================================================
def main():
    random.seed(42) # Semilla fija para consistencia

    print(f"\n" + "="*60)
    print(f" >>> SUDOKU NSGA-III <<<")
    print("="*60)

    for intento in range(1, INTENTOS_MAXIMOS + 1):
        print(f"\n--- Intento #{intento} (Población: {TAMANO_POBLACION}) ---")
        
        # 1. Crear población nueva
        pop = toolbox.population(n=TAMANO_POBLACION)
        
        # 2. Evaluar inicial
        fitnesses = list(map(toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        # Variables para control de estancamiento
        mejor_fitness_historico = (99, 99, 99)
        generaciones_sin_mejora = 0

        # Ciclo evolutivo
        for gen in range(MAX_GENERACIONES):
            # Algoritmo varAnd aplica Cruce y Mutación según las probabilidades definidas
            offspring = algorithms.varAnd(pop, toolbox, cxpb=PROB_CRUCE, mutpb=PROB_MUTACION)
            
            # Evaluar descendencia
            fits = toolbox.map(toolbox.evaluate, offspring)
            for fit, ind in zip(fits, offspring):
                ind.fitness.values = fit
            
            # Selección NSGA-III (Une padres e hijos y selecciona los mejores)
            pop = toolbox.select(pop + offspring, TAMANO_POBLACION)
            
            # Obtener el mejor de la generación actual
            best_ind = tools.selBest(pop, 1)[0]
            current_fit = best_ind.fitness.values
            
            # --- VERIFICAR VICTORIA ---
            if current_fit == (0.0, 0.0, 0.0):
                print(f"\n" + "*"*60)
                print(f" ¡SOLUCIÓN ENCONTRADA! (Intento {intento}, Gen {gen})")
                print("*"*60)
                imprimir_tablero_bonito(best_ind)
                return # Termina el programa exitosamente

            # --- CONTROL DE ESTANCAMIENTO ---
            # Sumamos errores para ver si hay mejora general
            err_actual = sum(current_fit)
            err_mejor = sum(mejor_fitness_historico)

            if err_actual < err_mejor:
                mejor_fitness_historico = current_fit
                generaciones_sin_mejora = 0
            else:
                generaciones_sin_mejora += 1
            
            # Reporte cada 20 gens
            if gen % 20 == 0:
                print(f"   Gen {gen:3d} | Faltas (F, C, B): {current_fit}")

            # Si no mejora en 60 generaciones, abortamos este intento
            if generaciones_sin_mejora >= 60:
                print(f"   >> Estancado en {current_fit}. Reiniciando...")
                break 

        print(f"Fin del intento {intento}. Fallido.")

    print("\n:( Se agotaron todos los intentos.")

if __name__ == "__main__":
    main()