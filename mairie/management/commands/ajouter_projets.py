"""
Commande Django pour ajouter 5 projets en base : 3 réalisés et 2 en cours.
Usage: python manage.py ajouter_projets
"""
from django.core.management.base import BaseCommand
from datetime import date
from decimal import Decimal

from mairie.models import Projet


class Command(BaseCommand):
    help = "Ajoute 5 projets (3 réalisés, 2 en cours) dans la base de données"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Réécrire les projets existants (même slug) au lieu de les ignorer",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)
        self.stdout.write(self.style.SUCCESS("Ajout des 5 projets (3 réalisés, 2 en cours)..."))

        projets_data = [
            # --- 3 PROJETS RÉALISÉS ---
            {
                "titre": "Réhabilitation du marché central de Kpalimé",
                "slug": "rehabilitation-marche-central-kpalime",
                "description": (
                    "Projet de réhabilitation complète du marché central de Kpalimé : "
                    "restructuration des stands, amélioration de l'évacuation des eaux usées, "
                    "éclairage public, sécurisation des accès et aménagement d'espaces de stationnement. "
                    "Ce projet a permis de moderniser les conditions de travail des commerçants "
                    "et d'améliorer l'hygiène et la sécurité sur le site."
                ),
                "resume": "Réhabilitation complète du marché central : stands, assainissement, éclairage et sécurisation.",
                "statut": "realise",
                "date_debut": date(2022, 3, 1),
                "date_fin": date(2023, 11, 15),
                "budget": Decimal("45000000.00"),
                "localisation": "Centre-ville, Kpalimé",
                "ordre_affichage": 10,
            },
            {
                "titre": "Électrification rurale des villages de Kloto 1",
                "slug": "electrification-rurale-villages-kloto1",
                "description": (
                    "Extension du réseau électrique vers plusieurs villages de la commune de Kloto 1 : "
                    "pose de poteaux et câbles, installation de transformateurs, branchements domestiques "
                    "et raccordement des espaces communs (écoles, centres de santé). "
                    "Plus de 800 ménages et une vingtaine d'équipements publics ont été raccordés."
                ),
                "resume": "Extension du réseau électrique vers les villages : plus de 800 ménages et équipements publics raccordés.",
                "statut": "realise",
                "date_debut": date(2021, 9, 1),
                "date_fin": date(2023, 6, 30),
                "budget": Decimal("120000000.00"),
                "localisation": "Villages de Kloto 1 (Kpodzi, Adéta, etc.)",
                "ordre_affichage": 20,
            },
            {
                "titre": "Construction d'un centre de santé communautaire",
                "slug": "construction-centre-sante-communautaire",
                "description": (
                    "Construction et équipement d'un centre de santé communautaire pour améliorer "
                    "l'accès aux soins de base dans un quartier périphérique : bâtiment avec salles de consultation, "
                    "accueil des urgences, pharmacie, maternité et logement pour le personnel. "
                    "Le centre est opérationnel et dessert plus de 5000 habitants."
                ),
                "resume": "Construction et équipement d'un centre de santé : consultation, maternité, pharmacie. Plus de 5000 habitants desservis.",
                "statut": "realise",
                "date_debut": date(2022, 1, 10),
                "date_fin": date(2024, 2, 28),
                "budget": Decimal("85000000.00"),
                "localisation": "Quartier Agou-Gare, Kpalimé",
                "ordre_affichage": 30,
            },
            # --- 2 PROJETS EN COURS ---
            {
                "titre": "Aménagement de la voirie et assainissement",
                "slug": "amenagement-voirie-assainissement",
                "description": (
                    "Aménagement et réhabilitation des voies de circulation et des réseaux d'assainissement "
                    "dans plusieurs quartiers : reprofilage des pistes, caniveaux, ouvrages de franchissement, "
                    "évacuation des eaux pluviales et lutte contre l'érosion. Les travaux se poursuivent "
                    "par phase selon les financements disponibles."
                ),
                "resume": "Réhabilitation des voies et réseaux d'assainissement : caniveaux, évacuation des eaux, lutte contre l'érosion.",
                "statut": "en_cours",
                "date_debut": date(2024, 4, 1),
                "date_fin": None,
                "budget": Decimal("65000000.00"),
                "localisation": "Quartiers Gbényédzi, Nyogbo, Kpodzi",
                "ordre_affichage": 40,
            },
            {
                "titre": "Adduction d'eau potable et bornes-fontaines",
                "slug": "adduction-eau-potable-bornes-fontaines",
                "description": (
                    "Projet d'adduction d'eau potable et de construction de bornes-fontaines dans les zones "
                    "mal desservies : forage, château d'eau, réseau de distribution et bornes-fontaines. "
                    "L'objectif est de réduire la corvée d'eau et d'améliorer la qualité de l'eau consommée. "
                    "Les travaux sont en cours ; la première phase (3 bornes) est en fin de réalisation."
                ),
                "resume": "Adduction d'eau potable et bornes-fontaines pour améliorer l'accès à l'eau dans les quartiers défavorisés.",
                "statut": "en_cours",
                "date_debut": date(2024, 8, 15),
                "date_fin": None,
                "budget": Decimal("55000000.00"),
                "localisation": "Secteurs ruraux et quartiers périphériques, Kloto 1",
                "ordre_affichage": 50,
            },
        ]

        created = 0
        updated = 0
        skipped = 0

        for i, data in enumerate(projets_data, 1):
            slug = data["slug"]
            existing = Projet.objects.filter(slug=slug).first()

            if existing and not force:
                self.stdout.write(self.style.WARNING(f"  {i}. Ignoré (existe déjà): {data['titre']}"))
                skipped += 1
                continue

            if existing and force:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.save()
                self.stdout.write(self.style.SUCCESS(f"  {i}. Mis à jour: {data['titre']}"))
                updated += 1
            else:
                Projet.objects.create(**data)
                self.stdout.write(self.style.SUCCESS(f"  {i}. Créé: {data['titre']}"))
                created += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Terminé: {created} créé(s), {updated} mis à jour, {skipped} ignoré(s)."))
        self.stdout.write("Consultez la page /nos-projets/ pour voir les projets.")
