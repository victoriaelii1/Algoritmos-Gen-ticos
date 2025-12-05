import random

# -------------------------------------------------------------------
# 1. PARÁMETROS (Ajustados para velocidad)
# -------------------------------------------------------------------
TAMANO_POBLACION = 1000
MAX_GENERACIONES = 500  # Generaciones por intento
PROB_CRUCE = 0.9
PROB_MUTACION = 0.2     # Un poco más alta ayuda a no estancarse
PORCENTAJE_ELITISMO = 0.1
TAMANO_TORNEO = 3       # Torneo más pequeño es más rápido

# -------------------------------------------------------------------
# TABLERO INICIAL
# -------------------------------------------------------------------
TABLERO_PROBLEM = [
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

# PRE-CALCULO: Guardamos las coordenadas (fila, col) que son fijas
# para no tener que calcularlo miles de veces por segundo.
INDICES_FIJOS = [set() for _ in range(9)]
for r in range(9):
    for c in range(9):
        if TABLERO_PROBLEM[r][c] != 0:
            INDICES_FIJOS[r].add(c)

# -------------------------------------------------------------------
# 2. CLASE INDIVIDUO SIMPLIFICADA
# -------------------------------------------------------------------
class Individuo:
    def __init__(self, genes=None):
        # genes es una lista de listas de enteros: [[1,2..], [4,5..]...]
        self.genes = genes
        self.adaptacion = 0.0

    def inicializar_aleatorio(self):
        self.genes = []
        for r in range(9):
            fila_origen = TABLERO_PROBLEM[r]
            # Números que ya están en la fila (pistas)
            presentes = {x for x in fila_origen if x != 0}
            # Números que faltan (1 al 9)
            faltantes = [x for x in range(1, 10) if x not in presentes]
            random.shuffle(faltantes)
            
            nueva_fila = []
            for c in range(9):
                val = fila_origen[c]
                if val != 0:
                    nueva_fila.append(val)
                else:
                    nueva_fila.append(faltantes.pop())
            self.genes.append(nueva_fila)

# -------------------------------------------------------------------
# 3. FUNCIÓN DE ADAPTACIÓN (OPTIMIZADA)
# -------------------------------------------------------------------
def calcular_adaptacion(individuo):
    errores = 0
    grid = individuo.genes
    
    # 1. Columnas (recorremos cada columna j)
    for c in range(9):
        # Usamos un set para ver cuántos únicos hay
        # Al ser lista de listas simple, el acceso es muy rápido
        columna = {grid[r][c] for r in range(9)}
        errores += (9 - len(columna))

    # 2. Cuadrantes 3x3
    for r_bloque in (0, 3, 6):
        for c_bloque in (0, 3, 6):
            # Aplanamos el bloque en un set
            bloque = set()
            for r in range(r_bloque, r_bloque + 3):
                row = grid[r]
                for c in range(c_bloque, c_bloque + 3):
                    bloque.add(row[c])
            errores += (9 - len(bloque))
            
    individuo.adaptacion = errores
    return errores

# -------------------------------------------------------------------
# 4. OPERADORES GENÉTICOS (SIN DEEPCOPY)
# -------------------------------------------------------------------

def cruce(padre1, padre2):
    # Cruce uniforme por filas:
    # El hijo toma filas completas de P1 o P2.
    # Así mantenemos la restricción de "no repetidos en filas".
    genes_h1 = []
    genes_h2 = []
    
    for r in range(9):
        if random.random() < 0.5:
            # Importante: lista[:] crea una copia rápida (no referencia)
            genes_h1.append(padre1.genes[r][:])
            genes_h2.append(padre2.genes[r][:])
        else:
            genes_h1.append(padre2.genes[r][:])
            genes_h2.append(padre1.genes[r][:])
            
    return Individuo(genes_h1), Individuo(genes_h2)

def mutar(ind):
    # Intercambio de dos números dentro de una fila (Swap mutation)
    # Solo tocamos posiciones NO fijas.
    r = random.randint(0, 8)
    fila = ind.genes[r]
    
    # Índices movibles en esta fila (pre-calculados arriba es más rápido, 
    # pero calcularlo aquí es barato)
    movibles = [c for c in range(9) if c not in INDICES_FIJOS[r]]
    
    if len(movibles) >= 2:
        idx1, idx2 = random.sample(movibles, 2)
        # Swap directo
        fila[idx1], fila[idx2] = fila[idx2], fila[idx1]

# -------------------------------------------------------------------
# 5. BLOQUE PRINCIPAL
# -------------------------------------------------------------------
def main():
    intento = 1
    
    while True: # Bucle infinito de intentos
        print(f"\n{'='*40}")
        print(f" >>> INICIANDO INTENTO #{intento} <<<")
        print(f"{'='*40}")
        
        # 1. Crear Población
        poblacion = []
        for _ in range(TAMANO_POBLACION):
            nuevo = Individuo()
            nuevo.inicializar_aleatorio()
            calcular_adaptacion(nuevo)
            poblacion.append(nuevo)
            
        # Ordenamos una vez al principio
        poblacion.sort(key=lambda x: x.adaptacion)
        mejor_global = poblacion[0]
        print(f"Mejor adaptación inicial: {mejor_global.adaptacion}")
        
        # 2. Ciclo Evolutivo
        for gen in range(MAX_GENERACIONES):
            
            # Si encontramos solución, salimos
            if poblacion[0].adaptacion == 0:
                print(f"\n{'*'*50}")
                print(f"¡SOLUCIÓN ENCONTRADA EN INTENTO {intento}, GEN {gen}!")
                print(f"{'*'*50}")
                imprimir_tablero(poblacion[0])
                return # Fin del programa

            # Elitismo: Los mejores pasan directo
            num_elite = int(TAMANO_POBLACION * PORCENTAJE_ELITISMO)
            nueva_poblacion = []
            
            # Copia manual rápida de la élite
            for i in range(num_elite):
                # Clonamos genes manualmente para evitar deepcopy
                elite_genes = [fila[:] for fila in poblacion[i].genes]
                elite_ind = Individuo(elite_genes)
                elite_ind.adaptacion = poblacion[i].adaptacion
                nueva_poblacion.append(elite_ind)
            
            # Rellenar resto de población con cruce y mutación
            while len(nueva_poblacion) < TAMANO_POBLACION:
                # Selección Torneo rápida
                p1 = min(random.sample(poblacion, TAMANO_TORNEO), key=lambda x: x.adaptacion)
                p2 = min(random.sample(poblacion, TAMANO_TORNEO), key=lambda x: x.adaptacion)
                
                if random.random() < PROB_CRUCE:
                    h1, h2 = cruce(p1, p2)
                else:
                    # Copia manual si no hay cruce
                    h1 = Individuo([f[:] for f in p1.genes])
                    h2 = Individuo([f[:] for f in p2.genes])
                
                if random.random() < PROB_MUTACION: mutar(h1)
                if random.random() < PROB_MUTACION: mutar(h2)
                
                calcular_adaptacion(h1)
                calcular_adaptacion(h2)
                
                nueva_poblacion.append(h1)
                if len(nueva_poblacion) < TAMANO_POBLACION:
                    nueva_poblacion.append(h2)
            
            # Reemplazo generacional
            poblacion = nueva_poblacion
            poblacion.sort(key=lambda x: x.adaptacion)
            
            if (gen + 1) % 50 == 0:
                print(f" Gen {gen+1:3d} | Faltas: {poblacion[0].adaptacion}")

        # Si se acaban las generaciones sin éxito:
        print(f" -> Intento {intento} fallido. Reiniciando...")
        intento += 1

def imprimir_tablero(ind):
    print("Tablero Solución:")
    for r in range(9):
        if r % 3 == 0 and r > 0: print("-" * 21)
        row_str = []
        for c in range(9):
            row_str.append(str(ind.genes[r][c]))
            if (c + 1) % 3 == 0 and c < 8: row_str.append("|")
        print(" ".join(row_str))

if __name__ == "__main__":
    main()