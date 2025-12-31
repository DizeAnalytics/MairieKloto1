from django.db import models


class Actualite(models.Model):
    """Actualité publiée par la mairie (avec jusqu'à 3 photos)."""

    titre = models.CharField(max_length=255)
    resume = models.TextField(
        blank=True,
        help_text="Court résumé qui apparaît sur la page d'accueil.",
    )
    contenu = models.TextField(
        blank=True,
        help_text="Contenu détaillé de l'actualité (ancien format, conservé pour compatibilité)."
    )

    # Bloc 1 : Photo 1 - Titre 1 - Texte 1
    photo1 = models.FileField(
        upload_to="actualites/photos/", blank=True, null=True, help_text="Première photo"
    )
    titre1 = models.CharField(
        max_length=255, blank=True, help_text="Titre pour la première photo"
    )
    texte1 = models.TextField(
        blank=True,
        help_text="Texte pour la première photo."
    )

    # Bloc 2 : Photo 2 - Titre 2 - Texte 2
    photo2 = models.FileField(
        upload_to="actualites/photos/", blank=True, null=True, help_text="Deuxième photo"
    )
    titre2 = models.CharField(
        max_length=255, blank=True, help_text="Titre pour la deuxième photo"
    )
    texte2 = models.TextField(
        blank=True,
        help_text="Texte pour la deuxième photo."
    )

    # Bloc 3 : Photo 3 - Titre 3 - Texte 3
    photo3 = models.FileField(
        upload_to="actualites/photos/", blank=True, null=True, help_text="Troisième photo"
    )
    titre3 = models.CharField(
        max_length=255, blank=True, help_text="Titre pour la troisième photo"
    )
    texte3 = models.TextField(
        blank=True,
        help_text="Texte pour la troisième photo."
    )

    date_publication = models.DateTimeField(auto_now_add=True)
    est_publie = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_publication"]
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"

    def __str__(self) -> str:
        return self.titre


