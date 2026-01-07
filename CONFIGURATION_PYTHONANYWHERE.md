# Configuration PythonAnywhere - Guide Étape par Étape

## Étape 1 : Configurer le WSGI

1. **Connectez-vous** à https://www.pythonanywhere.com avec le compte `mariekloto1tg`

2. **Allez dans l'onglet "Web"** (en haut de la page)

3. **Cliquez sur "WSGI configuration file"** (lien bleu dans la section "Code")

4. **Remplacez TOUT le contenu** du fichier par :

```python
import os
import sys

# Ajouter le chemin du projet
path = '/home/mariekloto1tg/MairieKloto1'
if path not in sys.path:
    sys.path.insert(0, path)

# Activer l'environnement virtuel
activate_this = '/home/mariekloto1tg/MairieKloto1/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Configurer les variables d'environnement Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mairie_kloto_platform.settings'

# Importer l'application WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. **Cliquez sur le bouton vert "Save"** en haut à droite

## Étape 2 : Configurer les Fichiers Statiques

Dans le même onglet **Web**, descendez jusqu'à la section **"Static files"** :

1. **Cliquez sur le bouton "+ Add a new static files mapping"**

2. **Remplissez les champs** :
   - **URL** : `/static/`
   - **Directory** : `/home/mariekloto1tg/MairieKloto1/staticfiles`

3. **Cliquez sur le bouton vert "Save"**

## Étape 3 : Configurer les Fichiers Média

Toujours dans la section **"Static files"** :

1. **Cliquez à nouveau sur "+ Add a new static files mapping"**

2. **Remplissez les champs** :
   - **URL** : `/media/`
   - **Directory** : `/home/mariekloto1tg/MairieKloto1/media`

3. **Cliquez sur le bouton vert "Save"**

## Étape 4 : Vérifier la Configuration du Domaine

Dans l'onglet **Web**, section **"Web app"** :

1. Vérifiez que **"Domain"** est : `mariekloto1tg.pythonanywhere.com`
2. Vérifiez que **"Python version"** est : `Python 3.10` (ou la version que vous avez utilisée)

## Étape 5 : Redémarrer l'Application

1. **Descendez tout en bas** de la page Web
2. **Cliquez sur le gros bouton vert "Reload mariekloto1tg.pythonanywhere.com"**
3. Attendez quelques secondes que le rechargement se termine

## Étape 6 : Vérifier que tout fonctionne

1. **Visitez** : `https://mariekloto1tg.pythonanywhere.com`
2. Vous devriez voir la page d'accueil de la Mairie de Kloto 1

## En cas d'erreur

### Erreur 500
1. Allez dans l'onglet **Web**
2. Cliquez sur **"Error log"** (lien en haut)
3. Lisez les messages d'erreur pour identifier le problème

### Fichiers statiques non chargés
1. Vérifiez que vous avez bien exécuté : `python manage.py collectstatic`
2. Vérifiez que les chemins dans "Static files" sont corrects
3. Redémarrez l'application

### Erreur de module non trouvé
1. Vérifiez que l'environnement virtuel est bien activé dans le WSGI
2. Vérifiez que tous les packages sont installés : `pip list`

## Commandes utiles dans la console

Si vous devez faire des modifications :

```bash
cd ~/MairieKloto1
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

Puis redémarrez l'application dans l'onglet Web.
