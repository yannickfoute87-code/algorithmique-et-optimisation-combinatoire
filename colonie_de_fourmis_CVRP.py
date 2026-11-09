"""
Colonie de fourmis pour le CVRP.

Utilisation :
  1. Mets ce fichier dans le même dossier que tes instances (.vrp, et .sol si tu les as).
  2. Lance :  python colonie_de_fourmis_CVRP.py
     (dans Jupyter :  %run colonie_de_fourmis_CVRP.py)
Le programme teste toutes les instances .vrp du dossier et affiche un tableau de résultats.
"""
import math
import random
import re
import time


# ---------- Lecture des fichiers de référence (CVRPLIB) ----------
def lire_instance(chemin):
    """Lit un fichier .vrp (format CVRPLIB) sans aucune bibliothèque."""
    capacite = None
    coordonnees, demandes = [], []
    section = None
    with open(chemin) as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne or ligne == "EOF":
                continue
            if ligne.startswith("CAPACITY"):
                capacite = int(ligne.split(":")[1])
            elif ligne.startswith("NODE_COORD_SECTION"):
                section = "coord"
            elif ligne.startswith("DEMAND_SECTION"):
                section = "demande"
            elif ligne.startswith("DEPOT_SECTION"):
                section = None
            elif section == "coord":
                _, x, y = ligne.split()[:3]
                coordonnees.append((float(x), float(y)))
            elif section == "demande":
                demandes.append(int(ligne.split()[1]))
    return {"coordonnees": coordonnees, "demandes": demandes, "capacite": capacite}


def lire_solution(chemin):
    """Lit un fichier .sol : renvoie les tournées de référence et leur coût."""
    tournees, cout = [], None
    with open(chemin) as f:
        for ligne in f:
            ligne = ligne.strip()
            if ligne.startswith("Route"):
                tournees.append([int(c) for c in ligne.split(":")[1].split()])
            elif ligne.startswith("Cost"):
                cout = float(ligne.split()[1])
    return tournees, cout


# ---------- Générateur d'instances ----------
def generer_instance(nb_clients, repartition="aleatoire", depot="centre",
                     capacite=50, demande_max=10, graine=1):
    """repartition : "aleatoire" ou "groupes" | depot : "centre" ou "coin"."""
    hasard = random.Random(graine)
    taille = 100
    coordonnees = [(50, 50) if depot == "centre" else (0, 0)]
    if repartition == "aleatoire":
        for _ in range(nb_clients):
            coordonnees.append((hasard.randint(0, taille), hasard.randint(0, taille)))
    else:
        nb_groupes = max(2, nb_clients // 10)
        centres = [(hasard.randint(10, 90), hasard.randint(10, 90)) for _ in range(nb_groupes)]
        for _ in range(nb_clients):
            cx, cy = hasard.choice(centres)
            x = min(taille, max(0, round(hasard.gauss(cx, 6))))
            y = min(taille, max(0, round(hasard.gauss(cy, 6))))
            coordonnees.append((x, y))
    demandes = [0] + [hasard.randint(1, demande_max) for _ in range(nb_clients)]
    return {"coordonnees": coordonnees, "demandes": demandes, "capacite": max(capacite, demande_max)}


# ---------- Distances, coût, vérification, gap ----------
def matrice_distances(data):
    """Distances arrondies à l'entier le plus proche (convention des instances de référence)."""
    pts = data["coordonnees"]
    n = len(pts)
    return [[math.floor(math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]) + 0.5)
             for j in range(n)] for i in range(n)]


def cout_solution(tournees, d):
    total = 0
    for t in tournees:
        chemin = [0] + t + [0]
        for i in range(len(chemin) - 1):
            total += d[chemin[i]][chemin[i + 1]]
    return total


def verifier_solution(tournees, data):
    problemes = []
    clients_attendus = set(range(1, len(data["demandes"])))
    for numero, t in enumerate(tournees, start=1):
        charge = sum(data["demandes"][c] for c in t)
        if charge > data["capacite"]:
            problemes.append(f"Camion {numero} trop chargé : {charge} pour une capacité de {data['capacite']}")
    tous = [c for t in tournees for c in t]
    for c in sorted(clients_attendus):
        nb = tous.count(c)
        if nb == 0:
            problemes.append(f"Le client {c} n'est livré par personne")
        elif nb > 1:
            problemes.append(f"Le client {c} est livré {nb} fois")
    return len(problemes) == 0, problemes


def gap(mon_cout, cout_reference):
    return 100 * (mon_cout - cout_reference) / cout_reference

# =====================================================================
#  COLONIE DE FOURMIS (style MAX-MIN Ant System) + recherche locale
# =====================================================================

def construire_solution(n, d, dem, Q, tau, eta, alpha, voisins, hasard, max_tournees):
    """Une fourmi construit une solution complète, client par client."""
    non_visites = set(range(1, n))
    tournees = []
    while non_visites:
        tournee, charge, courant = [], 0, 0
        derniere_tournee_autorisee = (max_tournees is not None and len(tournees) + 1 >= max_tournees)
        while True:
            # clients possibles : proches voisins non visités qui rentrent dans le camion
            candidats = [j for j in voisins[courant] if j in non_visites and charge + dem[j] <= Q]
            if not candidats:  # sinon, on regarde tous les clients restants
                candidats = [j for j in non_visites if charge + dem[j] <= Q]
            if not candidats:
                break  # camion plein pour tous les clients restants : retour au dépôt
            # on peut aussi choisir de retourner au dépôt (sauf si c'est le dernier camion autorisé)
            if tournee and not derniere_tournee_autorisee:
                candidats = candidats + [0]
            poids = [(tau[courant][j] ** alpha) * eta[courant][j] for j in candidats]
            choix = hasard.choices(candidats, weights=poids)[0]
            if choix == 0:
                break
            tournee.append(choix)
            charge += dem[choix]
            non_visites.remove(choix)
            courant = choix
        tournees.append(tournee)
    return tournees


def amelioration_locale(tournees, d, dem, Q):
    """Améliore une solution : 2-opt (dans une tournée), relocate et swap (entre tournées)."""
    tournees = [list(t) for t in tournees if t]
    EPS = 1e-9
    ameliore = True
    while ameliore:
        ameliore = False

        # --- 2-opt : on inverse un morceau de tournée si ça raccourcit ---
        for t in tournees:
            p = [0] + t + [0]
            trouve = True
            while trouve:
                trouve = False
                for i in range(len(p) - 2):
                    for j in range(i + 2, len(p) - 1):
                        delta = d[p[i]][p[j]] + d[p[i + 1]][p[j + 1]] - d[p[i]][p[i + 1]] - d[p[j]][p[j + 1]]
                        if delta < -EPS:
                            p[i + 1:j + 1] = reversed(p[i + 1:j + 1])
                            trouve = True
                            ameliore = True
            t[:] = p[1:-1]

        charges = [sum(dem[c] for c in t) for t in tournees]

        # --- relocate : on déplace un client dans une autre tournée ---
        fait = False
        for a in range(len(tournees)):
            ta = tournees[a]
            pa = [0] + ta + [0]
            for i in range(1, len(pa) - 1):
                c = pa[i]
                gain = d[pa[i - 1]][c] + d[c][pa[i + 1]] - d[pa[i - 1]][pa[i + 1]]
                for b in range(len(tournees)):
                    if b == a or charges[b] + dem[c] > Q:
                        continue
                    pb = [0] + tournees[b] + [0]
                    for k in range(len(pb) - 1):
                        cout_ajout = d[pb[k]][c] + d[c][pb[k + 1]] - d[pb[k]][pb[k + 1]]
                        if cout_ajout - gain < -EPS:
                            tournees[b].insert(k, c)
                            del ta[i - 1]
                            fait = True
                            break
                    if fait:
                        break
                if fait:
                    break
            if fait:
                break
        if fait:
            tournees = [t for t in tournees if t]
            ameliore = True
            continue

        # --- swap : on échange deux clients de deux tournées différentes ---
        for a in range(len(tournees)):
            pa = [0] + tournees[a] + [0]
            for b in range(a + 1, len(tournees)):
                pb = [0] + tournees[b] + [0]
                for i in range(1, len(pa) - 1):
                    for j in range(1, len(pb) - 1):
                        c1, c2 = pa[i], pb[j]
                        if charges[a] - dem[c1] + dem[c2] > Q or charges[b] - dem[c2] + dem[c1] > Q:
                            continue
                        delta = (d[pa[i - 1]][c2] + d[c2][pa[i + 1]] - d[pa[i - 1]][c1] - d[c1][pa[i + 1]]
                                 + d[pb[j - 1]][c1] + d[c1][pb[j + 1]] - d[pb[j - 1]][c2] - d[c2][pb[j + 1]])
                        if delta < -EPS:
                            tournees[a][i - 1], tournees[b][j - 1] = c2, c1
                            fait = True
                            break
                    if fait:
                        break
                if fait:
                    break
            if fait:
                break
        if fait:
            ameliore = True
    return tournees


def colonie_de_fourmis(data, nb_fourmis=20, nb_iterations=200, alpha=1.0, beta=3.0, rho=0.1,
                       max_tournees=None, temps_max=None, graine=0, afficher=False):
    """Résout un CVRP avec une colonie de fourmis.

    nb_fourmis    : fourmis par itération        | nb_iterations : nombre d'itérations maximum
    alpha         : poids des phéromones (traces) | beta : poids de la distance (proximité)
    rho           : évaporation des phéromones (0.1 = 10 % disparaît à chaque itération)
    max_tournees  : nombre maximum de camions (None = pas de limite)
    temps_max     : arrêt après ce nombre de secondes (None = pas de limite de temps)
    Renvoie (meilleures tournées, coût, historique des meilleurs coûts).
    """
    hasard = random.Random(graine)
    debut = time.time()
    n = len(data["demandes"])
    dem, Q = data["demandes"], data["capacite"]
    d = matrice_distances(data)

    # attractivité liée à la distance : plus c'est proche, plus c'est attirant
    eta = [[(1.0 / max(d[i][j], 0.5)) ** beta if i != j else 0.0 for j in range(n)] for i in range(n)]
    # on ne regarde d'abord que les 15 clients les plus proches (plus rapide)
    voisins = [sorted((j for j in range(1, n) if j != i), key=lambda j: d[i][j])[:15] for i in range(n)]

    def cle(tournees):  # d'abord respecter le nombre de camions, puis minimiser la distance
        depassement = max(0, len(tournees) - max_tournees) if max_tournees else 0
        return (depassement, cout_solution(tournees, d))

    # solution de départ : une première fourmi + amélioration locale
    tau = [[1.0] * n for _ in range(n)]
    meilleure = amelioration_locale(
        construire_solution(n, d, dem, Q, tau, eta, alpha, voisins, hasard, max_tournees), d, dem, Q)
    cle_meilleure = cle(meilleure)
    tau_max = 1.0 / (rho * max(cle_meilleure[1], 1))
    tau_min = tau_max / (2.0 * n)
    tau = [[tau_max] * n for _ in range(n)]
    historique = [cle_meilleure[1]]

    for it in range(nb_iterations):
        if temps_max is not None and time.time() - debut > temps_max:
            break

        # 1) chaque fourmi construit une solution
        meilleure_iter, cle_iter = None, None
        for _ in range(nb_fourmis):
            sol = construire_solution(n, d, dem, Q, tau, eta, alpha, voisins, hasard, max_tournees)
            k = cle(sol)
            if cle_iter is None or k < cle_iter:
                meilleure_iter, cle_iter = sol, k

        # 2) on améliore la meilleure solution de l'itération
        meilleure_iter = amelioration_locale(meilleure_iter, d, dem, Q)
        cle_iter = cle(meilleure_iter)
        if cle_iter < cle_meilleure:
            meilleure, cle_meilleure = meilleure_iter, cle_iter
            tau_max = 1.0 / (rho * max(cle_meilleure[1], 1))
            tau_min = tau_max / (2.0 * n)

        # 3) évaporation des phéromones
        for i in range(n):
            ligne = tau[i]
            for j in range(n):
                ligne[j] = max(tau_min, ligne[j] * (1 - rho))

        # 4) dépôt de phéromones sur la meilleure solution (de l'itération, ou la meilleure de toutes)
        reference = meilleure if it % 5 == 4 else meilleure_iter
        depot = 1.0 / max(cle(reference)[1], 1)
        for t in reference:
            chemin = [0] + t + [0]
            for i in range(len(chemin) - 1):
                a, b = chemin[i], chemin[i + 1]
                tau[a][b] = min(tau_max, tau[a][b] + depot)
                tau[b][a] = min(tau_max, tau[b][a] + depot)

        historique.append(cle_meilleure[1])
        if afficher and it % 20 == 0:
            print(f"Itération {it:4d} | meilleur coût : {cle_meilleure[1]} | camions : {len(meilleure)}")

    return meilleure, cle_meilleure[1], historique

# =====================================================================
#  OUTILS DE TEST : lancer l'algorithme sur plusieurs instances
# =====================================================================

def charger(nom):
    """Charge une instance de référence : fichiers NOM.vrp et NOM.sol dans le dossier du notebook."""
    data = lire_instance(nom + ".vrp")
    _, cout_ref = lire_solution(nom + ".sol")
    m = re.search(r"-k(\d+)", nom)
    return {"nom": nom, "data": data, "cout_ref": cout_ref, "K": int(m.group(1)) if m else None}


def creer(nom, nb_clients, repartition="aleatoire", depot="centre", capacite=50, graine=1, K=None):
    """Crée une instance générée (pas de coût de référence, donc pas de gap)."""
    data = generer_instance(nb_clients, repartition, depot, capacite, graine=graine)
    return {"nom": nom, "data": data, "cout_ref": None, "K": K}


def tester(instances, nb_essais=3, **parametres):
    """Lance la colonie de fourmis sur chaque instance, nb_essais fois (graines différentes)."""
    print(f"{'Instance':<22}{'clients':>8}{'meilleur':>10}{'moyen':>10}{'référence':>11}"
          f"{'gap min %':>11}{'gap moy %':>11}{'camions':>9}{'temps (s)':>11}")
    resultats = []
    for inst in instances:
        data, ref, K = inst["data"], inst["cout_ref"], inst["K"]
        d = matrice_distances(data)
        couts, meilleur_cout, meilleures_tournees = [], None, None
        debut = time.time()
        for essai in range(nb_essais):
            tournees, cout, _ = colonie_de_fourmis(data, max_tournees=K, graine=essai, **parametres)
            assert verifier_solution(tournees, data)[0], "solution invalide !"
            couts.append(cout)
            if meilleur_cout is None or cout < meilleur_cout:
                meilleur_cout, meilleures_tournees = cout, tournees
        temps = (time.time() - debut) / nb_essais
        moyen = sum(couts) / len(couts)
        g_min = f"{gap(meilleur_cout, ref):.2f}" if ref else "-"
        g_moy = f"{gap(moyen, ref):.2f}" if ref else "-"
        print(f"{inst['nom']:<22}{len(data['demandes']) - 1:>8}{meilleur_cout:>10}{moyen:>10.1f}"
              f"{(ref if ref else '-'):>11}{g_min:>11}{g_moy:>11}{len(meilleures_tournees):>9}{temps:>11.1f}")
        resultats.append({"nom": inst["nom"], "clients": len(data["demandes"]) - 1, "meilleur": meilleur_cout,
                          "moyen": moyen, "ref": ref, "tournees": meilleures_tournees, "temps": temps})
    return resultats


def dessiner(data, tournees, titre=""):
    """Dessine les tournées (nécessite matplotlib, installé par défaut dans la plupart des Jupyter)."""
    import matplotlib.pyplot as plt
    pts = data["coordonnees"]
    for t in tournees:
        chemin = [0] + t + [0]
        plt.plot([pts[i][0] for i in chemin], [pts[i][1] for i in chemin], marker="o", markersize=4)
    plt.scatter(pts[0][0], pts[0][1], c="red", marker="s", s=120, zorder=5, label="Dépôt")
    plt.title(titre)
    plt.legend()
    plt.show()


# =====================================================================
#  PROGRAMME PRINCIPAL : teste toutes les instances .vrp du dossier
# =====================================================================
if __name__ == "__main__":
    import glob
    import os

    NB_ESSAIS = 3          # nombre de lancements par instance (graines différentes)
    NB_ITERATIONS = 200    # nombre de tours de la colonie

    instances = []
    for fichier in sorted(glob.glob("*.vrp")):
        nom = fichier[:-4]
        data = lire_instance(fichier)
        cout_ref = lire_solution(nom + ".sol")[1] if os.path.exists(nom + ".sol") else None
        m = re.search(r"-k(\d+)", nom)
        instances.append({"nom": nom, "data": data, "cout_ref": cout_ref,
                          "K": int(m.group(1)) if m else None})

    if not instances:
        print("Aucun fichier .vrp trouvé dans le dossier :", os.getcwd())
    else:
        print(f"{len(instances)} instance(s) trouvée(s)\n")
        tester(instances, nb_essais=NB_ESSAIS, nb_iterations=NB_ITERATIONS)
