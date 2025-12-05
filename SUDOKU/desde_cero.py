import random
import copy
import numpy as np

# -------------------------------------------------------------------
# 1. PARÁMETROS DEL ALGORITMO 
# -------------------------------------------------------------------
TAMANO_POBLACION = 1000    # Tamaño de la población
MAX_GENERACIONES = 500   # Número máximo de generaciones
PROB_CRUCE = 0.9            # Probabilidad de cruce
PROB_MUTACION = 0.1        # Probabilidad de mutación
PORCENTAJE_ELITISMO = 0.1   # Porcentaje de la élite
TAMANO_TORNEO = 5      # (Método de selecciónTorneo)

# -------------------------------------------------------------------
# TABLERO A RESOLVER (Figura 1)
# -------------------------------------------------------------------
TABLERO_INICIAL = [
    [0, 6, 0, 1, 0, 4, 0, 5, 0],  # Fila 1
    [0, 0, 8, 3, 0, 5, 6, 0, 0],  # Fila 2
    [2, 0, 0, 0, 0, 0, 0, 0, 1],  # Fila 3
    [8, 0, 0, 4, 0, 7, 0, 0, 6],  # Fila 4
    [0, 0, 6, 0, 0, 0, 3, 0, 0],  # Fila 5
    [7, 0, 0, 9, 0, 1, 0, 0, 4],  # Fila 6
    [5, 0, 0, 0, 0, 0, 0, 0, 2],  # Fila 7
    [0, 0, 7, 2, 0, 6, 9, 0, 0],  # Fila 8
    [0, 4, 0, 5, 0, 8, 0, 7, 0]   # Fila 9
]

# -------------------------------------------------------------------
# 2. ESTRUCTURAS DE DATOS (INDIVIDUO)  
# -------------------------------------------------------------------
class Casilla:
    def __init__(self, valor, es_fijo):
        self.valor = valor
        self.es_fijo = es_fijo

class Individuo:
    def __init__(self, tablero_matriz):
        self.genes = [] 
        for i in range(9):
            fila_gen = []
            for j in range(9):
                valor = tablero_matriz[i][j]
                es_fijo = (valor != 0)
                fila_gen.append(Casilla(valor, es_fijo))
            self.genes.append(fila_gen)
        self.adaptacion = 0.0

    def imprimir(self):
        for i, fila in enumerate(self.genes):
            if i % 3 == 0 and i != 0:
                print("-" * 21)
            linea = ""
            for j, c in enumerate(fila):
                if j % 3 == 0 and j != 0:
                    linea += "| "
                linea += f"{c.valor} "
            print(linea)

# -------------------------------------------------------------------
# 3. GENERACIÓN DE LA POBLACIÓN INICIAL
# -------------------------------------------------------------------
def generar_individuo_inicial(tablero_inicial):
    individuo = Individuo(tablero_inicial)
    for i in range(9):
        fila_actual = individuo.genes[i]
        valores_fijos = [c.valor for c in fila_actual if c.es_fijo]
        valores_por_colocar = list(range(1, 10))
        for fijo in valores_fijos:
            if fijo in valores_por_colocar:
                valores_por_colocar.remove(fijo)
        random.shuffle(valores_por_colocar)
        for j in range(9):
            if not fila_actual[j].es_fijo:
                fila_actual[j].valor = valores_por_colocar.pop()
    return individuo

# -------------------------------------------------------------------
# 4. FUNCIÓN DE ADAPTACIÓN (FITNESS)
# -------------------------------------------------------------------
def calcular_adaptacion(individuo):
    num_faltas = 0
    # 1. Faltas columnas
    for j in range(9):
        columna = [individuo.genes[i][j].valor for i in range(9)]
        num_faltas += (9 - len(set(columna)))
    # 2. Faltas cuadrículas
    for i_sub in range(0, 9, 3):
        for j_sub in range(0, 9, 3):
            subcuadricula = []
            for i in range(i_sub, i_sub + 3):
                for j in range(j_sub, j_sub + 3):
                    subcuadricula.append(individuo.genes[i][j].valor)
            num_faltas += (9 - len(set(subcuadricula)))
    individuo.adaptacion = num_faltas

# -------------------------------------------------------------------
# 5. OPERADORES GENÉTICOS
# -------------------------------------------------------------------
def seleccion_torneo(poblacion, k=TAMANO_TORNEO):
    torneo = random.sample(poblacion, k)
    ganador = min(torneo, key=lambda ind: ind.adaptacion)
    return ganador

def cruce_por_filas(padre1, padre2):
    hijo1 = copy.deepcopy(padre1)
    hijo2 = copy.deepcopy(padre2)
    for i in range(9):
        if random.random() < 0.5:
            hijo1.genes[i] = copy.deepcopy(padre2.genes[i])
            hijo2.genes[i] = copy.deepcopy(padre1.genes[i])
    return hijo1, hijo2

def mutar_individuo(individuo):
    fila_idx = random.randint(0, 8)
    fila_gen = individuo.genes[fila_idx]
    posiciones_no_fijas = [j for j, c in enumerate(fila_gen) if not c.es_fijo]
    if len(posiciones_no_fijas) >= 2:
        k1, k2 = random.sample(posiciones_no_fijas, 2)
        valor_temp = fila_gen[k1].valor
        fila_gen[k1].valor = fila_gen[k2].valor
        fila_gen[k2].valor = valor_temp
    return individuo

# -------------------------------------------------------------------
# 6. BUCLE GENÉTICO PRINCIPAL
# -------------------------------------------------------------------
def main():
    intento = 1
    encontrado = False
    
    # Bucle infinito hasta encontrar la solución
    while not encontrado:
        print(f"\n" + "="*40)
        print(f" >>> INICIANDO INTENTO #{intento} <<<")
        print("="*40)
        print("Generando población inicial...")
        
        # 1. GENERAMOS UNA POBLACIÓN NUEVA (Reset total)
        poblacion = [generar_individuo_inicial(TABLERO_INICIAL) for _ in range(TAMANO_POBLACION)]
        for ind in poblacion:
            calcular_adaptacion(ind)
        
        mejor_global = min(poblacion, key=lambda ind: ind.adaptacion)
        print(f"Mejor adaptación inicial: {mejor_global.adaptacion}")
        
        # 2. Bucle de Generaciones corto (300 gens es suficiente para saber si va a ganar o no)
        # Si no gana en 300, asumimos que se trabó y reiniciamos.
        generaciones_por_intento = 150
        
        for gen in range(generaciones_por_intento):
            poblacion.sort(key=lambda ind: ind.adaptacion)
            
            # --- CONDICIÓN DE VICTORIA ---
            if poblacion[0].adaptacion == 0:
                mejor_global = copy.deepcopy(poblacion[0])
                encontrado = True
                break # Rompe el bucle for
            
            # Elitismo
            num_elite = int(TAMANO_POBLACION * PORCENTAJE_ELITISMO)
            nueva_poblacion = [copy.deepcopy(ind) for ind in poblacion[:num_elite]]
            
            # Cruce y Mutación
            while len(nueva_poblacion) < TAMANO_POBLACION:
                padre1 = seleccion_torneo(poblacion)
                padre2 = seleccion_torneo(poblacion)
                
                if random.random() < PROB_CRUCE:
                    hijo1, hijo2 = cruce_por_filas(padre1, padre2)
                else:
                    hijo1, hijo2 = copy.deepcopy(padre1), copy.deepcopy(padre2)
                
                if random.random() < PROB_MUTACION:
                    hijo1 = mutar_individuo(hijo1)
                if random.random() < PROB_MUTACION:
                    hijo2 = mutar_individuo(hijo2)
                
                if len(nueva_poblacion) < TAMANO_POBLACION:
                    nueva_poblacion.append(hijo1)
                if len(nueva_poblacion) < TAMANO_POBLACION:
                    nueva_poblacion.append(hijo2)

            poblacion = nueva_poblacion
            for ind in poblacion:
                calcular_adaptacion(ind)
            
            # Guardamos el mejor de la historia de este intento
            mejor_actual = min(poblacion, key=lambda ind: ind.adaptacion)
            if mejor_actual.adaptacion < mejor_global.adaptacion:
                mejor_global = copy.deepcopy(mejor_actual)
            
            # Imprimir progreso cada 50 generaciones
            if (gen + 1) % 50 == 0:
                print(f"  Gen {gen+1}/{generaciones_por_intento} | Faltas: {mejor_global.adaptacion}")

        # --- FIN DEL INTENTO ---
        if encontrado:
            print(f"\n" + "*"*50)
            print(f"¡¡¡SOLUCIÓN ENCONTRADA EN EL INTENTO {intento}, GEN {gen+1}!!!")
            print("*"*50)
            mejor_global.imprimir()
            print("\nEl tablero es una solución válida.")
        else:
            print(f"  -> Intento {intento} fallido (Se estancó en {mejor_global.adaptacion} faltas).")
            print("  -> Reiniciando algoritmo con nueva población...\n")
            intento += 1
# -------------------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------------------
if __name__ == "__main__":
    main()