# 🚀 Commandes à exécuter pour pousser sur GitHub

## Étape 1 : Créer le dépôt sur GitHub

1. Aller sur : https://github.com/DizeAnalytics
2. Cliquer sur le bouton vert **"New"** ou **"New repository"**
3. Nom du dépôt : **MairieKloto1**
4. **NE PAS** cocher "Add a README file"
5. Cliquer sur **"Create repository"**

## Étape 2 : Ouvrir Git Bash

- Clic droit dans le dossier `C:\Users\MONICA\Desktop\MKloto1`
- Sélectionner **"Git Bash Here"**

OU

- Ouvrir Git Bash
- Taper : `cd /c/Users/MONICA/Desktop/MKloto1`

## Étape 3 : Copier-coller ces commandes une par une

```bash
git config --global user.email "dizeanalytics@gmail.com"
```

```bash
git config --global user.name "DizeAnalytics"
```

```bash
git init
```

```bash
git add .
```

```bash
git commit -m "Initial commit: Plateforme web Mairie de Kloto 1"
```

```bash
git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git
```

```bash
git branch -M main
```

```bash
git push -u origin main
```

## Étape 4 : Authentification

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
7. Utiliser ce token comme mot de passe

## ✅ C'est terminé !

Vérifiez sur : https://github.com/DizeAnalytics/MairieKloto1

