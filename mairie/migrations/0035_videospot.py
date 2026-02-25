from django.db import migrations, models

import mairie.models


class Migration(migrations.Migration):

    dependencies = [
        ("mairie", "0034_alter_sectiondirection_direction_divisiondirection_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="VideoSpot",
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
                ("titre", models.CharField(max_length=255)),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Texte descriptif court de la vidéo ou du spot.",
                    ),
                ),
                (
                    "fichier_video",
                    models.FileField(
                        blank=True,
                        help_text="Fichier vidéo court (ex: spot de 5 minutes).",
                        null=True,
                        upload_to="mairie/videos_spots/",
                        validators=[mairie.models.validate_file_size],
                    ),
                ),
                (
                    "vignette",
                    models.ImageField(
                        blank=True,
                        help_text="Vignette optionnelle pour illustrer la vidéo.",
                        null=True,
                        upload_to="mairie/videos_spots/vignettes/",
                        validators=[mairie.models.validate_file_size],
                    ),
                ),
                (
                    "url_externe",
                    models.URLField(
                        blank=True,
                        help_text="Lien pour voir la suite (YouTube, Facebook, etc.).",
                    ),
                ),
                (
                    "est_active",
                    models.BooleanField(
                        default=True,
                        help_text="Afficher ce spot vidéo sur les pages d'accueil et d'actualités.",
                    ),
                ),
                (
                    "date_debut",
                    models.DateTimeField(
                        blank=True,
                        help_text="Date de début de diffusion de ce spot (facultatif).",
                        null=True,
                    ),
                ),
                (
                    "date_fin",
                    models.DateTimeField(
                        blank=True,
                        help_text="Date de fin de diffusion de ce spot (facultatif).",
                        null=True,
                    ),
                ),
                (
                    "ordre_priorite",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Permet de donner la priorité à certains spots (0 = priorité normale).",
                    ),
                ),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Spot vidéo",
                "verbose_name_plural": "Spots vidéos",
                "ordering": ["ordre_priorite", "-date_creation"],
            },
        ),
    ]

