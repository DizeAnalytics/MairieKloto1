# Guide de Déploiement sur PythonAnywhere

Ce guide vous explique comment déployer le projet Mairie de Kloto 1 sur PythonAnywhere depuis GitHub.

## Prérequis

- Compte PythonAnywhere : `mariekloto1tg`
- Projet disponible sur GitHub : `https://github.com/DizeAnalytics/MairieKloto1.git`

## Étapes de Déploiement

### 1. Connexion à PythonAnywhere

1. Allez sur https://www.pythonanywhere.com/
2. Connectez-vous avec le compte `mariekloto1tg`
3. Accédez à la console Bash

### 2. Cloner le projet depuis GitHub

```bash
cd ~
git clone https://github.com/DizeAnalytics/MairieKloto1.git
cd MairieKloto1
```

### 3. Créer un environnement virtuel

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configurer les variables d'environnement

Créez un fichier `.env` dans le répertoire du projet (ou configurez directement dans settings.py) :

```bash
nano .env
```

Ajoutez :
```
SECRET_KEY=votre_secret_key_ici
DEBUG=False
ALLOWED_HOSTS=mariekloto1tg.pythonanywhere.com
```

### 6. Modifier settings.py pour la production

Modifiez `mairie_kloto_platform/settings.py` :

```python
import os

# Récupérer SECRET_KEY depuis les variables d'environnement ou utiliser une valeur par défaut
SECRET_KEY = os.environ.get('SECRET_KEY', 'votre-secret-key-production')

# Désactiver DEBUG en production
DEBUG = False

# Ajouter le domaine PythonAnywhere
ALLOWED_HOSTS = ['mariekloto1tg.pythonanywhere.com', 'www.mariekloto1tg.pythonanywhere.com']

# Configuration de la base de données (SQLite est OK pour commencer)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configuration des fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = '/home/mariekloto1tg/MairieKloto1/staticfiles'

# Configuration des fichiers média
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/mariekloto1tg/MairieKloto1/media'
```

### 7. Créer la base de données

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 8. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 9. Configurer le fichier WSGI

1. Allez dans l'onglet **Web** de PythonAnywhere
2. Cliquez sur **WSGI configuration file**
3. Remplacez le contenu par :

```python
import os
import sys

# Ajouter le chemin du projet
path = '/home/mariekloto1tg/MairieKloto1'
if path not in sys.path:
    sys.path.insert(0, path)

# Activer l'environnement virtuel
activate_this = '/home/mariekloto1tg/MairieKloto1/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Configurer les variables d'environnement
os.environ['DJANGO_SETTINGS_MODULE'] = 'mairie_kloto_platform.settings'

# Importer l'application WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 10. Configurer les fichiers statiques et média

Dans l'onglet **Web** de PythonAnywhere :

1. **Static files** :
   - URL: `/static/`
   - Directory: `/home/mariekloto1tg/MairieKloto1/staticfiles`

2. **Media files** :
   - URL: `/media/`
   - Directory: `/home/mariekloto1tg/MairieKloto1/media`

### 11. Configurer le domaine

Dans l'onglet **Web** :
- **Domain**: `mariekloto1tg.pythonanywhere.com`
- **Python version**: Python 3.10

### 12. Redémarrer l'application

Cliquez sur le bouton **Reload** dans l'onglet **Web**

### 13. Tester l'application

Visitez : `https://mariekloto1tg.pythonanywhere.com`

## Commandes utiles pour la maintenance

### Mettre à jour depuis GitHub

```bash
cd ~/MairieKloto1
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Puis redémarrer l'application dans l'onglet **Web**.

### Voir les logs

Dans l'onglet **Web**, section **Error log** pour voir les erreurs.

### Accéder à la console Python

Dans l'onglet **Consoles**, créez une console Bash et :

```bash
cd ~/MairieKloto1
source venv/bin/activate
python manage.py shell
```

## Notes importantes

1. **SECRET_KEY** : Changez la SECRET_KEY en production pour la sécurité
2. **DEBUG** : Toujours mettre `DEBUG = False` en production
3. **Base de données** : SQLite fonctionne pour commencer, mais pour une production sérieuse, considérez PostgreSQL ou MySQL
4. **Fichiers média** : Les fichiers uploadés seront stockés dans `/home/mariekloto1tg/MairieKloto1/media`
5. **Backups** : Configurez des sauvegardes régulières de la base de données

## Dépannage

### Erreur 500
- Vérifiez les logs d'erreur dans l'onglet **Web**
- Vérifiez que tous les chemins sont corrects
- Vérifiez que l'environnement virtuel est activé

### Fichiers statiques non chargés
- Exécutez `python manage.py collectstatic`
- Vérifiez la configuration dans l'onglet **Web**

### Erreurs de migration
- Exécutez `python manage.py migrate`
- Vérifiez que la base de données est accessible
