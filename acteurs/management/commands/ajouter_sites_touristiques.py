from django.core.management.base import BaseCommand
from decimal import Decimal

from acteurs.models import SiteTouristique


class Command(BaseCommand):
    help = "Ajoute 5 sites touristiques validés par la mairie"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Début de l'ajout des sites touristiques..."))

        sites_data = [
            {
                "nom_site": "Cascade de Kpimé",
                "categorie_site": "cascade",
                "description": "Belle cascade située à proximité de Kpalimé, entourée d'une végétation luxuriante.",
                "particularite": "Point de vue panoramique et bassins naturels.",
                "prix_visite": Decimal("1000.00"),
                "horaires_visite": "08h00–17h00",
                "jours_ouverture": "Tous les jours",
                "quartier": "Kpimé",
                "canton": "Kpalimé",
                "adresse_complete": "Route de Kpimé, après le pont",
                "coordonnees_gps": "6.9530, 0.6270",
                "guide_disponible": True,
                "parking_disponible": True,
                "restauration_disponible": False,
                "acces_handicapes": False,
                "telephone_contact": "+22890100100",
                "site_web": "",
                "conditions_acces": "Chaussures de marche recommandées",
                "est_valide_par_mairie": True,
            },
            {
                "nom_site": "Mont Agou",
                "categorie_site": "montagne",
                "description": "Point culminant du Togo, idéal pour la randonnée et l'observation.",
                "particularite": "Panorama sur la région des Plateaux.",
                "prix_visite": Decimal("2000.00"),
                "horaires_visite": "07h00–16h00",
                "jours_ouverture": "Tous les jours",
                "quartier": "Agou",
                "canton": "Kpalimé",
                "adresse_complete": "Piste du Mont Agou",
                "coordonnees_gps": "6.8450, 0.6275",
                "guide_disponible": True,
                "parking_disponible": True,
                "restauration_disponible": True,
                "acces_handicapes": False,
                "telephone_contact": "+22890200200",
                "site_web": "",
                "conditions_acces": "Autorisation locale pour certains parcours",
                "est_valide_par_mairie": True,
            },
            {
                "nom_site": "Forêt de Missahohé",
                "categorie_site": "foret",
                "description": "Forêt dense avec biodiversité riche, idéale pour l'écotourisme.",
                "particularite": "Espèces végétales endémiques.",
                "prix_visite": Decimal("1500.00"),
                "horaires_visite": "08h00–17h00",
                "jours_ouverture": "Lundi–Samedi",
                "quartier": "Missahohé",
                "canton": "Kpalimé",
                "adresse_complete": "Entrée de la forêt de Missahohé",
                "coordonnees_gps": "6.9035, 0.6380",
                "guide_disponible": True,
                "parking_disponible": False,
                "restauration_disponible": False,
                "acces_handicapes": False,
                "telephone_contact": "+22890300300",
                "site_web": "",
                "conditions_acces": "Respect strict des consignes environnementales",
                "est_valide_par_mairie": True,
            },
            {
                "nom_site": "Jardin Botanique de Kloto",
                "categorie_site": "parc",
                "description": "Espace botanique mettant en valeur les plantes locales et médicinales.",
                "particularite": "Visites guidées pédagogiques.",
                "prix_visite": Decimal("800.00"),
                "horaires_visite": "09h00–18h00",
                "jours_ouverture": "Mardi–Dimanche",
                "quartier": "Centre-ville",
                "canton": "Kpalimé",
                "adresse_complete": "Avenue des Fleurs",
                "coordonnees_gps": "6.9000, 0.6200",
                "guide_disponible": True,
                "parking_disponible": True,
                "restauration_disponible": True,
                "acces_handicapes": True,
                "telephone_contact": "+22890400400",
                "site_web": "",
                "conditions_acces": "Accès libre, enfants accompagnés",
                "est_valide_par_mairie": True,
            },
            {
                "nom_site": "Monument des Indépendances",
                "categorie_site": "monument",
                "description": "Monument historique commémorant l'indépendance nationale.",
                "particularite": "Architecture symbolique et plaques commémoratives.",
                "prix_visite": Decimal("500.00"),
                "horaires_visite": "08h00–18h00",
                "jours_ouverture": "Tous les jours",
                "quartier": "Quartier Administratif",
                "canton": "Kpalimé",
                "adresse_complete": "Place de l'Indépendance",
                "coordonnees_gps": "6.9100, 0.6300",
                "guide_disponible": False,
                "parking_disponible": True,
                "restauration_disponible": False,
                "acces_handicapes": True,
                "telephone_contact": "+22890500500",
                "site_web": "",
                "conditions_acces": "Accès libre, respect du lieu",
                "est_valide_par_mairie": True,
            },
        ]

        for i, data in enumerate(sites_data, 1):
            site, created = SiteTouristique.objects.get_or_create(
                nom_site=data["nom_site"],
                defaults=data,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Site touristique {i} créé : {site.nom_site}"))
            else:
                self.stdout.write(self.style.WARNING(f"  - Site touristique {i} existe déjà : {site.nom_site}"))

        self.stdout.write(self.style.SUCCESS("\n✓ Ajout des sites touristiques terminé avec succès !"))
