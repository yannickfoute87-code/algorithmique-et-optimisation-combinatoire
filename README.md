# algorithmique-et-optimisation-combinatoire

## Accéder à l'environnement de travail

Toutes les commandes se tapent dans un terminal **PowerShell** et peuvent être copiées-collées telles quelles.

Les chemins ci-dessous correspondent à l'installation d'Ann (environnement virtuel dans `C:\Users\annf7\algo_env`). Sur une autre machine, remplacer ce chemin par le sien.

### 1. Se placer dans le dossier du projet

```powershell
cd "C:\Users\annf7\algo_env\Algo-optimisation projet\algorithmique-et-optimisation-combinatoire"
```

Les commandes `git` ne fonctionnent que depuis ce dossier. En dehors, elles renvoient `fatal: not a git repository`.

### 2. Activer l'environnement virtuel

```powershell
& "C:\Users\annf7\algo_env\Scripts\Activate.ps1"
```

L'environnement est actif quand `(algo_env)` apparaît au début de la ligne du terminal.

Si PowerShell répond que l'exécution de scripts est désactivée, lancer cette commande puis recommencer l'activation :

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
```

Pour quitter l'environnement :

```powershell
deactivate
```

### 3. Choisir le noyau du notebook dans VS Code

Le terminal ne suffit pas pour les fichiers `.ipynb`, il faut aussi indiquer l'environnement au notebook :

1. Ouvrir le notebook, puis cliquer sur **Sélectionner le noyau** en haut à droite.
2. Cliquer sur **Environnements Python...**
3. Choisir **algo_env**.

Si `algo_env` n'est pas dans la liste, coller ce chemin dans la barre de recherche :

```
C:\Users\annf7\algo_env\Scripts\python.exe
```

### 4. Récupérer le travail du groupe

À faire au début de chaque séance, avant de modifier quoi que ce soit :

```powershell
git pull
```

Pour voir ce qui a changé sur GitHub avant de l'appliquer :

```powershell
git fetch
git log --oneline --stat HEAD..origin/main
```

### 5. Envoyer son travail sur GitHub

Enregistrer les fichiers (Ctrl+S), puis :

```powershell
git status
git add test.ipynb
git commit -m "Description courte de la modification"
git push
```

- `git status` affiche les fichiers modifiés.
- Dans `git add`, mettre le ou les fichiers à envoyer, séparés par un espace.
- Si `git push` est refusé avec le message `rejected`, quelqu'un a envoyé entre-temps : lancer `git pull`, puis de nouveau `git push`.

### Résumé d'une séance

```powershell
cd "C:\Users\annf7\algo_env\Algo-optimisation projet\algorithmique-et-optimisation-combinatoire"
& "C:\Users\annf7\algo_env\Scripts\Activate.ps1"
git pull
```

Puis, une fois le travail terminé :

```powershell
git add test.ipynb
git commit -m "Description courte de la modification"
git push
```
#######AXEL########################
sous le dossier data, juste en dessous du dossier X bks_X.json contient les meilleurs coûts connus (BKS) des instances X, par exemple 27591 pour X-n101-k25. On s’en servira pour calculer le gap, sans avoir besoin de fichiers .sol
Algorithme Tabou dans le branch tabou du projet git 
Les lignes que tu as recopiées sont l’ancienne explication, celle de la première sortie (coût 41520, gap 50.48 %). Voici celle de la nouvelle sortie.

Ce que dit la sortie

(tabou_CVRP.py) départ : coût 41944 | gap : 52.02 % : la solution de départ (plus proche voisin). Le coût est un peu différent de 41520 parce que les distances sont maintenant arrondies à l’entier, comme dans les BKS.
(tabou1_CVRP.py) arrivée : coût 31263 | gap : 13.31 % : après les déplacements de clients, le coût est passé de 41944 à 31263. Le gap est tombé de 52 % à 13,31 %. Ça veut dire que l’amélioration marche.
tournées : 26 : toujours 26 camions, le code n’a supprimé aucune tournée.
valide : True : la solution reste correcte, chaque client est servi une fois et aucune capacité n’est dépassée.

(tabou2_CVRP.py) Graphique 1 (départ) : la solution de départ, coût 41944, gap 52 %. C’est la moins bonne.
Graphique 2 (arrivée) : la meilleure solution que ton code a trouvée, coût 31263, gap 13,31 %. Ce n’est pas l’optimale, juste la meilleure de ton algorithme.
Graphique 3 (courbe) : le coût qui baisse au fil des déplacements. La ligne rouge en pointillés est le coût de la meilleure solution connue (BKS), 27591. C’est la cible, pas une solution dessinée.

(tabou3_CVRP.py) le tabou tu ne cherches pas la solution optimale, mais une très bonne solution.

Pourquoi. Le CVRP est NP-difficile (c’est ce que tu dois prouver dans le livrable de modélisation). Pour 100 clients, aucune méthode ne peut tout essayer. Le tabou est une métaheuristique : elle trouve vite une solution proche de l’optimale, sans garantir que c’est la meilleure. Pour atteindre le coût optimal, il faudrait une méthode exacte (le PLNE), très lente dès que l’instance grandit.

Ce que demande ton sujet.

Un solveur capable de traiter des instances de taille réaliste.
Le gap par rapport à la meilleure solution connue.
Un gap sous 7 % pour ne pas être limité à la note B.

Le gap est justement la mesure de la distance entre ta solution et l’optimale. Pour X-n101-k25, tu dois donc descendre sous environ 29 520. Si tu t’en approchais encore plus, ce serait un bonus.

Ton rôle. Ton tabou doit donner une solution proche de l’optimale, sur plusieurs instances, avec un gap bas. Le PLNE du livrable de modélisation sert à décrire le problème exactement, pas à le résoudre ici.
##############################################################