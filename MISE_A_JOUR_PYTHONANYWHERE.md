# Guide de Mise à Jour sur PythonAnywhere

Ce guide contient toutes les commandes nécessaires pour mettre à jour le site hébergé sur PythonAnywhere après avoir poussé des modifications sur GitHub.

## Compte PythonAnywhere
- **Compte** : `mariekloto1tg`
- **Domaine** : `mariekloto1tg.pythonanywhere.com`
- **Répertoire projet** : `/home/mariekloto1tg/MairieKloto1`
- **Environnement virtuel** : `/home/mariekloto1tg/MairieKloto1/venv`

---

## 🔄 Commandes de Mise à Jour (À exécuter dans l'ordre)

### Étape 1 : Ouvrir une Console Bash sur PythonAnywhere

1. Connectez-vous à https://www.pythonanywhere.com
2. Cliquez sur l'onglet **"Consoles"** (en haut)
3. Créez ou ouvrez une **Bash console**

---

### Étape 2 : Aller dans le répertoire du projet

```bash
cd /home/mariekloto1tg/MairieKloto1
```

---

### Étape 3 : Activer l'environnement virtuel

```bash
source venv/bin/activate
```

Vous devriez voir `(venv)` au début de votre ligne de commande.

---

### Étape 4 : Récupérer les dernières modifications depuis GitHub

```bash
git pull origin main
```

Cette commande télécharge toutes les modifications que vous avez poussées sur GitHub.

---

### Étape 5 : Mettre à jour les dépendances Python

```bash
pip install --upgrade -r requirements.txt
```

Cette commande installe ou met à jour tous les packages listés dans `requirements.txt` (notamment Django si nécessaire).

---

### Étape 6 : Appliquer les migrations de base de données

```bash
python manage.py migrate
```

Cette commande applique toutes les nouvelles migrations (comme celles pour `VisiteSite` et `EtatCivilPage`).

---

### Étape 7 : Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

Cette commande copie tous les fichiers statiques (CSS, JavaScript, images) dans le dossier `staticfiles` pour qu'ils soient servis par le serveur web.

---

### Étape 8 : Vérifier qu'il n'y a pas d'erreurs

```bash
python manage.py check
```

Cette commande vérifie la configuration Django et affiche des erreurs éventuelles.

---

### Étape 9 : Recharger l'application web

**IMPORTANT :** Cette étape se fait via l'interface web de PythonAnywhere, pas en ligne de commande.

1. Retournez sur https://www.pythonanywhere.com
2. Cliquez sur l'onglet **"Web"** (en haut)
3. Dans la section de votre application web (`mariekloto1tg.pythonanywhere.com`), cliquez sur le bouton vert **"Reload"** ou **"Reload mariekloto1tg.pythonanywhere.com"**

Cela redémarre votre application Django avec les nouvelles modifications.

---

## ✅ Vérification finale

Après avoir rechargé l'application, visitez :
- https://mariekloto1tg.pythonanywhere.com/

Vérifiez que :
- Le site s'affiche correctement
- Les nouvelles pages (`/etat-civil/`, `/contactez-nous/`) sont accessibles
- L'administration Django fonctionne (`/Securelogin/`)

---

## 📝 Script de Mise à Jour Automatique (Optionnel)

Vous pouvez créer un script pour automatiser toutes ces étapes. Créez un fichier `update.sh` :

```bash
#!/bin/bash
cd /home/mariekloto1tg/MairieKloto1
source venv/bin/activate
git pull origin main
pip install --upgrade -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check
echo "✅ Mise à jour terminée ! N'oubliez pas de recharger l'application via l'interface Web de PythonAnywhere."
```

Pour l'exécuter :
```bash
chmod +x update.sh
./update.sh
```

---

## ⚠️ En cas de problème

### Si `git pull` échoue :
- Vérifiez que vous êtes bien connecté : `git remote -v`
- Vérifiez que vous avez les droits d'accès au dépôt GitHub

### Si les migrations échouent :
- Vérifiez les erreurs : `python manage.py migrate --verbosity 2`
- En cas de conflit de migration, consultez la documentation Django

### Si le site ne se charge pas après le reload :
- Vérifiez les logs d'erreur dans l'onglet **"Web"** de PythonAnywhere (section **"Error log"**)
- Vérifiez que tous les fichiers sont bien présents : `ls -la`
- Vérifiez que l'environnement virtuel est correctement activé

### Si des fichiers statiques ne s'affichent pas :
- Vérifiez que `collectstatic` a bien fonctionné : `ls staticfiles/`
- Vérifiez la configuration des fichiers statiques dans l'onglet **"Web"**

---

## 🔗 Liens utiles

- **Interface PythonAnywhere** : https://www.pythonanywhere.com
- **Votre site** : https://mariekloto1tg.pythonanywhere.com
- **Dépôt GitHub** : https://github.com/DizeAnalytics/MairieKloto1

---

**Date de dernière mise à jour de ce guide** : 2026-01-09
