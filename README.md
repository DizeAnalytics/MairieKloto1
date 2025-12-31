# Plateforme Web de la Mairie de Kloto 1

Plateforme de gestion économique et administrative pour la Mairie de Kloto 1, Kpalimé, Togo.

## Fonctionnalités

- **Gestion des acteurs économiques** : Enregistrement et suivi des entreprises et commerces
- **Institutions financières** : Répertoire des institutions financières partenaires
- **Sites touristiques** : Catalogue des sites touristiques validés
- **Emploi** : Gestion des profils d'emploi (jeunes et retraités)
- **Actualités** : Publication d'actualités municipales
- **Appels d'offres** : Gestion des appels d'offres et candidatures

## Technologies

- Django 6.0+
- Python 3.8+
- SQLite (base de données)
- Bootstrap pour le frontend

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/DizeAnalytics/MairieKloto1.git
cd MairieKloto1
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
venv\Scripts\activate  # Sur Windows
source venv/bin/activate  # Sur Linux/Mac
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Effectuer les migrations :
```bash
python manage.py migrate
```

5. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

6. Lancer le serveur de développement :
```bash
python manage.py runserver
```

## Structure du projet

- `mairie_kloto_platform/` : Configuration principale du projet Django
- `mairie/` : Application principale de gestion municipale
- `acteurs/` : Gestion des acteurs économiques
- `emploi/` : Gestion de l'emploi
- `actualites/` : Gestion des actualités
- `comptes/` : Gestion de l'authentification

## Développement

Pour contribuer au projet, veuillez créer une branche et soumettre une pull request.

## Licence

Propriété de la Mairie de Kloto 1, Togo.

