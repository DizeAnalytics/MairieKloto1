from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from mairie.models import AppelOffre


class Command(BaseCommand):
    help = "Ajoute 5 appels d'offres de test dans la base de données"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Début de l'ajout des appels d'offres..."))

        maintenant = timezone.now()

        appels_data = [
            {
                "titre": "Appel d'offres pour la construction d'un marché moderne",
                "reference": "AO-2025-001",
                "description": "La Mairie de Kloto 1 lance un appel d'offres pour la construction d'un marché moderne dans le centre-ville de Kpalimé. Le projet comprend la construction de 200 stands commerciaux, des installations sanitaires modernes, un système de drainage et un parking. Les entreprises candidates doivent avoir une expérience minimale de 5 ans dans le domaine du bâtiment et des travaux publics, et être enregistrées au RCCM.",
                "public_cible": "entreprises",
                "date_debut": maintenant - timedelta(days=10),
                "date_fin": maintenant + timedelta(days=30),
                "budget_estime": Decimal("500000000.00"),  # 500 millions FCFA
                "criteres_selection": "Expérience minimale de 5 ans en BTP, capacité financière, équipe technique qualifiée, références de projets similaires, respect des normes environnementales.",
                "statut": "publie",
                "est_publie_sur_site": True,
            },
            {
                "titre": "Partenariat pour le financement de projets communautaires",
                "reference": "AO-2025-002",
                "description": "La Mairie recherche des partenaires financiers (banques, IMF, bailleurs de fonds) pour financer des projets de développement communautaire dans la commune. Les projets concernent l'amélioration de l'accès à l'eau potable, l'électrification rurale, et le soutien aux micro-entreprises. Les institutions financières intéressées doivent proposer des conditions de financement avantageuses et des modalités adaptées aux besoins locaux.",
                "public_cible": "institutions",
                "date_debut": maintenant - timedelta(days=5),
                "date_fin": maintenant + timedelta(days=45),
                "budget_estime": Decimal("200000000.00"),  # 200 millions FCFA
                "criteres_selection": "Agrément officiel, expérience en financement de projets communautaires, taux d'intérêt compétitifs, flexibilité dans les modalités de remboursement, accompagnement technique.",
                "statut": "publie",
                "est_publie_sur_site": True,
            },
            {
                "titre": "Recrutement de jeunes pour le programme d'insertion professionnelle",
                "reference": "AO-2025-003",
                "description": "La Mairie de Kloto 1 lance un programme d'insertion professionnelle pour les jeunes de la commune. Ce programme offre des opportunités de stage, de formation professionnelle et d'emploi dans divers secteurs (commerce, artisanat, services, agriculture). Les jeunes candidats doivent être âgés de 18 à 35 ans, résider dans la commune, et être motivés à développer leurs compétences professionnelles.",
                "public_cible": "jeunes",
                "date_debut": maintenant - timedelta(days=3),
                "date_fin": maintenant + timedelta(days=60),
                "criteres_selection": "Âge entre 18 et 35 ans, résidence dans la commune de Kloto 1, motivation et engagement, niveau d'études minimum CEP, disponibilité immédiate.",
                "statut": "publie",
                "est_publie_sur_site": True,
            },
            {
                "titre": "Mise à disposition d'expertise pour l'amélioration de la gestion municipale",
                "reference": "AO-2025-004",
                "description": "La Mairie recherche des retraités actifs ayant une expertise en administration publique, gestion financière, ou planification urbaine pour accompagner l'amélioration de la gestion municipale. Les missions concernent le conseil, la formation du personnel, et l'appui technique sur des projets spécifiques. Les retraités intéressés doivent avoir une expérience significative dans le secteur public ou parapublic.",
                "public_cible": "retraites",
                "date_debut": maintenant - timedelta(days=7),
                "date_fin": maintenant + timedelta(days=40),
                "budget_estime": Decimal("50000000.00"),  # 50 millions FCFA
                "criteres_selection": "Expérience minimale de 20 ans dans le secteur public, expertise dans au moins un domaine (administration, finances, urbanisme), disponibilité pour des missions ponctuelles, capacité de transmission de savoir.",
                "statut": "publie",
                "est_publie_sur_site": True,
            },
            {
                "titre": "Appel à projets pour le développement économique local",
                "reference": "AO-2025-005",
                "description": "La Mairie de Kloto 1 lance un appel à projets ouvert à tous (entreprises, institutions financières, jeunes entrepreneurs, retraités) pour le développement économique local. Les projets peuvent concerner l'agriculture, l'artisanat, le commerce, les services, le tourisme, ou tout autre secteur porteur. Les projets sélectionnés bénéficieront d'un accompagnement technique et d'un appui à la recherche de financement. Cet appel vise à stimuler l'innovation et l'entrepreneuriat dans la commune.",
                "public_cible": "tous",
                "date_debut": maintenant - timedelta(days=1),
                "date_fin": maintenant + timedelta(days=90),
                "budget_estime": Decimal("100000000.00"),  # 100 millions FCFA
                "criteres_selection": "Innovation et impact local, viabilité économique, création d'emplois, respect de l'environnement, contribution au développement de la commune, faisabilité technique et financière.",
                "statut": "publie",
                "est_publie_sur_site": True,
            },
        ]

        for i, data in enumerate(appels_data, 1):
            appel, created = AppelOffre.objects.get_or_create(
                reference=data["reference"],
                defaults=data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Appel d'offres {i} créé : {appel.titre} ({appel.reference})"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  - Appel d'offres {i} existe déjà : {appel.titre} ({appel.reference})"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("\n✓ Ajout des appels d'offres terminé avec succès !")
        )

