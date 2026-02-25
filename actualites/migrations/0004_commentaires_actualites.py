from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("actualites", "0003_restructure_photos_titres_textes"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CommentaireActualite",
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
                ("nom", models.CharField(help_text="Nom ou prénom du citoyen.", max_length=150)),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        help_text="Adresse e-mail (facultative).",
                        max_length=254,
                    ),
                ),
                (
                    "texte",
                    models.TextField(help_text="Contenu du commentaire."),
                ),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                (
                    "est_valide",
                    models.BooleanField(
                        default=True,
                        help_text="Si décoché, le commentaire n'est pas affiché publiquement.",
                    ),
                ),
                (
                    "actualite",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="commentaires",
                        to="actualites.actualite",
                    ),
                ),
                (
                    "utilisateur",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="commentaires_actualites",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Commentaire d'actualité",
                "verbose_name_plural": "Commentaires d'actualités",
                "ordering": ["-date_creation"],
            },
        ),
    ]

