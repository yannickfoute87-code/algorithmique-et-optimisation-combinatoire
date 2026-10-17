import random


def lancer_jeu():
    print("==========================================")
    print("  BIENVENUE AU JEU DU NOMBRE MYSTÈRE ! 🎯")
    print("==========================================")

    # Étape 1 : Définition de l'intervalle
    try:
        min_val = int(
            input("Entrez la borne inférieure de l'intervalle : ")
        )
        max_val = int(
            input("Entrez la borne supérieure de l'intervalle : ")
        )

        if min_val >= max_val:
            print(
                "❌ La borne inférieure doit être strictement inférieure à la borne supérieure."
            )
            return
    except ValueError:
        print("❌ Veuillez entrer des nombres entiers valides.")
        return

    # Génération du nombre aléatoire
    nombre_mystere = random.randint(min_val, max_val)
    print(
        f"\n✨ Un nombre mystère a été choisi entre {min_val} et {max_val} !"
    )
    print("À vous de jouer.\n")

    # Demande des noms des joueurs
    joueur1 = input("Nom du Joueur 1 : ").strip() or "Joueur 1"
    joueur2 = input("Nom du Joueur 2 : ").strip() or "Joueur 2"

    joueurs = [joueur1, joueur2]
    tour = 0  # 0 pour joueur1, 1 pour joueur2
    trouve = False
    tentatives = {joueur1: 0, joueur2: 0}

    # Étape 2 : Boucle principale du jeu
    while not trouve:
        joueur_actuel = joueurs[tour]
        print(f"--- Tour de {joueur_actuel} ---")

        try:
            saisie = input(
                f"[{joueur_actuel}] Devinez le nombre : "
            ).strip()
            proposition = int(saisie)
        except ValueError:
            print("⚠️ Entrée invalide. Veuillez entrer un nombre entier.\n")
            continue

        tentatives[joueur_actuel] += 1

        # Étape 3 : Vérification de la proposition
        if proposition < min_val or proposition > max_val:
            print(
                f"⚠️ Attention, votre nombre est en dehors de l'intervalle ({min_val} - {max_val}) !\n"
            )
        elif proposition < nombre_mystere:
            print("📉 C'est PLUS !\n")
        elif proposition > nombre_mystere:
            print("📈 C'est MOINS !\n")
        else:
            trouve = True
            print("==========================================")
            print(
                f"🎉 BRAVO {joueur_actuel} ! Tu as trouvé le nombre mystère ({nombre_mystere}) !"
            )
            print(
                f"🏆 Victoire en {tentatives[joueur_actuel]} tentatives pour {joueur_actuel}."
            )
            print("==========================================")
            break

        # Alternance des joueurs
        tour = 1 - tour


# Lancement du jeu
if __name__ == "__main__":
    lancer_jeu()