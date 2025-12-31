"""
Script pour créer un superutilisateur Django de manière non-interactive.
Usage: python create_superadmin.py
"""
import os
import sys
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mairie_kloto_platform.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superadmin():
    """Crée un superutilisateur si il n'existe pas déjà."""
    
    # Informations du superadmin (vous pouvez les modifier)
    username = input("Nom d'utilisateur (admin): ").strip() or "admin"
    email = input("Email: ").strip()
    
    if not email:
        print("L'email est requis!")
        sys.exit(1)
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=username).exists():
        print(f"L'utilisateur '{username}' existe déjà!")
        response = input("Voulez-vous réinitialiser le mot de passe? (o/n): ").strip().lower()
        if response != 'o':
            sys.exit(0)
        user = User.objects.get(username=username)
    else:
        user = User.objects.create_user(username=username, email=email)
    
    # Demander le mot de passe
    import getpass
    password = getpass.getpass("Mot de passe: ")
    password_confirm = getpass.getpass("Confirmer le mot de passe: ")
    
    if password != password_confirm:
        print("Les mots de passe ne correspondent pas!")
        sys.exit(1)
    
    if len(password) < 8:
        print("Le mot de passe doit contenir au moins 8 caractères!")
        sys.exit(1)
    
    # Définir le mot de passe et les permissions
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    
    print(f"\n✅ Superadmin '{username}' créé avec succès!")
    print(f"   Email: {email}")
    print(f"\n🔐 Vous pouvez maintenant vous connecter à l'admin via:")
    print(f"   http://localhost:8000/Securelogin/")

if __name__ == '__main__':
    try:
        create_superadmin()
    except KeyboardInterrupt:
        print("\n\nOpération annulée.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)

