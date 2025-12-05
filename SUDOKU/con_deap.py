import random
import numpy as np
import copy
from deap import base, creator, tools

# -------------------------------------------------------------------
# 1. PARÁMETROS DEL ALGORITMO (CONFIGURACIÓN RÁPIDA)
# -------------------------------------------------------------------
TAMANO_POBLACION = 2000        # Población alta para mayor diversidad inicial
MAX_GENERACIONES_POR_INTENTO = 150 # Reinicio rápido si se estanca
PROB_CRUCE = 0.9
PROB_MUTACION = 0.1
PORCENTAJE_ELITISMO = 0.1 
TAMANO_TORNEO = 5

# -------------------------------------------------------------------
# TABLERO A RESOLVER
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# 2. FUNCIÓN PARA IMPRIMIR BONITO (NUEVA)
# -------------------------------------------------------------------
def imprimir_tablero_bonito(tablero):
    print(" -----------------------")
    for i, fila in enumerate(tablero):
        # Cada 3 filas imprimimos una línea horizontal divisoria
        if i > 0 and i % 3 == 0:
            print("|-------+-------+-------|")
        
        linea = "| "
        for j, val in enumerate(fila):
            linea += f"{val} "
            # Cada 3 columnas imprimimos una barra vertical
            if (j + 1) % 3 == 0 and j < 8:
                linea += "| "
        linea += "|"
        print(linea)
    print(" -----------------------")

# -------------------------------------------------------------------
# 3. CONFIGURACIÓN DE DEAP
# -------------------------------------------------------------------
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

def crear_individuo_sudoku():
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

def evaluar_sudoku(individuo):
    num_faltas = 0
    # Columnas
    for c in range(9):
        columna = [individuo[r][c] for r in range(9)]
        num_faltas += (9 - len(set(columna)))
    # Subcuadrículas
    for i_sub in range(0, 9, 3):
        for j_sub in range(0, 9, 3):
            subcuadricula = []
            for r in range(i_sub, i_sub + 3):
                for c in range(j_sub, j_sub + 3):
                    subcuadricula.append(individuo[r][c])
            num_faltas += (9 - len(set(subcuadricula)))
    return (num_faltas,)

toolbox.register("evaluate", evaluar_sudoku)
toolbox.register("mate", tools.cxUniform, indpb=0.5)

def mutar_sudoku(individuo, indpb):
    fila_idx = random.randint(0, 8)
    fila = individuo[fila_idx]
    indices_movibles = [i for i, val in enumerate(TABLERO_INICIAL[fila_idx]) if val == 0]
    if len(indices_movibles) >= 2:
        idx1, idx2 = random.sample(indices_movibles, 2)
        fila[idx1], fila[idx2] = fila[idx2], fila[idx1]
    return (individuo,)

toolbox.register("mutate", mutar_sudoku, indpb=PROB_MUTACION)
toolbox.register("select", tools.selTournament, tournsize=TAMANO_TORNEO)

# -------------------------------------------------------------------
# 4. FUNCIÓN PRINCIPAL
# -------------------------------------------------------------------
def main():
    intento = 1
    encontrado = False
    
    while not encontrado:
        print(f"\n" + "="*45)
        print(f" >>> INICIANDO INTENTO #{intento} (Pop: {TAMANO_POBLACION}) <<<")
        print("="*45)
        
        poblacion = toolbox.population(n=TAMANO_POBLACION)
        
        fitnesses = list(map(toolbox.evaluate, poblacion))
        for ind, fit in zip(poblacion, fitnesses):
            ind.fitness.values = fit
            
        mejor_ind = tools.selBest(poblacion, 1)[0]
        print(f"Mejor adaptación inicial: {mejor_ind.fitness.values[0]}")
        
        for gen in range(MAX_GENERACIONES_POR_INTENTO):
            poblacion.sort(key=lambda x: x.fitness.values[0])
            
            if poblacion[0].fitness.values[0] == 0:
                encontrado = True
                break
            
            num_elite = int(TAMANO_POBLACION * PORCENTAJE_ELITISMO)
            elite = [toolbox.clone(ind) for ind in poblacion[:num_elite]]
            
            offspring = toolbox.select(poblacion, len(poblacion) - num_elite)
            offspring = list(map(toolbox.clone, offspring))
            
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < PROB_CRUCE:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < PROB_MUTACION:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            poblacion[:] = elite + offspring
            
            if (gen + 1) % 25 == 0:
                print(f"  Gen {gen+1}/{MAX_GENERACIONES_POR_INTENTO} | Faltas: {poblacion[0].fitness.values[0]}")

        if encontrado:
            print(f"\n" + "*"*50)
            print(f"¡SOLUCIÓN ENCONTRADA EN EL INTENTO {intento}, GEN {gen}!")
            print("*"*50)
            
            mejor_final = tools.selBest(poblacion, 1)[0]
            # AQUÍ LLAMAMOS A LA FUNCIÓN DE IMPRESIÓN BONITA
            imprimir_tablero_bonito(mejor_final)
            
            print("\nEl tablero es una solución válida.")
        else:
            print(f"  -> Intento {intento} fallido. Reiniciando...\n")
            intento += 1

if __name__ == "__main__":
    main()