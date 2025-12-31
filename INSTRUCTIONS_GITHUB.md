# Instructions pour pousser le projet sur GitHub

## ✅ Fichiers créés

J'ai créé les fichiers suivants pour vous aider :
- `.gitignore` : Fichier pour ignorer les fichiers qui ne doivent pas être versionnés (base de données, fichiers Python compilés, etc.)
- `README.md` : Documentation du projet
- `push_to_github.bat` : Script Windows pour automatiser le processus
- `push_to_github.ps1` : Script PowerShell (alternative)

## 📋 Étapes à suivre

### Option 1 : Utiliser le script automatique (RECOMMANDÉ)

1. **Créer le dépôt sur GitHub** (si pas déjà fait) :
   - Aller sur https://github.com/DizeAnalytics
   - Cliquer sur "New repository"
   - Nom : `MairieKloto1`
   - **NE PAS** cocher "Initialize this repository with a README" (on a déjà les fichiers)
   - Cliquer sur "Create repository"

2. **Exécuter le script** :
   - Double-cliquer sur `push_to_github.bat`
   - Ou ouvrir PowerShell dans le dossier et exécuter : `.\push_to_github.bat`

3. **Authentification** :
   - Si demandé, utilisez votre email : `dizeanalytics@gmail.com`
   - Utilisez un **Personal Access Token** (pas votre mot de passe)
   - Pour créer un token : https://github.com/settings/tokens → Generate new token (classic) → cocher `repo` → Generate

### Option 2 : Commandes manuelles

Si le script ne fonctionne pas, ouvrez **Git Bash** ou **PowerShell** dans le dossier du projet et exécutez :

```bash
# Configuration Git (première fois seulement)
git config --global user.email "dizeanalytics@gmail.com"
git config --global user.name "DizeAnalytics"

# Initialiser le dépôt
git init

# Ajouter tous les fichiers
git add .

# Créer le commit
git commit -m "Initial commit: Plateforme web Mairie de Kloto 1"

# Ajouter le remote GitHub
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git

# Renommer la branche en main
git branch -M main

# Pousser vers GitHub
git push -u origin main
```

## 🔐 Authentification GitHub

GitHub n'accepte plus les mots de passe. Vous devez utiliser un **Personal Access Token** :

1. Aller sur : https://github.com/settings/tokens
2. Cliquer sur "Generate new token" → "Generate new token (classic)"
3. Donner un nom : "MairieKloto1"
4. Cocher la permission `repo` (accès complet)
5. Cliquer sur "Generate token"
6. **COPIER LE TOKEN** (vous ne pourrez plus le voir après)
7. Utiliser ce token comme mot de passe lors de `git push`

## ⚠️ Si vous avez des erreurs

### Erreur : "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git
```

### Erreur : "failed to push some refs"
Assurez-vous que le dépôt GitHub est vide ou utilisez :
```bash
git push -u origin main --force
```
⚠️ Attention : `--force` écrase l'historique, utilisez seulement si le dépôt est vide ou si vous savez ce que vous faites.

### Erreur : Git n'est pas reconnu
- Réinstaller Git depuis : https://git-scm.com/download/win
- Redémarrer votre terminal après l'installation

## ✅ Vérification

Après avoir poussé, vérifiez sur GitHub :
- https://github.com/DizeAnalytics/MairieKloto1
- Tous vos fichiers devraient être visibles

## 📝 Commandes utiles pour plus tard

```bash
# Voir l'état des modifications
git status

# Ajouter des modifications
git add .
git commit -m "Description des modifications"
git push

# Récupérer les dernières modifications
git pull
```

