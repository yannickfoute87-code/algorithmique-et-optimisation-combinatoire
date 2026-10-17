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
