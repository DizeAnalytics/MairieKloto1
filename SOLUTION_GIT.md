# Solution : Problème de compatibilité Git

## Problème détecté

Git installé sur votre système n'est pas compatible avec votre version de Windows. L'erreur indique :
> "Cette version de git.exe n'est pas compatible avec la version de Windows actuellement exécutée"

## Solutions

### Option 1 : Réinstaller Git (RECOMMANDÉ)

1. **Désinstaller l'ancienne version** :
   - Panneau de configuration → Programmes → Désinstaller Git

2. **Télécharger et installer la dernière version** :
   - Aller sur : https://git-scm.com/download/win
   - Télécharger la version 64-bit pour Windows
   - Installer avec les paramètres par défaut
   - **Redémarrer votre ordinateur** après l'installation

3. **Vérifier l'installation** :
   - Ouvrir PowerShell
   - Taper : `git --version`
   - Vous devriez voir quelque chose comme : `git version 2.x.x`

4. **Exécuter les commandes** :
   - Ouvrir Git Bash dans le dossier `C:\Users\MONICA\Desktop\MKloto1`
   - Exécuter les commandes du fichier `COMMANDES_GIT.txt`

### Option 2 : Utiliser GitHub Desktop (PLUS SIMPLE)

GitHub Desktop est une interface graphique qui gère Git automatiquement :

1. **Télécharger GitHub Desktop** :
   - https://desktop.github.com/
   - Installer et se connecter avec votre compte GitHub (dizeanalytics@gmail.com)

2. **Publier le projet** :
   - Fichier → Add Local Repository
   - Sélectionner le dossier `C:\Users\MONICA\Desktop\MKloto1`
   - Si demandé, créer un dépôt Git (oui)
   - Publier → Nom : `MairieKloto1` → Publier

### Option 3 : Utiliser Visual Studio Code

Si vous utilisez VS Code :

1. **Installer l'extension Git** (déjà incluse)
2. **Ouvrir le dossier** dans VS Code
3. **Source Control** (icône Git à gauche)
4. **Cliquer sur "Publish to GitHub"**
5. **Suivre les instructions**

## Commandes à exécuter (après réinstallation de Git)

Une fois Git réinstallé, ouvrez **Git Bash** dans le dossier du projet et exécutez :

```bash
# Configuration
git config --global user.email "dizeanalytics@gmail.com"
git config --global user.name "DizeAnalytics"

# Initialisation
git init
git add .
git commit -m "Initial commit: Plateforme web Mairie de Kloto 1"

# Connexion à GitHub (créer le dépôt sur GitHub d'abord !)
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git
git branch -M main
git push -u origin main
```

## Recommandation

Je recommande **GitHub Desktop** car c'est le plus simple et le plus visuel. Vous n'avez pas besoin de connaître les commandes Git.

