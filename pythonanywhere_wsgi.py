# Configuration WSGI pour PythonAnywhere
# Ce fichier peut être utilisé directement dans la configuration WSGI de PythonAnywhere

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
