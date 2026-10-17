import random
import tkinter as tk
from tkinter import messagebox


class JeuNombreMystereGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Jeu du Nombre Mystère")
        self.root.geometry("500x550")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        # Variables de jeu
        self.min_val = 1
        self.max_val = 100
        self.nombre_mystere = 0
        self.joueurs = ["Joueur 1", "Joueur 2"]
        self.tour = 0
        self.tentatives = {0: 0, 1: 0}
        self.jeu_en_cours = False

        self.creer_interface()

    def creer_interface(self):
        # Titre
        self.lbl_titre = tk.Label(
            self.root,
            text="🎯 NOMBRE MYSTÈRE 🎯",
            font=("Helvetica", 20, "bold"),
            bg="#1e1e2e",
            fg="#cba6f7",
        )
        self.lbl_titre.pack(pady=15)

        # Cadre Configuration
        self.frame_config = tk.LabelFrame(
            self.root,
            text=" Configuration ",
            font=("Helvetica", 11, "bold"),
            bg="#1e1e2e",
            fg="#89b4fa",
            padx=15,
            pady=10,
        )
        self.frame_config.pack(fill="x", padx=20, pady=5)

        # Noms des joueurs
        tk.Label(
            self.frame_config,
            text="Joueur 1 :",
            bg="#1e1e2e",
            fg="#cdd6f4",
        ).grid(row=0, column=0, sticky="w", pady=2)
        self.ent_j1 = tk.Entry(
            self.frame_config,
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="white",
            width=12,
        )
        self.ent_j1.insert(0, "Alice")
        self.ent_j1.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(
            self.frame_config,
            text="Joueur 2 :",
            bg="#1e1e2e",
            fg="#cdd6f4",
        ).grid(row=0, column=2, sticky="w", pady=2)
        self.ent_j2 = tk.Entry(
            self.frame_config,
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="white",
            width=12,
        )
        self.ent_j2.insert(0, "Bob")
        self.ent_j2.grid(row=0, column=3, padx=5, pady=2)

        # Intervalle
        tk.Label(
            self.frame_config,
            text="Borne Min :",
            bg="#1e1e2e",
            fg="#cdd6f4",
        ).grid(row=1, column=0, sticky="w", pady=5)
        self.ent_min = tk.Entry(
            self.frame_config,
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="white",
            width=12,
        )
        self.ent_min.insert(0, "1")
        self.ent_min.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(
            self.frame_config,
            text="Borne Max :",
            bg="#1e1e2e",
            fg="#cdd6f4",
        ).grid(row=1, column=2, sticky="w", pady=5)
        self.ent_max = tk.Entry(
            self.frame_config,
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="white",
            width=12,
        )
        self.ent_max.insert(0, "100")
        self.ent_max.grid(row=1, column=3, padx=5, pady=5)

        # Bouton Lancer
        self.btn_lancer = tk.Button(
            self.frame_config,
            text="🚀 Démarrer la partie",
            font=("Helvetica", 10, "bold"),
            bg="#a6e3a1",
            fg="#11111b",
            activebackground="#94e2d5",
            command=self.demarrer_partie,
        )
        self.btn_lancer.grid(row=2, column=0, columnspan=4, pady=10)

        # Zone de Jeu (Zone d'affichage interactif)
        self.frame_jeu = tk.Frame(self.root, bg="#181825", bd=2, relief="groove")
        self.frame_jeu.pack(fill="both", expand=True, padx=20, pady=10)

        self.lbl_tour = tk.Label(
            self.frame_jeu,
            text="Cliquez sur 'Démarrer' pour jouer",
            font=("Helvetica", 12, "bold"),
            bg="#181825",
            fg="#f9e2af",
        )
        self.lbl_tour.pack(pady=10)

        self.lbl_indice = tk.Label(
            self.frame_jeu,
            text="❓",
            font=("Helvetica", 16, "bold"),
            bg="#181825",
            fg="#89dceb",
        )
        self.lbl_indice.pack(pady=5)

        # Saisie de la proposition
        self.ent_proposition = tk.Entry(
            self.frame_jeu,
            font=("Helvetica", 16),
            bg="#313244",
            fg="#cdd6f4",
            justify="center",
            width=8,
            state="disabled",
        )
        self.ent_proposition.pack(pady=5)
        self.ent_proposition.bind("<Return>", lambda e: self.valider_proposition())

        self.btn_valider = tk.Button(
            self.frame_jeu,
            text="Deviner !",
            font=("Helvetica", 11, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            state="disabled",
            command=self.valider_proposition,
        )
        self.btn_valider.pack(pady=5)

        # Zone d'animation / Confettis (Canvas)
        self.canvas_anim = tk.Canvas(
            self.frame_jeu, bg="#181825", highlightthickness=0, height=80
        )
        self.canvas_anim.pack(fill="x", padx=10, pady=5)

    def demarrer_partie(self):
        try:
            self.min_val = int(self.ent_min.get())
            self.max_val = int(self.ent_max.get())
            if self.min_val >= self.max_val:
                messagebox.showerror(
                    "Erreur", "La borne min doit être inférieure à la borne max !"
                )
                return
        except ValueError:
            messagebox.showerror(
                "Erreur", "Veuillez entrer des nombres entiers valides."
            )
            return

        self.joueurs[0] = self.ent_j1.get().strip() or "Joueur 1"
        self.joueurs[1] = self.ent_j2.get().strip() or "Joueur 2"

        self.nombre_mystere = random.randint(self.min_val, self.max_val)
        self.tour = 0
        self.tentatives = {0: 0, 1: 0}
        self.jeu_en_cours = True

        self.ent_proposition.config(state="normal")
        self.btn_valider.config(state="normal")
        self.ent_proposition.focus()

        self.maj_interface_tour()

    def maj_interface_tour(self):
        joueur_actuel = self.joueurs[self.tour]
        couleur = "#f38ba8" if self.tour == 0 else "#89b4fa"
        self.lbl_tour.config(
            text=f"À toi de jouer : {joueur_actuel} !", fg=couleur
        )
        self.lbl_indice.config(
            text=f"Devine un nombre entre {self.min_val} et {self.max_val}",
            fg="#cdd6f4",
        )
        self.ent_proposition.delete(0, tk.END)

    def secouer_fenetre(self):
        """Animation de secousse si la valeur est fausse."""
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        for i in range(4):
            self.root.geometry(f"+{x+10}+{y}")
            self.root.update()
            self.root.after(20)
            self.root.geometry(f"+{x-10}+{y}")
            self.root.update()
            self.root.after(20)
        self.root.geometry(f"+{x}+{y}")

    def valider_proposition(self):
        if not self.jeu_en_cours:
            return

        try:
            val = int(self.ent_proposition.get())
        except ValueError:
            self.lbl_indice.config(
                text="⚠️ Saisis un nombre entier !", fg="#fab387"
            )
            return

        self.tentatives[self.tour] += 1

        if val < self.nombre_mystere:
            self.lbl_indice.config(
                text=f"📈 C'est PLUS grand que {val} !", fg="#f9e2af"
            )
            self.secouer_fenetre()
            self.tour = 1 - self.tour
            self.maj_interface_tour()
        elif val > self.nombre_mystere:
            self.lbl_indice.config(
                text=f"📉 C'est PLUS PETIT que {val} !", fg="#f9e2af"
            )
            self.secouer_fenetre()
            self.tour = 1 - self.tour
            self.maj_interface_tour()
        else:
            self.victoire()

    def victoire(self):
        self.jeu_en_cours = False
        gagnant = self.joueurs[self.tour]
        nb_t = self.tentatives[self.tour]

        self.lbl_tour.config(
            text=f"🎉 VICTOIRE DE {gagnant.upper()} ! 🎉", fg="#a6e3a1"
        )
        self.lbl_indice.config(
            text=f"Le nombre était bien {self.nombre_mystere} !\nTrouvé en {nb_t} tentative(s).",
            fg="#a6e3a1",
        )

        self.ent_proposition.config(state="disabled")
        self.btn_valider.config(state="disabled")

        # Animation Confettis
        self.animer_confettis()

    def animer_confettis(self):
        self.canvas_anim.delete("all")
        couleurs = ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#89b4fa", "#cba6f7"]
        particules = []

        for _ in range(50):
            x = random.randint(10, 440)
            y = random.randint(0, 20)
            r = random.randint(3, 7)
            c = random.choice(couleurs)
            p = self.canvas_anim.create_oval(x, y, x + r, y + r, fill=c, outline="")
            particules.append((p, random.randint(2, 5)))

        def faire_tomber():
            encore = False
            for p, vitesse in particules:
                self.canvas_anim.move(p, 0, vitesse)
                coords = self.canvas_anim.coords(p)
                if coords and coords[1] < 80:
                    encore = True
            if encore:
                self.root.after(30, faire_tomber)

        faire_tomber()


if __name__ == "__main__":
    root = tk.Tk()
    app = JeuNombreMystereGUI(root)
    root.mainloop()