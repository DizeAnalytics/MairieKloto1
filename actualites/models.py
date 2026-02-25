from django.db import models
from django.conf import settings


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


class CommentaireActualite(models.Model):
    """Commentaire laissé par un citoyen sur une actualité donnée."""

    actualite = models.ForeignKey(
        Actualite,
        related_name="commentaires",
        on_delete=models.CASCADE,
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="commentaires_actualites",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    nom = models.CharField(
        max_length=150,
        help_text="Nom ou prénom du citoyen.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Adresse e-mail (facultative).",
    )
    texte = models.TextField(
        help_text="Contenu du commentaire.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    est_valide = models.BooleanField(
        default=True,
        help_text="Si décoché, le commentaire n'est pas affiché publiquement.",
    )

    class Meta:
        ordering = ["-date_creation"]
        verbose_name = "Commentaire d'actualité"
        verbose_name_plural = "Commentaires d'actualités"

    def __str__(self) -> str:
        return f"Commentaire de {self.nom} sur « {self.actualite} »"


