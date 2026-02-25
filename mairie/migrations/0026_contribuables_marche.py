# Generated manually for contribuables (marchés / places publiques)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("mairie", "0025_partenaire"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EmplacementMarche",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("canton", models.CharField(blank=True, help_text="Canton où se situe le marché ou la place.", max_length=100)),
                ("village", models.CharField(blank=True, help_text="Village (si applicable).", max_length=150)),
                ("quartier", models.CharField(help_text="Quartier ou secteur (ex: Centre-ville, Marché central).", max_length=150)),
                ("nom_lieu", models.CharField(help_text="Nom du lieu (ex: Marché central de Kpalimé, Place publique X).", max_length=255)),
                ("description", models.TextField(blank=True, help_text="Description du lieu (accès, horaires du marché, etc.).")),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("date_modification", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Emplacement (marché / place publique)",
                "verbose_name_plural": "Emplacements (marchés / places publiques)",
                "ordering": ["canton", "quartier", "nom_lieu"],
            },
        ),
        migrations.CreateModel(
            name="Contribuable",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(help_text="Nom de famille.", max_length=100)),
                ("prenom", models.CharField(help_text="Prénom(s).", max_length=150)),
                ("telephone", models.CharField(help_text="Numéro de téléphone du contribuable.", max_length=30)),
                ("date_naissance", models.DateField(blank=True, help_text="Date de naissance.", null=True)),
                ("lieu_naissance", models.CharField(blank=True, help_text="Lieu de naissance.", max_length=255)),
                ("nationalite", models.CharField(default="Togolaise", help_text="Nationalité.", max_length=100)),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("date_modification", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        help_text="Compte utilisateur pour « Mon compte » (consultation des cotisations).",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="contribuable",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Contribuable (marché / place publique)",
                "verbose_name_plural": "Contribuables (marchés / places publiques)",
                "ordering": ["nom", "prenom"],
            },
        ),
        migrations.CreateModel(
            name="BoutiqueMagasin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "matricule",
                    models.CharField(help_text="Matricule unique du local (ex: MKT-2025-001).", max_length=50, unique=True),
                ),
                (
                    "type_local",
                    models.CharField(
                        choices=[("magasin", "Magasin"), ("boutique", "Boutique"), ("local", "Local")],
                        default="boutique",
                        help_text="Type de local.",
                        max_length=20,
                    ),
                ),
                ("superficie_m2", models.DecimalField(decimal_places=2, help_text="Superficie en m².", max_digits=10)),
                ("prix_location_mensuel", models.DecimalField(decimal_places=2, help_text="Prix de location mensuel (FCFA).", max_digits=12)),
                (
                    "prix_location_annuel",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Prix de location annuelle (FCFA), si différent de 12 × mensuel.",
                        max_digits=12,
                        null=True,
                    ),
                ),
                (
                    "activite_vendue",
                    models.CharField(
                        help_text="Que vend le locataire ? (ex: légumes, vêtements, épices).",
                        max_length=255,
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, help_text="Description complémentaire du local ou de l'activité."),
                ),
                ("est_actif", models.BooleanField(default=True, help_text="Local actuellement occupé / actif.")),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("date_modification", models.DateTimeField(auto_now=True)),
                (
                    "contribuable",
                    models.ForeignKey(
                        help_text="Locataire (contribuable) du local.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="boutiques_magasins",
                        to="mairie.contribuable",
                    ),
                ),
                (
                    "emplacement",
                    models.ForeignKey(
                        help_text="Marché ou place publique où se situe le local.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="boutiques_magasins",
                        to="mairie.emplacementmarche",
                    ),
                ),
            ],
            options={
                "verbose_name": "Boutique / Magasin (marché)",
                "verbose_name_plural": "Boutiques / Magasins (marché)",
                "ordering": ["emplacement", "matricule"],
            },
        ),
        migrations.CreateModel(
            name="CotisationAnnuelle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("annee", models.PositiveIntegerField(help_text="Année de cotisation (ex: 2025).")),
                (
                    "montant_annuel_du",
                    models.DecimalField(decimal_places=2, help_text="Montant total dû pour l'année (FCFA).", max_digits=12),
                ),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("date_modification", models.DateTimeField(auto_now=True)),
                (
                    "boutique",
                    models.ForeignKey(
                        help_text="Boutique ou magasin concerné.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cotisations_annuelles",
                        to="mairie.boutiquemagasin",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cotisation annuelle (boutique/magasin)",
                "verbose_name_plural": "Cotisations annuelles (boutiques/magasins)",
                "ordering": ["-annee", "boutique"],
                "unique_together": {("boutique", "annee")},
            },
        ),
        migrations.CreateModel(
            name="PaiementCotisation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "mois",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Mois 1"),
                            (2, "Mois 2"),
                            (3, "Mois 3"),
                            (4, "Mois 4"),
                            (5, "Mois 5"),
                            (6, "Mois 6"),
                            (7, "Mois 7"),
                            (8, "Mois 8"),
                            (9, "Mois 9"),
                            (10, "Mois 10"),
                            (11, "Mois 11"),
                            (12, "Mois 12"),
                        ],
                        help_text="Mois concerné (1-12).",
                    ),
                ),
                ("montant_paye", models.DecimalField(decimal_places=2, help_text="Montant payé (FCFA).", max_digits=12)),
                (
                    "date_paiement",
                    models.DateTimeField(default=django.utils.timezone.now, help_text="Date et heure du paiement."),
                ),
                ("notes", models.TextField(blank=True, help_text="Notes éventuelles (mode de paiement, reçu, etc.).")),
                (
                    "cotisation_annuelle",
                    models.ForeignKey(
                        help_text="Cotisation annuelle concernée.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="paiements",
                        to="mairie.cotisationannuelle",
                    ),
                ),
                (
                    "encaisse_par",
                    models.ForeignKey(
                        blank=True,
                        help_text="Agent de la mairie ayant encaissé.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="paiements_cotisations_encaisses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Paiement de cotisation (mois)",
                "verbose_name_plural": "Paiements de cotisation (mois)",
                "ordering": ["cotisation_annuelle", "mois"],
                "unique_together": {("cotisation_annuelle", "mois")},
            },
        ),
        migrations.CreateModel(
            name="TicketMarche",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(help_text="Date du jour de marché.")),
                (
                    "nom_vendeur",
                    models.CharField(help_text="Nom du vendeur (étalage) si différent du contribuable.", max_length=255),
                ),
                ("telephone_vendeur", models.CharField(blank=True, help_text="Téléphone du vendeur.", max_length=30)),
                ("montant", models.DecimalField(decimal_places=2, help_text="Montant du ticket (FCFA).", max_digits=10)),
                ("notes", models.TextField(blank=True, help_text="Notes éventuelles.")),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                (
                    "contribuable",
                    models.ForeignKey(
                        blank=True,
                        help_text="Contribuable identifié (si déjà enregistré).",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tickets_marche",
                        to="mairie.contribuable",
                    ),
                ),
                (
                    "emplacement",
                    models.ForeignKey(
                        help_text="Marché où le ticket a été vendu.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tickets_marche",
                        to="mairie.emplacementmarche",
                    ),
                ),
                (
                    "encaisse_par",
                    models.ForeignKey(
                        blank=True,
                        help_text="Agent de la mairie ayant vendu le ticket.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tickets_marche_encaisses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Ticket marché (étalage)",
                "verbose_name_plural": "Tickets marché (étalages)",
                "ordering": ["-date", "-date_creation"],
            },
        ),
    ]
