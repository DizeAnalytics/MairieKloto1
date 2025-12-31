# Instructions pour pousser le projet sur GitHub

## Prérequis

1. **Installer Git** si ce n'est pas déjà fait :
   - Télécharger depuis : https://git-scm.com/download/win
   - Installer en suivant les instructions

2. **Créer un compte GitHub** (si pas déjà fait) avec l'email : dizeanalytics@gmail.com

3. **Créer le dépôt sur GitHub** :
   - Aller sur https://github.com/DizeAnalytics
   - Cliquer sur "New repository"
   - Nom : `MairieKloto1`
   - Description : "Plateforme web de gestion pour la Mairie de Kloto 1"
   - Public ou Private (selon votre choix)
   - **NE PAS** initialiser avec README, .gitignore ou license (on a déjà les fichiers)

## Commandes Git à exécuter

Ouvrez PowerShell ou Git Bash dans le dossier du projet (`C:\Users\MONICA\Desktop\MKloto1`) et exécutez les commandes suivantes :

### 1. Configurer Git (première fois seulement)
```powershell
git config --global user.email "dizeanalytics@gmail.com"
git config --global user.name "DizeAnalytics"
```

### 2. Initialiser le dépôt Git
```powershell
git init
```

### 3. Ajouter tous les fichiers
```powershell
git add .
```

### 4. Faire le premier commit
```powershell
git commit -m "Initial commit: Plateforme web Mairie de Kloto 1"
```

### 5. Ajouter le remote GitHub
```powershell
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git
```

### 6. Pousser vers GitHub
```powershell
git branch -M main
git push -u origin main
```

## Authentification GitHub

Si vous êtes invité à vous authentifier :
- Utilisez votre email : `dizeanalytics@gmail.com`
- Utilisez un **Personal Access Token** (pas votre mot de passe)
- Pour créer un token : GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
- Permissions nécessaires : `repo` (accès complet aux dépôts)

## Commandes utiles pour plus tard

### Voir l'état des fichiers
```powershell
git status
```

### Ajouter des modifications
```powershell
git add .
git commit -m "Description des modifications"
git push
```

### Récupérer les dernières modifications
```powershell
git pull
```

