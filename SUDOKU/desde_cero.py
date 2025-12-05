import random

# -------------------------------------------------------------------
# 1. PARÁMETROS (IGUALADOS A DEAP Y NSGA-III)
# -------------------------------------------------------------------
TAMANO_POBLACION = 600   # Igual que en DEAP
MAX_GENERACIONES = 150   # Igual que en DEAP
PROB_CRUCE = 0.9
PROB_MUTACION = 0.1      # 10% 
PORCENTAJE_ELITISMO = 0.1
TAMANO_TORNEO = 3        

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

# PRE-CALCULO: Índices fijos
INDICES_FIJOS = [set() for _ in range(9)]
for r in range(9):
    for c in range(9):
        if TABLERO_PROBLEM[r][c] != 0:
            INDICES_FIJOS[r].add(c)

# -------------------------------------------------------------------
# 2. CLASE INDIVIDUO
# -------------------------------------------------------------------
class Individuo:
    def __init__(self, genes=None):
        self.genes = genes
        self.adaptacion = 0.0

    def inicializar_aleatorio(self):
        self.genes = []
        for r in range(9):
            fila_origen = TABLERO_PROBLEM[r]
            presentes = {x for x in fila_origen if x != 0}
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
# 3. FUNCIÓN DE ADAPTACIÓN
# -------------------------------------------------------------------
def calcular_adaptacion(individuo):
    errores = 0
    grid = individuo.genes
    
    # 1. Columnas
    for c in range(9):
        columna = {grid[r][c] for r in range(9)}
        errores += (9 - len(columna))

    # 2. Cuadrantes 3x3
    for r_bloque in (0, 3, 6):
        for c_bloque in (0, 3, 6):
            bloque = set()
            for r in range(r_bloque, r_bloque + 3):
                row = grid[r]
                for c in range(c_bloque, c_bloque + 3):
                    bloque.add(row[c])
            errores += (9 - len(bloque))
            
    individuo.adaptacion = errores
    return errores

# -------------------------------------------------------------------
# 4. OPERADORES GENÉTICOS
# -------------------------------------------------------------------
def cruce(padre1, padre2):
    genes_h1 = []
    genes_h2 = []
    for r in range(9):
        if random.random() < 0.5:
            genes_h1.append(padre1.genes[r][:])
            genes_h2.append(padre2.genes[r][:])
        else:
            genes_h1.append(padre2.genes[r][:])
            genes_h2.append(padre1.genes[r][:])
    return Individuo(genes_h1), Individuo(genes_h2)

def mutar(ind):
    # --- CAMBIO IMPORTANTE PARA LA COMPARATIVA ---
    # Hacemos 3 cambios para igualar la agresividad de DEAP/NSGA-III
    # bajo la misma regla del 10% de probabilidad de evento.
    CAMBIOS = 3 
    
    for _ in range(CAMBIOS):
        r = random.randint(0, 8)
        fila = ind.genes[r]
        movibles = [c for c in range(9) if c not in INDICES_FIJOS[r]]
        
        if len(movibles) >= 2:
            idx1, idx2 = random.sample(movibles, 2)
            fila[idx1], fila[idx2] = fila[idx2], fila[idx1]

# -------------------------------------------------------------------
# 5. BLOQUE PRINCIPAL
# -------------------------------------------------------------------
def main():
    intento = 1
    
    while True: 
        print(f"\n{'='*40}")
        print(f" >>> INICIANDO INTENTO #{intento} (Manual) <<<")
        print(f"{'='*40}")
        
        # 1. Crear Población
        poblacion = []
        for _ in range(TAMANO_POBLACION):
            nuevo = Individuo()
            nuevo.inicializar_aleatorio()
            calcular_adaptacion(nuevo)
            poblacion.append(nuevo)
            
        poblacion.sort(key=lambda x: x.adaptacion)
        
        # 2. Ciclo Evolutivo
        for gen in range(MAX_GENERACIONES):
            
            if poblacion[0].adaptacion == 0:
                print(f"\n{'*'*50}")
                print(f"¡SOLUCIÓN ENCONTRADA EN INTENTO {intento}, GEN {gen}!")
                print(f"{'*'*50}")
                imprimir_tablero(poblacion[0])
                return 

            # Elitismo
            num_elite = int(TAMANO_POBLACION * PORCENTAJE_ELITISMO)
            nueva_poblacion = []
            
            for i in range(num_elite):
                elite_genes = [fila[:] for fila in poblacion[i].genes]
                elite_ind = Individuo(elite_genes)
                elite_ind.adaptacion = poblacion[i].adaptacion
                nueva_poblacion.append(elite_ind)
            
            # Cruce y Mutación
            while len(nueva_poblacion) < TAMANO_POBLACION:
                sample = random.sample(poblacion, TAMANO_TORNEO * 2)
                p1 = min(sample[:TAMANO_TORNEO], key=lambda x: x.adaptacion)
                p2 = min(sample[TAMANO_TORNEO:], key=lambda x: x.adaptacion)
                
                if random.random() < PROB_CRUCE:
                    h1, h2 = cruce(p1, p2)
                else:
                    h1 = Individuo([f[:] for f in p1.genes])
                    h2 = Individuo([f[:] for f in p2.genes])
                
                if random.random() < PROB_MUTACION: mutar(h1)
                if random.random() < PROB_MUTACION: mutar(h2)
                
                calcular_adaptacion(h1)
                calcular_adaptacion(h2)
                
                nueva_poblacion.append(h1)
                if len(nueva_poblacion) < TAMANO_POBLACION:
                    nueva_poblacion.append(h2)
            
            poblacion = nueva_poblacion
            poblacion.sort(key=lambda x: x.adaptacion)
            
            if (gen + 1) % 50 == 0:
                print(f" Gen {gen+1:3d} | Faltas: {poblacion[0].adaptacion}")

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