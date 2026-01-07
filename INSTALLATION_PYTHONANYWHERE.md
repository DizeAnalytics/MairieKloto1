# Installation sur PythonAnywhere - Guide Rapide

## Problème : "No matching distribution found for Django>=6.0,<7.0"

### Solution

Sur PythonAnywhere, utilisez le fichier `requirements-pythonanywhere.txt` qui contient Django 4.2.16 (compatible Python 3.8+).

## Commandes à exécuter

```bash
# 1. Aller dans le dossier du projet
cd ~/MairieKloto1

# 2. Activer l'environnement virtuel
source venv/bin/activate

# 3. Mettre à jour pip
pip install --upgrade pip setuptools wheel

# 4. Installer les dépendances avec la version compatible
pip install -r requirements-pythonanywhere.txt

# OU si vous préférez installer manuellement :
pip install Django==4.2.16
pip install Pillow>=10.0.0
pip install django-admin-interface==0.32.0
pip install django-colorfield>=0.9.0
pip install reportlab>=4.0.0
```

## Vérification

```bash
# Vérifier que Django est installé
python -c "import django; print(django.get_version())"
# Devrait afficher : 4.2.16
```

## Si l'erreur persiste

1. **Vérifiez la version de Python** :
   ```bash
   python3 --version
   ```
   - Python 3.8, 3.9, 3.10 ou 3.11 fonctionnent avec Django 4.2.16

2. **Réinstallez pip** :
   ```bash
   python3 -m pip install --upgrade pip
   ```

3. **Installez Django directement** :
   ```bash
   pip install Django==4.2.16 --no-cache-dir
   ```

4. **Vérifiez l'environnement virtuel** :
   ```bash
   which python
   # Devrait pointer vers : /home/mariekloto1tg/MairieKloto1/venv/bin/python
   ```
