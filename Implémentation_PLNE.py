import math
import pulp

# --- Données de l'instance ---
coords = {0: (0, 0), 1: (3, 4), 2: (5, 10), 3: (-3, 3), 4: (-2, -4)}  # 0 = dépôt
demande = {1: 8, 2: 3, 3: 9, 4: 7}  # demande des clients
Q, K = 10, 2 # capacité du véhicule et nombre de véhicules
clients = list(demande)
noeuds = [0] + clients 

def dist(i, j): #distance euclidienne entre les noeuds i et j
    return math.dist(coords[i], coords[j])

# --- Le problème doit être créé AVANT les variables ---
prob = pulp.LpProblem("CVRP", pulp.LpMinimize)

# --- Variables : créées par le problème avec add_variable ---
x = {(i, j): prob.add_variable(f"x_{i}_{j}", cat=pulp.LpBinary)
     for i in noeuds for j in noeuds if i != j}
u = {i: prob.add_variable(f"u_{i}", lowBound=demande[i], upBound=Q)
     for i in clients}

# --- Objectif ---
prob += pulp.lpSum(dist(i, j) * x[i, j] for i in noeuds for j in noeuds if i != j)

# --- Contraintes (identiques à avant) ---
for i in clients:
    prob += pulp.lpSum(x[i, j] for j in noeuds if j != i) == 1
    prob += pulp.lpSum(x[j, i] for j in noeuds if j != i) == 1
prob += pulp.lpSum(x[0, j] for j in clients) <= K
prob += pulp.lpSum(x[0, j] for j in clients) == pulp.lpSum(x[i, 0] for i in clients)
for i in clients:
    for j in clients:
        if i != j:
            prob += u[j] >= u[i] + demande[j] - Q * (1 - x[i, j])

# --- Résolution : COIN_CMD remplace PULP_CBC_CMD, et solve() renvoie des stats ---
stats = prob.solve(pulp.COIN_CMD(msg=False))

print(stats.status_str)                                  # "Optimal", "Infeasible", ...
print("Coût total :", pulp.value(prob.objective))
print("Arcs utilisés :", [(i, j) for (i, j) in x if x[i, j].varValue > 0.5])