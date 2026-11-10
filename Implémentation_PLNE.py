import math
import pulp  # bibliothèque de modélisation : on y décrit le PLNE, un solveur le résout

# --- Données de l'instance ---
coords = {0: (0, 0), 1: (2, 4), 2: (5, 1), 3: (-3, 3), 4: (-2, -4)}  # 0 = dépôt
demande = {1: 4, 2: 3, 3: 5, 4: 2}  # demande de chaque client
Q, K = 10, 2                        # capacité d'un camion, nombre de camions
clients = list(demande)             # [1, 2, 3, 4]
noeuds = [0] + clients              # dépôt + clients

def dist(i, j):
    # distance euclidienne entre deux nœuds
    return math.dist(coords[i], coords[j])

# --- Création du problème : on veut minimiser ---
prob = pulp.LpProblem("CVRP", pulp.LpMinimize)

# --- Variables ---
# x[i, j] binaire : 1 si un camion va de i à j
x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
     for i in noeuds for j in noeuds if i != j}# u[i] continue : charge cumulée au client i, bornée entre sa demande et Q
u = {i: pulp.LpVariable(f"u_{i}", lowBound=demande[i], upBound=Q) for i in clients}

# --- Objectif : somme des distances des arcs utilisés ---
prob += pulp.lpSum(dist(i, j) * x[i, j] for i in noeuds for j in noeuds if i != j)

# --- Contraintes ---
for i in clients:
    prob += pulp.lpSum(x[i, j] for j in noeuds if j != i) == 1   # chaque client est quitté une fois
    prob += pulp.lpSum(x[j, i] for j in noeuds if j != i) == 1   # chaque client est atteint une fois
prob += pulp.lpSum(x[0, j] for j in clients) <= K                # au plus K départs du dépôt
prob += pulp.lpSum(x[0, j] for j in clients) == pulp.lpSum(x[i, 0] for i in clients)  # autant de retours
for i in clients:
    for j in clients:
        if i != j:
            # capacité + élimination des sous-tours (MTZ)
            prob += u[j] >= u[i] + demande[j] - Q * (1 - x[i, j])

# --- Résolution avec le solveur CBC fourni avec PuLP ---
prob.solve(pulp.PULP_CBC_CMD(msg=False))

print(pulp.LpStatus[pulp.LpProblem.status.fget(prob)] if False else pulp.LpStatus[prob.status])
print("Coût total :", pulp.value(prob.objective))
print("Arcs utilisés :", [(i, j) for (i, j) in x if x[i, j].value() > 0.5])