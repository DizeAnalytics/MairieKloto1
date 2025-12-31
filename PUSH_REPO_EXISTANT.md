# 🚀 Pousser vers le dépôt GitHub existant : MairieKloto1

Le dépôt **DizeAnalytics/MairieKloto1** existe déjà sur GitHub. Voici comment y envoyer votre code local.

## Option 1 : Script automatique (RECOMMANDÉ)

Double-cliquer sur le fichier **`PUSH_REPO_EXISTANT.bat`** - il gérera tout automatiquement !

## Option 2 : Commandes manuelles dans Git Bash

### Étape 1 : Ouvrir Git Bash

- Clic droit dans le dossier `C:\Users\MONICA\Desktop\MKloto1`
- Sélectionner **"Git Bash Here"**

### Étape 2 : Configuration Git (première fois seulement)

```bash
git config --global user.email "dizeanalytics@gmail.com"
git config --global user.name "DizeAnalytics"
```

### Étape 3 : Initialiser le dépôt local

```bash
git init
```

### Étape 4 : Ajouter tous les fichiers

```bash
git add .
```

### Étape 5 : Créer le commit

```bash
git commit -m "Initial commit: Plateforme web Mairie de Kloto 1"
```

### Étape 6 : Connecter au dépôt GitHub

```bash
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git
```

**Si erreur "remote origin already exists" :**
```bash
git remote remove origin
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git
```

### Étape 7 : Renommer la branche en main

```bash
git branch -M main
```

### Étape 8 : Récupérer les fichiers existants (si le repo n'est pas vide)

Si le dépôt GitHub contient déjà des fichiers (README, .gitignore, etc.) :

```bash
git pull origin main --allow-unrelated-histories --no-edit
```

Si le dépôt est vide, **ignorer cette étape**.

### Étape 9 : Pousser vers GitHub

```bash
git push -u origin main --force
```

Le `--force` est nécessaire pour écraser l'historique si c'est la première fois que vous poussez.

**Si erreur**, essayez sans `--force` :
```bash
git push -u origin main
```

## Authentification GitHub

Quand Git vous demande de vous connecter :

- **Username** : `dizeanalytics@gmail.com`
- **Password** : Votre **Personal Access Token** (PAS votre mot de passe GitHub)

### Comment créer un Personal Access Token :

1. Aller sur : https://github.com/settings/tokens
2. Cliquer sur **"Generate new token"** → **"Generate new token (classic)"**
3. Donner un nom : `MairieKloto1`
4. Cocher la case **`repo`** (Full control of private repositories)
5. Cliquer sur **"Generate token"** en bas
6. **COPIER LE TOKEN** (vous ne pourrez plus le voir après !)
7. Utiliser ce token comme mot de passe lors de `git push`

## ✅ Vérification

Après le push, vérifiez sur : https://github.com/DizeAnalytics/MairieKloto1

Tous vos fichiers devraient être maintenant sur GitHub !

