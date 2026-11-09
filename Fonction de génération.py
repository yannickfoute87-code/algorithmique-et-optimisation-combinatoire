import numpy as np
import matplotlib.pyplot as plt


def generer_instance(n, repartition="R", depot="centre", route_moy=10,
                     fenetres=False, largeur_fenetre=50, seed=0):
    """Génère une instance CVRP (ou CVRPTW) aléatoire de n clients."""
    rng = np.random.default_rng(seed)
    taille = 2000

    # Position du dépôt
    if depot == "centre":
        dep = np.array([taille / 2, taille / 2])
    elif depot == "coin":
        dep = np.array([0.0, 0.0])
    else:
        dep = rng.uniform(0, taille, 2)

    # Position des clients
    if repartition == "R":
        coords = rng.uniform(0, taille, (n, 2))
    else:
        centres = rng.uniform(0, taille, (max(3, n // 30), 2))
        choix = rng.integers(0, len(centres), n)
        coords = centres[choix] + rng.normal(0, taille * 0.05, (n, 2))
        coords = np.clip(coords, 0, taille)

    # Demandes et capacité
    demandes = rng.integers(1, 100, n)
    capacite = int(np.ceil(route_moy * demandes.sum() / n))

    # Matrice des distances
    pts = np.vstack([dep, coords])
    diff = pts[:, None, :] - pts[None, :, :]
    dist = np.rint(np.sqrt((diff ** 2).sum(axis=2))).astype(int)

    instance = {"coords": pts, "demande": np.r_[0, demandes],
                "capacite": capacite, "dist": dist}

    if fenetres:
        service = 10
        horizon = int(dist[0].max() * 2 + 20 * service * route_moy)
        ouverture = np.zeros(n + 1, dtype=int)
        for i in range(1, n + 1):
            max_ouv = max(dist[0, i], horizon - dist[0, i] - service - largeur_fenetre)
            ouverture[i] = rng.integers(dist[0, i], max_ouv + 1)
        fermeture = ouverture + largeur_fenetre
        fermeture[0], ouverture[0] = horizon, 0
        instance.update({"ouverture": ouverture, "fermeture": fermeture,
                         "service": np.r_[0, np.full(n, service)]})
    return instance


# --- Test : cette partie s'exécute quand tu lances le fichier ---
inst = generer_instance(n=100, repartition="R", depot="centre", seed=42)
pts = inst["coords"]
demande = inst["demande"]

plt.figure(figsize=(7, 7))

# Clients : taille proportionnelle à la demande
plt.scatter(pts[1:, 0], pts[1:, 1],
            s=demande[1:] * 3,          # taille = demande x 3
            alpha=0.6, edgecolors="k", #linewidths=0.4,
            label="clients")

# Dépôt : taille fixe, en rouge
plt.scatter(pts[0, 0], pts[0, 1], c="red", marker="o", s=150,
            edgecolors="k", label="dépôt", zorder=3)

plt.gca().set_aspect("equal")
plt.legend()
plt.title("Taille des points = demande du client")
plt.show()