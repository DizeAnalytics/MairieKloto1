"""
Commande Django pour peupler la base avec des données de démonstration :
- EmplacementsMarche (marchés / places publiques)
- Contribuables
- Boutiques/Magasins
- Cotisations annuelles et paiements mensuels
- Tickets marché (étalages)

Usage: python manage.py peupler_contribuables_marche
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from mairie.models import (
    AgentCollecteur,
    EmplacementMarche,
    Contribuable,
    BoutiqueMagasin,
    CotisationAnnuelle,
    PaiementCotisation,
    TicketMarche,
)


class Command(BaseCommand):
    help = (
        "Peuple la base avec des contribuables, emplacements marché, "
        "boutiques/magasins, cotisations (annuelles + mensuelles) et tickets marché."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recréer les données même si des enregistrements existent déjà (matricules, etc.).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Supprimer toutes les données contribuables/marché avant de peupler (à utiliser avec précaution).",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)
        clear = options.get("clear", False)

        # Agent pour encaissements (optionnel) - utiliser AgentCollecteur si disponible
        agent_collecteur = AgentCollecteur.objects.filter(statut="actif").first()
        agent_user = agent_collecteur.user if agent_collecteur else User.objects.filter(is_staff=True).first()

        if clear:
            self.stdout.write(self.style.WARNING("Suppression des données existantes..."))
            PaiementCotisation.objects.all().delete()
            TicketMarche.objects.all().delete()
            CotisationAnnuelle.objects.all().delete()
            BoutiqueMagasin.objects.all().delete()
            Contribuable.objects.all().delete()
            EmplacementMarche.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Données supprimées."))

        # --- 1. Emplacements (marchés / places publiques) ---
        self.stdout.write(self.style.SUCCESS("Création des emplacements marché..."))
        emplacements_data = [
            {
                "canton": "Kloto",
                "village": "",
                "quartier": "Centre-ville",
                "nom_lieu": "Marché central de Kpalimé",
                "description": "Principal marché de Kpalimé, tous les jours. Légumes, viande, épices, vêtements, artisanat.",
            },
            {
                "canton": "Kloto",
                "village": "Adéta",
                "quartier": "Marché",
                "nom_lieu": "Marché d'Adéta",
                "description": "Marché hebdomadaire d'Adéta.",
            },
            {
                "canton": "Kloto",
                "village": "Kpodzi",
                "quartier": "Place publique",
                "nom_lieu": "Place du marché de Kpodzi",
                "description": "Place publique et marché de Kpodzi.",
            },
            {
                "canton": "Kloto",
                "village": "",
                "quartier": "Gbényédzi",
                "nom_lieu": "Marché de Gbényédzi",
                "description": "Marché de quartier, étalages et quelques boutiques.",
            },
        ]
        emplacements = []
        for data in emplacements_data:
            obj, created = EmplacementMarche.objects.get_or_create(
                nom_lieu=data["nom_lieu"],
                quartier=data["quartier"],
                defaults=data,
            )
            emplacements.append(obj)
            self.stdout.write(f"  - {obj} {'(créé)' if created else '(existant)'}")

        # --- 2. Contribuables ---
        self.stdout.write(self.style.SUCCESS("Création des contribuables..."))
        contribuables_data = [
            {"nom": "Adjo", "prenom": "Marie", "telephone": "+228 90 12 34 56"},
            {"nom": "Gbado", "prenom": "Koffi", "telephone": "+228 91 23 45 67"},
            {"nom": "Tchalla", "prenom": "Ama", "telephone": "+228 92 34 56 78"},
            {"nom": "Séna", "prenom": "Komlan", "telephone": "+228 93 45 67 89"},
            {"nom": "Agbé", "prenom": "Yawo", "telephone": "+228 94 56 78 90"},
            {"nom": "Dédé", "prenom": "Abra", "telephone": "+228 95 67 89 01"},
            {"nom": "Foli", "prenom": "Kossi", "telephone": "+228 96 78 90 12"},
            {"nom": "Mensah", "prenom": "Akossiwa", "telephone": "+228 97 89 01 23"},
            {"nom": "Tsé", "prenom": "Kodjo", "telephone": "+228 98 90 12 34"},
            {"nom": "Worou", "prenom": "Séna", "telephone": "+228 99 01 23 45"},
        ]
        contribuables = []
        for data in contribuables_data:
            obj, created = Contribuable.objects.get_or_create(
                nom=data["nom"],
                prenom=data["prenom"],
                defaults={**data, "nationalite": "Togolaise"},
            )
            contribuables.append(obj)
            self.stdout.write(f"  - {obj.nom_complet} {'(créé)' if created else '(existant)'}")

        # --- 3. Boutiques / Magasins ---
        self.stdout.write(self.style.SUCCESS("Création des boutiques et magasins..."))
        # Note: Un contribuable peut avoir plusieurs boutiques (ex: contribuable 0 a 2 boutiques)
        # Répartition : marché central (4), Adéta (2), Kpodzi (2), Gbényédzi (2)
        boutiques_data = [
            {
                "matricule": "MKT-2025-001",
                "emplacement_idx": 0,
                "type_local": "boutique",
                "superficie_m2": Decimal("8.00"),
                "prix_location_mensuel": Decimal("25000.00"),
                "prix_location_annuel": Decimal("270000.00"),  # tarif annuel dégressif
                "contribuable_idx": 0,  # Marie Adjo - première boutique
                "activite_vendue": "Légumes et fruits",
            },
            {
                "matricule": "MKT-2025-002",
                "emplacement_idx": 0,
                "type_local": "boutique",
                "superficie_m2": Decimal("6.50"),
                "prix_location_mensuel": Decimal("20000.00"),
                "prix_location_annuel": None,
                "contribuable_idx": 0,  # Marie Adjo - deuxième boutique (même contribuable)
                "activite_vendue": "Épices et condiments",
            },
            {
                "matricule": "MKT-2025-003",
                "emplacement_idx": 0,
                "type_local": "magasin",
                "superficie_m2": Decimal("15.00"),
                "prix_location_mensuel": Decimal("50000.00"),
                "prix_location_annuel": Decimal("540000.00"),
                "contribuable_idx": 1,  # Koffi Gbado
                "activite_vendue": "Vêtements et tissus",
            },
            {
                "matricule": "MKT-2025-004",
                "emplacement_idx": 0,
                "type_local": "local",
                "superficie_m2": Decimal("10.00"),
                "prix_location_mensuel": Decimal("35000.00"),
                "prix_location_annuel": None,
                "contribuable_idx": 2,  # Ama Tchalla
                "activite_vendue": "Produits de première nécessité",
            },
            {
                "matricule": "MKT-2025-005",
                "emplacement_idx": 1,
                "type_local": "boutique",
                "superficie_m2": Decimal("6.00"),
                "prix_location_mensuel": Decimal("15000.00"),
                "prix_location_annuel": None,
                "contribuable_idx": 3,  # Komlan Séna
                "activite_vendue": "Céréales et légumineuses",
            },
            {
                "matricule": "MKT-2025-006",
                "emplacement_idx": 1,
                "type_local": "boutique",
                "superficie_m2": Decimal("5.00"),
                "prix_location_mensuel": Decimal("12000.00"),
                "prix_location_annuel": Decimal("132000.00"),
                "contribuable_idx": 3,  # Komlan Séna - deuxième boutique (même contribuable)
                "activite_vendue": "Biscuits et boissons",
            },
            {
                "matricule": "MKT-2025-007",
                "emplacement_idx": 2,
                "type_local": "boutique",
                "superficie_m2": Decimal("7.00"),
                "prix_location_mensuel": Decimal("18000.00"),
                "prix_location_annuel": None,
                "contribuable_idx": 4,  # Yawo Agbé
                "activite_vendue": "Quincaillerie",
            },
            {
                "matricule": "MKT-2025-008",
                "emplacement_idx": 2,
                "type_local": "magasin",
                "superficie_m2": Decimal("12.00"),
                "prix_location_mensuel": Decimal("40000.00"),
                "prix_location_annuel": None,
                "contribuable_idx": 5,  # Abra Dédé
                "activite_vendue": "Électronique et accessoires",
            },
            {
                "matricule": "MKT-2025-009",
                "emplacement_idx": 3,
                "type_local": "boutique",
                "superficie_m2": Decimal("5.50"),
                "prix_location_mensuel": Decimal("14000.00"),
                "prix_location_annuel": None,
                "contribuable_idx": 6,  # Kossi Foli
                "activite_vendue": "Snacks et restauration rapide",
            },
            {
                "matricule": "MKT-2025-010",
                "emplacement_idx": 3,
                "type_local": "local",
                "superficie_m2": Decimal("9.00"),
                "prix_location_mensuel": Decimal("22000.00"),
                "prix_location_annuel": Decimal("240000.00"),
                "contribuable_idx": 7,  # Akossiwa Mensah
                "activite_vendue": "Artisanat et souvenirs",
            },
        ]
        boutiques = []
        for data in boutiques_data:
            if not force and BoutiqueMagasin.objects.filter(matricule=data["matricule"]).exists():
                b = BoutiqueMagasin.objects.get(matricule=data["matricule"])
                boutiques.append(b)
                self.stdout.write(f"  - {data['matricule']} (existant)")
                continue
            emplacement = emplacements[data["emplacement_idx"]]
            contribuable = contribuables[data["contribuable_idx"]]
            b = BoutiqueMagasin.objects.create(
                matricule=data["matricule"],
                emplacement=emplacement,
                type_local=data["type_local"],
                superficie_m2=data["superficie_m2"],
                prix_location_mensuel=data["prix_location_mensuel"],
                prix_location_annuel=data.get("prix_location_annuel"),
                contribuable=contribuable,
                activite_vendue=data["activite_vendue"],
                est_actif=True,
            )
            boutiques.append(b)
            self.stdout.write(f"  - {b.matricule} {b.contribuable.nom_complet} (créé)")

        # --- 4. Cotisations annuelles (2024 et 2025) + paiements mensuels ---
        self.stdout.write(self.style.SUCCESS("Création des cotisations annuelles et paiements mensuels..."))
        annee_courante = date.today().year
        for annee in (annee_courante - 1, annee_courante):
            for b in boutiques:
                montant_annuel = b.get_prix_annuel()
                cot, created = CotisationAnnuelle.objects.get_or_create(
                    boutique=b,
                    annee=annee,
                    defaults={"montant_annuel_du": montant_annuel},
                )
                if not created and force:
                    cot.montant_annuel_du = montant_annuel
                    cot.save()
                # Paiements mensuels : pour 2025, simuler quelques mois payés (1 à 6)
                if annee == annee_courante:
                    montant_mensuel = b.prix_location_mensuel
                    for mois in range(1, 7):  # janvier à juin
                        if PaiementCotisation.objects.filter(cotisation_annuelle=cot, mois=mois).exists() and not force:
                            continue
                        PaiementCotisation.objects.get_or_create(
                            cotisation_annuelle=cot,
                            mois=mois,
                            defaults={
                                "montant_paye": montant_mensuel,
                                "date_paiement": timezone.make_aware(
                                    timezone.datetime(annee, mois, 15, 10, 0, 0)
                                ),
                                "encaisse_par_agent": agent_collecteur,
                                "encaisse_par": agent_user,
                                "notes": "Paiement mensuel",
                            },
                        )
        self.stdout.write(f"  Cotisations annuelles et paiements (mois 1-6) créés pour {len(boutiques)} boutiques.")

        # --- 5. Tickets marché (étalages) ---
        self.stdout.write(self.style.SUCCESS("Création des tickets marché (étalages)..."))
        aujourd_hui = date.today()
        tickets_data = [
            {"jours_offset": 0, "emplacement_idx": 0, "contribuable_idx": None, "nom_vendeur": "Vendeuse anonyme 1", "tel": "", "montant": Decimal("500.00")},
            {"jours_offset": 0, "emplacement_idx": 0, "contribuable_idx": 0, "nom_vendeur": "Marie Adjo", "tel": "+228 90 12 34 56", "montant": Decimal("1000.00")},
            {"jours_offset": 0, "emplacement_idx": 0, "contribuable_idx": None, "nom_vendeur": "Vendeur légumes", "tel": "", "montant": Decimal("750.00")},
            {"jours_offset": -1, "emplacement_idx": 0, "contribuable_idx": None, "nom_vendeur": "Étalage fruits", "tel": "", "montant": Decimal("500.00")},
            {"jours_offset": -2, "emplacement_idx": 1, "contribuable_idx": 4, "nom_vendeur": "Yawo Agbé", "tel": "+228 94 56 78 90", "montant": Decimal("1000.00")},
            {"jours_offset": -2, "emplacement_idx": 1, "contribuable_idx": None, "nom_vendeur": "Vendeur Adéta", "tel": "", "montant": Decimal("500.00")},
            {"jours_offset": -3, "emplacement_idx": 2, "contribuable_idx": None, "nom_vendeur": "Étalage Kpodzi", "tel": "", "montant": Decimal("750.00")},
            {"jours_offset": -4, "emplacement_idx": 3, "contribuable_idx": 9, "nom_vendeur": "Séna Worou", "tel": "+228 99 01 23 45", "montant": Decimal("1000.00")},
            {"jours_offset": -5, "emplacement_idx": 0, "contribuable_idx": None, "nom_vendeur": "Vendeuse anonyme 2", "tel": "", "montant": Decimal("500.00")},
            {"jours_offset": -7, "emplacement_idx": 0, "contribuable_idx": 1, "nom_vendeur": "Koffi Gbado", "tel": "+228 91 23 45 67", "montant": Decimal("1000.00")},
        ]
        for t in tickets_data:
            ticket_date = aujourd_hui + timedelta(days=t["jours_offset"])
            contrib = contribuables[t["contribuable_idx"]] if t["contribuable_idx"] is not None else None
            if TicketMarche.objects.filter(
                date=ticket_date,
                emplacement=emplacements[t["emplacement_idx"]],
                nom_vendeur=t["nom_vendeur"],
            ).exists() and not force:
                continue
            TicketMarche.objects.create(
                date=ticket_date,
                emplacement=emplacements[t["emplacement_idx"]],
                contribuable=contrib,
                nom_vendeur=t["nom_vendeur"],
                telephone_vendeur=t["tel"],
                montant=t["montant"],
                encaisse_par_agent=agent_collecteur,
                encaisse_par=agent_user,
                notes="Ticket étalage",
            )
        self.stdout.write(f"  {len(tickets_data)} tickets marché créés.")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Résumé:"))
        self.stdout.write(f"  - Emplacements marché : {EmplacementMarche.objects.count()}")
        self.stdout.write(f"  - Contribuables : {Contribuable.objects.count()}")
        self.stdout.write(f"  - Boutiques / Magasins : {BoutiqueMagasin.objects.count()}")
        self.stdout.write(f"  - Cotisations annuelles : {CotisationAnnuelle.objects.count()}")
        self.stdout.write(f"  - Paiements cotisation (mensuels) : {PaiementCotisation.objects.count()}")
        self.stdout.write(f"  - Tickets marché (étalages) : {TicketMarche.objects.count()}")
        self.stdout.write(self.style.SUCCESS("Terminé. Consultez l'admin ou « Mon compte » pour les contribuables."))
