import copy
import json
import numpy as np
import vrplib
import matplotlib.pyplot as plt

nom = "X-n101-k25"
instance = vrplib.read_instance(f"data/X/{nom}.vrp")
with open("data/bks_X.json", encoding="utf-8") as f:
    bks = json.load(f)["bks"]

# distances arrondies à l'entier (convention des instances X)
D = np.rint(instance["edge_weight"]).astype(int)
q = instance["demand"]
Q = instance["capacity"]
coords = instance["node_coord"]
n = len(q) - 1

def cout_tournee(r):
    return sum(D[a][b] for a, b in zip(r[:-1], r[1:]))

def cout_total(sol):
    return int(sum(cout_tournee(r) for r in sol))

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

def meilleur_deplacement(sol):
    # cherche le déplacement d'un client vers une autre tournée qui fait le plus baisser le coût
    charges = [sum(q[c] for c in r) for r in sol]
    meilleur = (0, None)
    for a, ra in enumerate(sol):
        for i in range(1, len(ra) - 1):
            c = ra[i]
            gain_retrait = D[ra[i-1]][c] + D[c][ra[i+1]] - D[ra[i-1]][ra[i+1]]
            for b, rb in enumerate(sol):
                if b == a or charges[b] + q[c] > Q:
                    continue
                for j in range(1, len(rb)):
                    cout_ajout = D[rb[j-1]][c] + D[c][rb[j]] - D[rb[j-1]][rb[j]]
                    delta = cout_ajout - gain_retrait
                    if delta < meilleur[0]:
                        meilleur = (delta, (a, i, b, j))
    return meilleur

def appliquer(sol, mv):
    a, i, b, j = mv
    c = sol[a].pop(i)
    sol[b].insert(j, c)
    if len(sol[a]) == 2:
        sol.pop(a)

def dessiner_tournees(ax, sol, titre):
    # une couleur par tournée, le dépôt en carré noir
    cmap = plt.get_cmap("tab20")
    for k, r in enumerate(sol):
        x = [coords[i][0] for i in r]
        y = [coords[i][1] for i in r]
        ax.plot(x, y, "-o", color=cmap(k % 20), markersize=3, linewidth=1)
    ax.plot(coords[0][0], coords[0][1], "ks", markersize=9)
    ax.set_title(titre)

sol = solution_initiale()
sol_depart = copy.deepcopy(sol)
c0 = cout_total(sol)
print("départ  : coût", c0, "| gap : %.2f %%" % gap(c0, bks[nom]))

cout = c0
historique = [cout]
while True:
    delta, mv = meilleur_deplacement(sol)
    if mv is None:
        break
    appliquer(sol, mv)
    cout += int(delta)
    historique.append(cout)

c1 = cout_total(sol)
print("arrivée : coût", c1, "| gap : %.2f %%" % gap(c1, bks[nom]))
print("tournées :", len(sol), "| valide :", est_valide(sol))

fig, axs = plt.subplots(1, 3, figsize=(18, 5))
dessiner_tournees(axs[0], sol_depart, "Départ : coût %d (gap %.1f %%)" % (c0, gap(c0, bks[nom])))
dessiner_tournees(axs[1], sol, "Arrivée : coût %d (gap %.1f %%)" % (c1, gap(c1, bks[nom])))
axs[2].plot(historique)
axs[2].axhline(bks[nom], color="red", linestyle="--", label="BKS")
axs[2].set_title("Évolution du coût")
axs[2].set_xlabel("Déplacements")
axs[2].set_ylabel("Coût total")
axs[2].legend()
plt.tight_layout()
plt.show()