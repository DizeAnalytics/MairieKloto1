"""
Commande Django personnalisée pour créer un superutilisateur.
Usage: python manage.py create_superadmin --username admin --email admin@example.com --password motdepasse
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée un superutilisateur pour l\'administration Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nom d\'utilisateur du superadmin',
            default='admin'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email du superadmin',
            required=True
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Mot de passe du superadmin',
            required=True
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Ne pas demander de confirmation',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        noinput = options['noinput']

        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f"L'utilisateur '{username}' existe déjà!")
            )
            if not noinput:
                response = input("Voulez-vous réinitialiser le mot de passe? (o/n): ").strip().lower()
                if response != 'o':
                    self.stdout.write(self.style.ERROR("Opération annulée."))
                    return
            user = User.objects.get(username=username)
        else:
            try:
                user = User.objects.create_user(username=username, email=email)
                self.stdout.write(
                    self.style.SUCCESS(f"Utilisateur '{username}' créé.")
                )
            except IntegrityError:
                self.stdout.write(
                    self.style.ERROR(f"Erreur lors de la création de l'utilisateur '{username}'.")
                )
                return

        # Définir le mot de passe et les permissions
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuperadmin '{username}' créé/modifié avec succès!\n"
                f"   Username: {username}\n"
                f"   Email: {email}\n"
                f"\nVous pouvez maintenant vous connecter à l'admin via:\n"
                f"   http://localhost:8000/Securelogin/"
            )
        )

