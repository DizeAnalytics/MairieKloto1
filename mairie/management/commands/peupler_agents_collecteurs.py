"""
Commande Django pour peupler la base avec des agents collecteurs de taxes.
Usage: python manage.py peupler_agents_collecteurs
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

from mairie.models import AgentCollecteur, EmplacementMarche


class Command(BaseCommand):
    help = "Peuple la base avec des agents collecteurs de taxes de démonstration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recréer les agents même si des enregistrements existent déjà (même matricule).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Supprimer tous les agents collecteurs avant de peupler (à utiliser avec précaution).",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)
        clear = options.get("clear", False)

        if clear:
            self.stdout.write(self.style.WARNING("Suppression des agents collecteurs existants..."))
            AgentCollecteur.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Agents supprimés."))

        # Récupérer les emplacements existants pour les assigner
        emplacements = list(EmplacementMarche.objects.all())
        if not emplacements:
            self.stdout.write(
                self.style.WARNING(
                    "Aucun emplacement marché trouvé. "
                    "Créez d'abord des emplacements avec la commande peupler_contribuables_marche."
                )
            )
            return

        # Données des agents collecteurs
        agents_data = [
            {
                "username": "agent.koffi",
                "email": "koffi.adjovi@mairiekloto1.tg",
                "matricule": "AGT-2025-001",
                "nom": "Adjovi",
                "prenom": "Koffi",
                "telephone": "+228 90 11 22 33",
                "statut": "actif",
                "date_embauche": date(2023, 1, 15),
                "emplacements_indices": [0],  # Marché central
            },
            {
                "username": "agent.ama",
                "email": "ama.tchalla@mairiekloto1.tg",
                "matricule": "AGT-2025-002",
                "nom": "Tchalla",
                "prenom": "Ama",
                "telephone": "+228 91 22 33 44",
                "statut": "actif",
                "date_embauche": date(2023, 3, 1),
                "emplacements_indices": [0, 3],  # Marché central + Gbényédzi
            },
            {
                "username": "agent.komlan",
                "email": "komlan.sena@mairiekloto1.tg",
                "matricule": "AGT-2025-003",
                "nom": "Séna",
                "prenom": "Komlan",
                "telephone": "+228 92 33 44 55",
                "statut": "actif",
                "date_embauche": date(2024, 1, 10),
                "emplacements_indices": [1],  # Marché d'Adéta
            },
            {
                "username": "agent.yawo",
                "email": "yawo.agbe@mairiekloto1.tg",
                "matricule": "AGT-2025-004",
                "nom": "Agbé",
                "prenom": "Yawo",
                "telephone": "+228 93 44 55 66",
                "statut": "actif",
                "date_embauche": date(2024, 2, 20),
                "emplacements_indices": [2],  # Place Kpodzi
            },
            {
                "username": "agent.abra",
                "email": "abra.dede@mairiekloto1.tg",
                "matricule": "AGT-2025-005",
                "nom": "Dédé",
                "prenom": "Abra",
                "telephone": "+228 94 55 66 77",
                "statut": "inactif",
                "date_embauche": date(2022, 6, 1),
                "emplacements_indices": [],  # Aucun (inactif)
            },
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for data in agents_data:
            matricule = data["matricule"]
            existing_agent = AgentCollecteur.objects.filter(matricule=matricule).first()

            if existing_agent and not force:
                self.stdout.write(self.style.WARNING(f"  Ignoré (existe déjà): {matricule} - {data['nom']} {data['prenom']}"))
                skipped_count += 1
                continue

            # Créer ou récupérer l'utilisateur
            user, user_created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["prenom"],
                    "last_name": data["nom"],
                    "is_staff": True,  # Les agents sont des membres du staff
                },
            )
            if not user_created:
                # Mettre à jour l'utilisateur existant
                user.email = data["email"]
                user.first_name = data["prenom"]
                user.last_name = data["nom"]
                user.is_staff = True
                user.save()

            # Créer ou mettre à jour l'agent
            if existing_agent and force:
                # Mettre à jour
                for key in ["nom", "prenom", "telephone", "email", "statut", "date_embauche"]:
                    setattr(existing_agent, key, data[key])
                existing_agent.user = user
                existing_agent.save()
                agent = existing_agent
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Mis à jour: {matricule} - {agent.nom_complet}"))
            else:
                # Créer
                agent = AgentCollecteur.objects.create(
                    user=user,
                    matricule=matricule,
                    nom=data["nom"],
                    prenom=data["prenom"],
                    telephone=data["telephone"],
                    email=data["email"],
                    statut=data["statut"],
                    date_embauche=data["date_embauche"],
                    notes=f"Agent collecteur créé automatiquement le {timezone.now().strftime('%d/%m/%Y')}.",
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Créé: {matricule} - {agent.nom_complet}"))

            # Assigner les emplacements
            emplacements_assignes = [emplacements[i] for i in data["emplacements_indices"] if i < len(emplacements)]
            if emplacements_assignes:
                agent.emplacements_assignes.set(emplacements_assignes)
                self.stdout.write(f"    → Assigné à {len(emplacements_assignes)} emplacement(s)")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Résumé:"))
        self.stdout.write(f"  - Agents créés : {created_count}")
        self.stdout.write(f"  - Agents mis à jour : {updated_count}")
        self.stdout.write(f"  - Agents ignorés : {skipped_count}")
        self.stdout.write(f"  - Total agents collecteurs : {AgentCollecteur.objects.count()}")
        self.stdout.write(self.style.SUCCESS("Terminé. Les agents peuvent maintenant être utilisés pour les encaissements."))
