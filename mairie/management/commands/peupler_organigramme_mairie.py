"""
Commande Django pour peupler la base avec un organigramme de démonstration :
- 4 directions
- 3 sections par direction
- plusieurs personnels par section

Usage : python manage.py peupler_organigramme_mairie
"""

from django.core.management.base import BaseCommand

from mairie.models import DirectionMairie, SectionDirection, PersonnelSection, ServiceSection


class Command(BaseCommand):
    help = (
        "Peuple la base avec un organigramme complet de démonstration "
        "(4 directions, sections et personnels rattachés)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Réécrire les données existantes (directions, sections, personnels) au lieu de les laisser inchangées.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Supprimer tout l'organigramme (directions, sections, personnels) avant de peupler.",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)
        clear = options.get("clear", False)

        if clear:
            self.stdout.write(self.style.WARNING("Suppression de l'organigramme existant..."))
            PersonnelSection.objects.all().delete()
            SectionDirection.objects.all().delete()
            DirectionMairie.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Organigramme supprimé."))

        # --- Définition des données de démonstration ---
        # Inspiré du schéma fourni : Conseil communal -> Maire -> SG -> Directions.
        organigramme_data = [
            {
                "nom": "Direction des affaires administratives, ressources humaines et état civil",
                "sigle": "DAARHEC",
                "chef_direction": "Directeur des affaires administratives",
                "ordre_affichage": 1,
                "sections": [
                    {
                        "nom": "Section État civil",
                        "sigle": "SEC",
                        "chef_section": "Chef section état civil",
                        "ordre_affichage": 1,
                        "personnels": [
                            {
                                "nom_prenoms": "Kossi ADJOMAYI",
                                "fonction": "Officier de l'état civil",
                                "contact": "+228 90 00 00 01",
                                "adresse": "Hôtel de Ville, Bureau État civil",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Akossiwa MENSAH",
                                "fonction": "Agent d'accueil",
                                "contact": "+228 90 00 00 02",
                                "adresse": "Guichet état civil",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                    {
                        "nom": "Section Ressources humaines",
                        "sigle": "SRH",
                        "chef_section": "Chef section ressources humaines",
                        "ordre_affichage": 2,
                        "personnels": [
                            {
                                "nom_prenoms": "Ama TCHALLA",
                                "fonction": "Responsable RH",
                                "contact": "+228 90 00 00 03",
                                "adresse": "Bureau RH",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Komlan SENA",
                                "fonction": "Gestionnaire de paie",
                                "contact": "+228 90 00 00 04",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                    {
                        "nom": "Section Secrétariat administratif",
                        "sigle": "SSA",
                        "chef_section": "Chef secrétariat administratif",
                        "ordre_affichage": 3,
                        "personnels": [
                            {
                                "nom_prenoms": "Abra DEDE",
                                "fonction": "Secrétaire principal",
                                "contact": "+228 90 00 00 05",
                                "adresse": "Secrétariat général",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Yawo AGBE",
                                "fonction": "Assistant administratif",
                                "contact": "+228 90 00 00 06",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                ],
            },
            {
                "nom": "Direction des affaires financières",
                "sigle": "DAF",
                "chef_direction": "Directeur des affaires financières",
                "ordre_affichage": 2,
                "sections": [
                    {
                        "nom": "Section Budget et comptabilité",
                        "sigle": "SBC",
                        "chef_section": "Chef budget et comptabilité",
                        "ordre_affichage": 1,
                        "personnels": [
                            {
                                "nom_prenoms": "Kwami AHO",
                                "fonction": "Comptable principal",
                                "contact": "+228 90 00 00 07",
                                "adresse": "",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Essohanam KOUASSI",
                                "fonction": "Assistant comptable",
                                "contact": "+228 90 00 00 08",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                    {
                        "nom": "Section Recettes et recouvrement",
                        "sigle": "SRR",
                        "chef_section": "Chef recettes et recouvrement",
                        "ordre_affichage": 2,
                        "personnels": [
                            {
                                "nom_prenoms": "Kafui ADZO",
                                "fonction": "Contrôleur des recettes",
                                "contact": "+228 90 00 00 09",
                                "adresse": "",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Eyram BODJONA",
                                "fonction": "Agent de recouvrement",
                                "contact": "+228 90 00 00 10",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                    {
                        "nom": "Section Dépenses et trésorerie",
                        "sigle": "SDT",
                        "chef_section": "Chef dépenses et trésorerie",
                        "ordre_affichage": 3,
                        "personnels": [
                            {
                                "nom_prenoms": "Akouvi KPAN",
                                "fonction": "Trésorière municipale",
                                "contact": "+228 90 00 00 11",
                                "adresse": "",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Kodjo AMEGAN",
                                "fonction": "Gestionnaire de caisse",
                                "contact": "+228 90 00 00 12",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                ],
            },
            {
                "nom": "Direction des services techniques",
                "sigle": "DST",
                "chef_direction": "Directeur des services techniques",
                "ordre_affichage": 3,
                "sections": [
                    {
                        "nom": "Section Voirie et réseaux divers",
                        "sigle": "SVRD",
                        "chef_section": "Chef voirie et réseaux divers",
                        "ordre_affichage": 1,
                        "personnels": [
                            {
                                "nom_prenoms": "Sena KOFFI",
                                "fonction": "Ingénieur voirie",
                                "contact": "+228 90 00 00 13",
                                "adresse": "",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Etse DOSSOU",
                                "fonction": "Technicien VRD",
                                "contact": "+228 90 00 00 14",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                    {
                        "nom": "Section Bâtiments communaux",
                        "sigle": "SBCO",
                        "chef_section": "Chef bâtiments communaux",
                        "ordre_affichage": 2,
                        "personnels": [
                            {
                                "nom_prenoms": "Komi FOLI",
                                "fonction": "Responsable entretien bâtiments",
                                "contact": "+228 90 00 00 15",
                                "adresse": "",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Mawuli AKPA",
                                "fonction": "Agent technique",
                                "contact": "+228 90 00 00 16",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                    {
                        "nom": "Section Environnement et hygiène",
                        "sigle": "SEH",
                        "chef_section": "Chef environnement et hygiène",
                        "ordre_affichage": 3,
                        "personnels": [
                            {
                                "nom_prenoms": "Akossiwa KODJO",
                                "fonction": "Chargée de l'environnement",
                                "contact": "+228 90 00 00 17",
                                "adresse": "",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Yawovi MENOU",
                                "fonction": "Agent d'hygiène",
                                "contact": "+228 90 00 00 18",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                ],
            },
            {
                "nom": "Direction de la planification du développement",
                "sigle": "DPD",
                "chef_direction": "Directeur de la planification du développement",
                "ordre_affichage": 4,
                "sections": [
                    {
                        "nom": "Section Études et planification",
                        "sigle": "SEP",
                        "chef_section": "Chef études et planification",
                        "ordre_affichage": 1,
                        "personnels": [
                            {
                                "nom_prenoms": "Julien KOULE",
                                "fonction": "Planificateur",
                                "contact": "+228 90 00 00 19",
                                "adresse": "",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Béatrice AFA",
                                "fonction": "Chargée d'études",
                                "contact": "+228 90 00 00 20",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                    {
                        "nom": "Section Suivi-évaluation",
                        "sigle": "SSE",
                        "chef_section": "Chef suivi-évaluation",
                        "ordre_affichage": 2,
                        "personnels": [
                            {
                                "nom_prenoms": "Michel KPOME",
                                "fonction": "Spécialiste suivi-évaluation",
                                "contact": "+228 90 00 00 21",
                                "adresse": "",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Esther GATI",
                                "fonction": "Chargée de reporting",
                                "contact": "+228 90 00 00 22",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                    {
                        "nom": "Section Coopération et projets",
                        "sigle": "SCP",
                        "chef_section": "Chef coopération et projets",
                        "ordre_affichage": 3,
                        "personnels": [
                            {
                                "nom_prenoms": "Nadia LAWSON",
                                "fonction": "Chargée de coopération",
                                "contact": "+228 90 00 00 23",
                                "adresse": "",
                                "ordre_affichage": 1,
                            },
                            {
                                "nom_prenoms": "Serge AYEVA",
                                "fonction": "Gestionnaire de projets",
                                "contact": "+228 90 00 00 24",
                                "adresse": "",
                                "ordre_affichage": 2,
                            },
                        ],
                    },
                ],
            },
        ]

        created_dirs = 0
        updated_dirs = 0
        created_sections = 0
        updated_sections = 0
        created_personnels = 0
        updated_personnels = 0

        for d in organigramme_data:
            sigle = d["sigle"]
            direction_defaults = {
                "nom": d["nom"],
                "chef_direction": d["chef_direction"],
                "ordre_affichage": d["ordre_affichage"],
                "est_active": True,
            }

            direction, created = DirectionMairie.objects.get_or_create(
                sigle=sigle, defaults=direction_defaults
            )
            if created:
                created_dirs += 1
                self.stdout.write(self.style.SUCCESS(f"Direction créée : {direction}"))
            else:
                if force:
                    for key, value in direction_defaults.items():
                        setattr(direction, key, value)
                    direction.save()
                    updated_dirs += 1
                    self.stdout.write(self.style.SUCCESS(f"Direction mise à jour : {direction}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Direction existante conservée : {direction}"))

            # Sections
            for s in d.get("sections", []):
                section_defaults = {
                    "nom": s["nom"],
                    "chef_section": s["chef_section"],
                    "ordre_affichage": s["ordre_affichage"],
                    "est_active": True,
                }
                section, sec_created = SectionDirection.objects.get_or_create(
                    direction=direction,
                    sigle=s["sigle"],
                    defaults=section_defaults,
                )
                if sec_created:
                    created_sections += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  Section créée : {section.nom} ({section.sigle})")
                    )
                else:
                    if force:
                        for key, value in section_defaults.items():
                            setattr(section, key, value)
                        section.save()
                        updated_sections += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  Section mise à jour : {section.nom} ({section.sigle})"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Section existante conservée : {section.nom} ({section.sigle})"
                            )
                        )

                # Personnels
                for p in s.get("personnels", []):
                    pers_defaults = {
                        "adresse": p.get("adresse", ""),
                        "contact": p.get("contact", ""),
                        "ordre_affichage": p.get("ordre_affichage", 0),
                        "est_actif": True,
                    }
                    personnel, pers_created = PersonnelSection.objects.get_or_create(
                        section=section,
                        nom_prenoms=p["nom_prenoms"],
                        fonction=p["fonction"],
                        defaults=pers_defaults,
                    )
                    if pers_created:
                        created_personnels += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"    Personnel créé : {personnel.nom_prenoms} - {personnel.fonction}"
                            )
                        )
                    else:
                        if force:
                            for key, value in pers_defaults.items():
                                setattr(personnel, key, value)
                            personnel.save()
                            updated_personnels += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"    Personnel mis à jour : {personnel.nom_prenoms} - {personnel.fonction}"
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"    Personnel existant conservé : {personnel.nom_prenoms} - {personnel.fonction}"
                                )
                            )

        # Création automatique de services (au moins 2 par section)
        created_services = 0
        for section in SectionDirection.objects.all():
            existing_count = ServiceSection.objects.filter(section=section).count()
            if existing_count >= 2:
                continue

            # Services de base générés à partir du nom de la section
            base_title = section.nom
            templates = [
                f"Accueil et information - {base_title}",
                f"Gestion des dossiers - {base_title}",
            ]

            # Créer autant de services que nécessaire pour atteindre 2
            for idx in range(existing_count, 2):
                titre = templates[idx] if idx < len(templates) else f"Service {idx + 1} - {base_title}"
                ServiceSection.objects.create(
                    section=section,
                    titre=titre,
                    description="Service généré automatiquement pour illustrer les activités de la section.",
                    responsable=section.chef_section or "",
                    ordre_affichage=idx,
                    est_actif=True,
                )
                created_services += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Résumé de l'organigramme :"))
        self.stdout.write(f"  - Directions créées : {created_dirs}")
        self.stdout.write(f"  - Directions mises à jour : {updated_dirs}")
        self.stdout.write(f"  - Sections créées : {created_sections}")
        self.stdout.write(f"  - Sections mises à jour : {updated_sections}")
        self.stdout.write(f"  - Personnels créés : {created_personnels}")
        self.stdout.write(f"  - Personnels mis à jour : {updated_personnels}")
        self.stdout.write(f"  - Services créés (complémentaires) : {created_services}")
        self.stdout.write(
            self.style.SUCCESS(
                "Terminé. Consultez les pages /organigramme/ et /organigramme/section/<id>/services/ pour vérifier l'affichage."
            )
        )

