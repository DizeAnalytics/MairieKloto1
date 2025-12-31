from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


def validate_file_size(value):
    limit = 5 * 1024 * 1024  # 5 Mo
    if value.size > limit:
        raise ValidationError('Le fichier est trop volumineux (max 5 Mo).')


class MotMaire(models.Model):
    """Mot de bienvenue du maire."""
    
    titre = models.CharField(
        max_length=255,
        default="Mot du Maire",
        help_text="Titre du message (ex: 'Mot du Maire', 'Bienvenue', etc.)"
    )
    contenu = models.TextField(
        validators=[MinLengthValidator(50)],
        help_text="Message de bienvenue du maire (minimum 50 caractères)"
    )
    nom_maire = models.CharField(
        max_length=255,
        help_text="Nom complet du maire"
    )
    photo_maire = models.ImageField(
        upload_to="mairie/photos/",
        blank=True,
        null=True,
        help_text="Photo du maire"
    )
    signature = models.ImageField(
        upload_to="mairie/signatures/",
        blank=True,
        null=True,
        help_text="Signature du maire"
    )
    est_actif = models.BooleanField(
        default=True,
        help_text="Afficher ce message sur la page d'accueil"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mot du maire"
        verbose_name_plural = "Mots du maire"
        ordering = ["-date_modification"]

    def __str__(self):
        return f"Mot du maire - {self.nom_maire}"


class Collaborateur(models.Model):
    """Collaborateurs et membres du bureau de la mairie."""
    
    FONCTION_CHOICES = [
        ("maire", "Maire"),
        ("premier_adjoint", "Premier Adjoint au Maire"),
        ("adjoint", "Adjoint au Maire"),
        ("secretaire_general", "Secrétaire Général"),
        ("directeur", "Directeur"),
        ("chef_service", "Chef de Service"),
        ("conseiller", "Conseiller Municipal"),
        ("autre", "Autre"),
    ]

    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=150)
    fonction = models.CharField(
        max_length=50,
        choices=FONCTION_CHOICES,
        help_text="Fonction dans la mairie"
    )
    fonction_custom = models.CharField(
        max_length=255,
        blank=True,
        help_text="Fonction personnalisée (si 'Autre' est sélectionné)"
    )
    photo = models.ImageField(
        upload_to="mairie/collaborateurs/",
        blank=True,
        null=True,
        help_text="Photo du collaborateur"
    )
    telephone = models.CharField(
        max_length=30,
        blank=True,
        help_text="Numéro de téléphone"
    )
    email = models.EmailField(
        blank=True,
        help_text="Adresse email"
    )
    bureau = models.CharField(
        max_length=255,
        blank=True,
        help_text="Localisation du bureau (ex: 'Bureau 101, 1er étage')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description des responsabilités et compétences"
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage (0 = premier, plus grand = plus bas)"
    )
    est_visible = models.BooleanField(
        default=True,
        help_text="Afficher ce collaborateur sur la page d'accueil"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Collaborateur"
        verbose_name_plural = "Collaborateurs"
        ordering = ["ordre_affichage", "fonction", "nom"]

    def __str__(self):
        fonction_display = self.get_fonction_display() if self.fonction != "autre" else self.fonction_custom
        return f"{self.nom} {self.prenoms} - {fonction_display}"

    def get_fonction_complete(self):
        """Retourne la fonction complète (choix ou custom)."""
        if self.fonction == "autre" and self.fonction_custom:
            return self.fonction_custom
        return self.get_fonction_display()


class InformationMairie(models.Model):
    """Informations générales sur la mairie (contacts, horaires, etc.)."""
    
    TYPE_INFO_CHOICES = [
        ("contact", "Contact"),
        ("horaire", "Horaires"),
        ("adresse", "Adresse"),
        ("mission", "Mission/Vision"),
        ("histoire", "Histoire"),
        ("autre", "Autre"),
    ]

    type_info = models.CharField(
        max_length=20,
        choices=TYPE_INFO_CHOICES,
        default="autre"
    )
    titre = models.CharField(max_length=255)
    contenu = models.TextField()
    icone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icône (ex: '📞', '🕒', '📍', etc.)"
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage"
    )
    est_visible = models.BooleanField(
        default=True,
        help_text="Afficher cette information sur la page d'accueil"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Information mairie"
        verbose_name_plural = "Informations mairie"
        ordering = ["ordre_affichage", "type_info", "titre"]

    def __str__(self):
        return f"{self.get_type_info_display()}: {self.titre}"


class AppelOffre(models.Model):
    """Appel d'offres lancé par la mairie, ouvert à un ou plusieurs publics cibles."""

    PUBLIC_CIBLE_CHOICES = [
        ("entreprises", "Entreprises / Acteurs économiques"),
        ("institutions", "Institutions financières"),
        ("jeunes", "Jeunes en quête d'emploi"),
        ("retraites", "Retraités actifs"),
        ("tous", "Tout le monde"),
    ]

    STATUT_CHOICES = [
        ("brouillon", "Brouillon"),
        ("publie", "Publié"),
        ("cloture", "Clôturé"),
        ("archive", "Archivé"),
    ]

    titre = models.CharField(max_length=255)
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Référence interne de l'appel d'offres (ex: A0-2025-001).",
    )
    description = models.TextField(
        help_text="Description détaillée de l'appel d'offres, objet, objectifs, conditions."
    )

    public_cible = models.CharField(
        max_length=20,
        choices=PUBLIC_CIBLE_CHOICES,
        default="tous",
        help_text="Public principalement visé par cet appel d'offres.",
    )

    date_debut = models.DateTimeField(
        help_text="Date et heure d'ouverture de l'appel d'offres."
    )
    date_fin = models.DateTimeField(
        help_text="Date et heure de clôture de l'appel d'offres."
    )

    budget_estime = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Budget estimé ou montant indicatif (facultatif).",
    )

    document_officiel = models.FileField(
        upload_to="mairie/appels_offres/",
        blank=True,
        null=True,
        help_text="Cahier des charges ou document officiel de l'appel d'offres (PDF, DOC, etc.).",
    )

    criteres_selection = models.TextField(
        blank=True,
        help_text="Résumé des critères de sélection (facultatif, pour affichage rapide).",
    )

    dossier_candidature = models.TextField(
        blank=True,
        help_text="Liste des pièces à fournir pour le dossier de candidature.",
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="brouillon",
        help_text="Statut de l'appel d'offres.",
    )

    est_publie_sur_site = models.BooleanField(
        default=False,
        help_text="Cocher pour afficher cet appel d'offres sur la plateforme publique.",
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Appel d'offres"
        verbose_name_plural = "Appels d'offres"
        ordering = ["-date_debut", "-date_creation"]

    def __str__(self) -> str:
        return f"{self.titre} ({self.reference or 'sans réf.'})"


class Candidature(models.Model):
    """Candidature soumise pour un appel d'offres."""
    
    STATUT_CANDIDATURE = [
        ("en_attente", "En attente"),
        ("acceptee", "Acceptée"),
        ("refusee", "Refusée"),
    ]

    appel_offre = models.ForeignKey(
        AppelOffre,
        on_delete=models.CASCADE,
        related_name="candidatures",
        verbose_name="Appel d'offres concerné"
    )
    candidat = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="candidatures",
        verbose_name="Candidat"
    )
    
    fichier_dossier = models.FileField(
        upload_to="mairie/candidatures/",
        validators=[validate_file_size],
        help_text="Dossier complet (PDF uniquement, max 5 Mo).",
        verbose_name="Dossier de candidature (PDF)"
    )
    
    date_soumission = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CANDIDATURE,
        default="en_attente",
        verbose_name="Statut de la candidature"
    )
    
    message_accompagnement = models.TextField(
        blank=True,
        verbose_name="Message d'accompagnement (facultatif)"
    )

    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        ordering = ["-date_soumission"]
        unique_together = ["appel_offre", "candidat"]

    def __str__(self):
        return f"Candidature de {self.candidat.get_full_name() or self.candidat.username} pour {self.appel_offre.reference}"
