"""
Commande Django pour ajouter une fiche de cartographie pour la commune active.
Usage: python manage.py ajouter_cartographie_commune
"""

from django.core.management.base import BaseCommand
from decimal import Decimal

from mairie.models import ConfigurationMairie, CartographieCommune


class Command(BaseCommand):
    help = "Crée ou met à jour les données de cartographie pour la commune active (ConfigurationMairie.est_active=True)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Réécrire les données existantes au lieu de les laisser inchangées",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)

        config = ConfigurationMairie.objects.filter(est_active=True).first()
        if not config:
            self.stdout.write(
                self.style.ERROR(
                    "Aucune ConfigurationMairie active trouvée. "
                    "Créez d'abord une configuration dans l'admin."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Utilisation de la configuration active : {config.nom_commune}"
            )
        )

        # Données d'exemple pour la commune de Kloto 1
        data = {
            "superficie_km2": 146,
            "population_totale": 95000,
            "densite_hab_km2": 650,
            "taux_natalite_pour_mille": Decimal("32.50"),
            "taux_mortalite_pour_mille": Decimal("7.80"),
            "taux_croissance_pourcent": Decimal("2.30"),
            "principales_activites": (
                "Agriculture (café, cacao, cultures vivrières)\n"
                "Tourisme (montagnes, cascades, sites naturels)\n"
                "Commerce et services\n"
                "Artisanat (sculpture, textile, produits locaux)"
            ),
            "infrastructures_sante": (
                "Centre hospitalier préfectoral de Kpalimé\n"
                "Centre médico-social de Kpalimé\n"
                "Centres de santé de quartiers (Kpodzi, Nyiveme, Agomé-Yo, etc.)\n"
                "Postes de santé périphériques dans les villages\n"
                "Cliniques et cabinets privés"
            ),
            "infrastructures_education": (
                "Écoles maternelles publiques et privées\n"
                "Écoles primaires publiques et privées\n"
                "Collèges d'enseignement général (CEG)\n"
                "Lycées d'enseignement général\n"
                "Collèges / Lycées (établissements à double cycle)\n"
                "Centres de formation professionnelle et technique"
            ),
            "infrastructures_routes": (
                "Axes principaux bitumés reliant Kpalimé à Lomé et aux localités voisines\n"
                "Réseau de voiries urbaines\n"
                "Pistes rurales desservant les villages\n"
                "Ouvrages d'assainissement et caniveaux"
            ),
            "infrastructures_administration": (
                "Mairie de Kloto 1\n"
                "Préfecture de Kloto\n"
                "Services déconcentrés de l'État\n"
                "Chefferies traditionnelles et services de sécurité"
            ),
            "centre_latitude": Decimal("6.900000"),
            "centre_longitude": Decimal("0.630000"),
            "zoom_carte": 13,
        }

        cartographie, created = CartographieCommune.objects.get_or_create(
            configuration=config, defaults=data
        )

        if not created and force:
            for key, value in data.items():
                setattr(cartographie, key, value)
            cartographie.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "Fiche de cartographie existante mise à jour avec les nouvelles données."
                )
            )
        elif created:
            self.stdout.write(
                self.style.SUCCESS(
                    "Fiche de cartographie créée avec succès pour la commune active."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Une fiche de cartographie existe déjà. "
                    "Utilisez --force pour la réécrire ou modifiez-la dans l'admin."
                )
            )

        self.stdout.write(
            self.style.SUCCESS("Terminé. Consultez la page /cartographie/ pour vérifier l'affichage.")
        )

