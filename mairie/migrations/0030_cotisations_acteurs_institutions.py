# Generated migration for cotisations acteurs économiques et institutions financières

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ("mairie", "0029_boutiquemagasin_agent_collecteur"),
        ("acteurs", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CotisationAnnuelleActeur",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "annee",
                    models.PositiveIntegerField(
                        help_text="Année de cotisation (ex: 2025)."
                    ),
                ),
                (
                    "montant_annuel_du",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Montant total dû pour l'année (FCFA).",
                        max_digits=12,
                    ),
                ),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("date_modification", models.DateTimeField(auto_now=True)),
                (
                    "acteur",
                    models.ForeignKey(
                        help_text="Acteur économique concerné.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cotisations_annuelles",
                        to="acteurs.acteureconomique",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cotisation annuelle (acteur économique)",
                "verbose_name_plural": "Cotisations annuelles (acteurs économiques)",
                "ordering": ["-annee", "acteur"],
                "unique_together": {("acteur", "annee")},
            },
        ),
        migrations.CreateModel(
            name="CotisationAnnuelleInstitution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "annee",
                    models.PositiveIntegerField(
                        help_text="Année de cotisation (ex: 2025)."
                    ),
                ),
                (
                    "montant_annuel_du",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Montant total dû pour l'année (FCFA).",
                        max_digits=12,
                    ),
                ),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("date_modification", models.DateTimeField(auto_now=True)),
                (
                    "institution",
                    models.ForeignKey(
                        help_text="Institution financière concernée.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cotisations_annuelles",
                        to="acteurs.institutionfinanciere",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cotisation annuelle (institution financière)",
                "verbose_name_plural": "Cotisations annuelles (institutions financières)",
                "ordering": ["-annee", "institution"],
                "unique_together": {("institution", "annee")},
            },
        ),
        migrations.CreateModel(
            name="PaiementCotisationActeur",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "montant_paye",
                    models.DecimalField(
                        decimal_places=2, help_text="Montant payé (FCFA).", max_digits=12
                    ),
                ),
                (
                    "date_paiement",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="Date et heure du paiement.",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Notes éventuelles (mode de paiement, reçu, etc.).",
                    ),
                ),
                (
                    "cotisation_annuelle",
                    models.ForeignKey(
                        help_text="Cotisation annuelle concernée.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="paiements",
                        to="mairie.cotisationannuelleacteur",
                    ),
                ),
                (
                    "encaisse_par_agent",
                    models.ForeignKey(
                        blank=True,
                        help_text="Agent collecteur ayant encaissé ce paiement.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="paiements_cotisations_acteurs_encaisses",
                        to="mairie.agentcollecteur",
                    ),
                ),
            ],
            options={
                "verbose_name": "Paiement de cotisation (acteur économique)",
                "verbose_name_plural": "Paiements de cotisation (acteurs économiques)",
                "ordering": ["-date_paiement", "cotisation_annuelle"],
            },
        ),
        migrations.CreateModel(
            name="PaiementCotisationInstitution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "montant_paye",
                    models.DecimalField(
                        decimal_places=2, help_text="Montant payé (FCFA).", max_digits=12
                    ),
                ),
                (
                    "date_paiement",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="Date et heure du paiement.",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Notes éventuelles (mode de paiement, reçu, etc.).",
                    ),
                ),
                (
                    "cotisation_annuelle",
                    models.ForeignKey(
                        help_text="Cotisation annuelle concernée.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="paiements",
                        to="mairie.cotisationannuelleinstitution",
                    ),
                ),
                (
                    "encaisse_par_agent",
                    models.ForeignKey(
                        blank=True,
                        help_text="Agent collecteur ayant encaissé ce paiement.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="paiements_cotisations_institutions_encaisses",
                        to="mairie.agentcollecteur",
                    ),
                ),
            ],
            options={
                "verbose_name": "Paiement de cotisation (institution financière)",
                "verbose_name_plural": "Paiements de cotisation (institutions financières)",
                "ordering": ["-date_paiement", "cotisation_annuelle"],
            },
        ),
    ]
