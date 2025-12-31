#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script Python pour pousser le projet sur GitHub
"""
import subprocess
import os
import sys

def run_command(command, description, ignore_errors=False):
    """Exécute une commande et affiche le résultat"""
    print(f"\n[{description}]")
    print(f"Execution: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=not ignore_errors,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode == 0:
            print("OK")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            return True
        print(f"ERREUR: {e}")
        if e.stderr:
            print(f"Erreur: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("Publication sur GitHub: DizeAnalytics/MairieKloto1")
    print("=" * 60)
    
    # Changer vers le répertoire du script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"\nRépertoire de travail: {os.getcwd()}")
    
    commands = [
        ('git config --global user.email "dizeanalytics@gmail.com"', "Configuration email"),
        ('git config --global user.name "DizeAnalytics"', "Configuration nom"),
        ('git init', "Initialisation du dépôt"),
        ('git add .', "Ajout des fichiers"),
        ('git commit -m "Initial commit: Plateforme web Mairie de Kloto 1"', "Création du commit"),
        ('git remote remove origin', "Suppression remote existant (si existe)"),
        ('git remote add origin https://github.com/DizeAnalytics/MairieKloto1.git', "Ajout du remote"),
        ('git branch -M main', "Renommage branche en main"),
    ]
    
    for cmd, desc in commands:
        # Ignorer les erreurs pour certaines commandes
        if "remote remove" in cmd:
            run_command(cmd + " 2>nul", desc)
        else:
            if not run_command(cmd, desc):
                print(f"\n⚠ Erreur lors de: {desc}")
                response = input("Continuer quand même? (o/n): ")
                if response.lower() != 'o':
                    sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Récupération des fichiers existants (si nécessaire)...")
    print("=" * 60)
    
    # Essayer de pull (peut échouer si repo vide, c'est OK)
    pull_result = subprocess.run(
        'git pull origin main --allow-unrelated-histories --no-edit',
        shell=True,
        capture_output=True,
        text=True
    )
    if pull_result.returncode == 0:
        print("OK - Fichiers existants recuperes")
    else:
        print("INFO - Depot vide ou erreur mineure - on continue")
    
    print("\n" + "=" * 60)
    print("PUSH vers GitHub")
    print("=" * 60)
    print("\nATTENTION: Vous devrez vous authentifier avec:")
    print("  - Username: dizeanalytics@gmail.com")
    print("  - Password: Votre Personal Access Token GitHub")
    print("\nAppuyez sur Entree pour continuer...")
    input()
    
    # Essayer avec --force d'abord
    if run_command('git push -u origin main --force', "Push vers GitHub (avec --force)"):
        print("\n" + "=" * 60)
        print("SUCCES! Projet publie sur GitHub")
        print("https://github.com/DizeAnalytics/MairieKloto1")
        print("=" * 60)
    else:
        print("\nTentative sans --force...")
        if run_command('git push -u origin main', "Push vers GitHub (sans --force)"):
            print("\n" + "=" * 60)
            print("SUCCES! Projet publie sur GitHub")
            print("https://github.com/DizeAnalytics/MairieKloto1")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("ECHEC lors du push")
            print("Verifiez vos identifiants et votre connexion")
            print("=" * 60)
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnnulé par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERREUR: {e}")
        sys.exit(1)

