import copy
import json
import random
import time
import numpy as np
import vrplib
import matplotlib.pyplot as plt

nom = "X-n101-k25"
iter_max = 1000   # nombre d'itérations du tabou
random.seed(0)

instance = vrplib.read_instance(f"data/X/{nom}.vrp")
with open("data/bks_X.json", encoding="utf-8") as f:
    bks = json.load(f)["bks"]

# distances arrondies à l'entier (convention des instances X)
D = np.rint(instance["edge_weight"]).astype(int).tolist()
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

def meilleur_voisin(sol, tabou, it, cout, meilleur_cout):
    # meilleur déplacement d'un client vers une autre tournée, même s'il fait monter le coût
    # un client tabou ne peut pas bouger, sauf si cela donne une solution meilleure que la meilleure connue
    charges = [sum(q[c] for c in r) for r in sol]
    meilleur = (float("inf"), None)
    for a, ra in enumerate(sol):
        for i in range(1, len(ra) - 1):
            c = ra[i]
            est_tabou = tabou.get(c, 0) > it
            gain_retrait = D[ra[i-1]][c] + D[c][ra[i+1]] - D[ra[i-1]][ra[i+1]]
            for b, rb in enumerate(sol):
                if b == a or charges[b] + q[c] > Q:
                    continue
                for j in range(1, len(rb)):
                    delta = D[rb[j-1]][c] + D[c][rb[j]] - D[rb[j-1]][rb[j]] - gain_retrait
                    if est_tabou and cout + delta >= meilleur_cout:
                        continue
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

def recherche_tabou(sol, iter_max):
    cout = cout_total(sol)
    best = copy.deepcopy(sol)
    best_cout = cout
    tabou = {}   # client -> itération jusqu'à laquelle il est interdit de le déplacer
    hist = [cout]
    hist_best = [best_cout]
    for it in range(1, iter_max + 1):
        delta, mv = meilleur_voisin(sol, tabou, it, cout, best_cout)
        if mv is None:
            break
        client = sol[mv[0]][mv[1]]
        appliquer(sol, mv)
        cout += int(delta)
        tabou[client] = it + random.randint(8, 15)   # durée tabou
        if cout < best_cout:
            best_cout = cout
            best = copy.deepcopy(sol)
        hist.append(cout)
        hist_best.append(best_cout)
        if it % 100 == 0:
            print("itération", it, "| meilleur coût :", best_cout, "| gap : %.2f %%" % gap(best_cout, bks[nom]))
    return best, best_cout, hist, hist_best

sol = solution_initiale()
sol_depart = copy.deepcopy(sol)
c0 = cout_total(sol)
print("départ  : coût", c0, "| gap : %.2f %%" % gap(c0, bks[nom]))

debut = time.time()
best, best_cout, hist, hist_best = recherche_tabou(sol, iter_max)
duree = time.time() - debut

print("arrivée : coût", best_cout, "| gap : %.2f %%" % gap(best_cout, bks[nom]))
print("tournées :", len(best), "| valide :", est_valide(best), "| temps : %.1f s" % duree)

fig, axs = plt.subplots(1, 3, figsize=(18, 5))
dessiner_tournees(axs[0], sol_depart, "Départ : coût %d (gap %.1f %%)" % (c0, gap(c0, bks[nom])))
dessiner_tournees(axs[1], best, "Tabou : coût %d (gap %.1f %%)" % (best_cout, gap(best_cout, bks[nom])))
axs[2].plot(hist, label="coût courant", alpha=0.6)
axs[2].plot(hist_best, label="meilleur coût")
axs[2].axhline(bks[nom], color="red", linestyle="--", label="BKS")
axs[2].set_title("Évolution du coût")
axs[2].set_xlabel("Itérations")
axs[2].set_ylabel("Coût total")
axs[2].legend()
plt.tight_layout()
plt.show()