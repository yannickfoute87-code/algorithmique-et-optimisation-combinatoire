import json
import vrplib

nom = "X-n101-k25"
instance = vrplib.read_instance(f"data/X/{nom}.vrp")
with open("data/bks_X.json", encoding="utf-8") as f:
    bks = json.load(f)["bks"]

D = instance["edge_weight"]
q = instance["demand"]
Q = instance["capacity"]
n = len(q) - 1

def cout_tournee(r):
    return sum(D[a][b] for a, b in zip(r[:-1], r[1:]))

def cout_total(sol):
    return sum(cout_tournee(r) for r in sol)

def solution_initiale():
    # plus proche voisin, en respectant la capacité
    non_visites = set(range(1, n + 1))
    sol = []
    while non_visites:
        route = [0]
        charge = 0
        courant = 0
        while True:
            candidats = [c for c in non_visites if charge + q[c] <= Q]
            if not candidats:
                break
            suivant = min(candidats, key=lambda c: D[courant][c])
            route.append(suivant)
            charge += q[suivant]
            non_visites.remove(suivant)
            courant = suivant
        route.append(0)
        sol.append(route)
    return sol

def est_valide(sol):
    clients = sorted(c for r in sol for c in r[1:-1])
    capa_ok = all(sum(q[c] for c in r) <= Q for r in sol)
    return clients == list(range(1, n + 1)) and capa_ok

def gap(cout, ref):
    return 100 * (cout - ref) / ref

sol = solution_initiale()
c = cout_total(sol)
print("tournées :", len(sol), "| valide :", est_valide(sol))
print("coût :", c, "| BKS :", bks[nom], "| gap : %.2f %%" % gap(c, bks[nom]))