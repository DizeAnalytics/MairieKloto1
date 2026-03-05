from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


def validate_file_size(value):
    limit = 5 * 1024 * 1024  # 5 Mo
    if value.size > limit:
        raise ValidationError("Le fichier est trop volumineux (max 5 Mo).")


def validate_video_size(value):
    limit = 25 * 1024 * 1024  # 25 Mo
    if value.size > limit:
        raise ValidationError("La vidéo est trop volumineuse (max 25 Mo).")


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


class DirectionMairie(models.Model):
    """
    Direction de la mairie (ex: Direction des affaires administratives, Direction des services techniques).
    Reliée à l'organigramme sous la supervision du Secrétaire Général.
    """

    nom = models.CharField(
        max_length=255,
        help_text="Nom complet de la direction (ex: Direction des affaires administratives, ressources humaines et état civil).",
    )
    sigle = models.CharField(
        max_length=50,
        blank=True,
        help_text="Sigle de la direction (ex: DAARHEC).",
    )
    chef_direction = models.CharField(
        max_length=255,
        help_text="Nom du Chef de direction.",
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage dans l'organigramme (de gauche à droite).",
    )
    est_active = models.BooleanField(
        default=True,
        help_text="Afficher cette direction dans l'organigramme public.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Direction de la mairie"
        verbose_name_plural = "Directions de la mairie"
        ordering = ["ordre_affichage", "nom"]

    def __str__(self) -> str:
        if self.sigle:
            return f"{self.nom} ({self.sigle})"
        return self.nom


class DivisionDirection(models.Model):
    """
    Division rattachée à une direction (niveau intermédiaire entre la direction et les sections).
    Exemple : Division des affaires administratives, Division des services techniques, etc.
    """

    direction = models.ForeignKey(
        DirectionMairie,
        on_delete=models.CASCADE,
        related_name="divisions",
        help_text="Direction à laquelle cette division est rattachée.",
    )
    nom = models.CharField(
        max_length=255,
        help_text="Nom complet de la division.",
    )
    sigle = models.CharField(
        max_length=50,
        blank=True,
        help_text="Sigle de la division (facultatif).",
    )
    chef_division = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nom du Chef de division (facultatif).",
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage de la division à l'intérieur de la direction.",
    )
    est_active = models.BooleanField(
        default=True,
        help_text="Afficher cette division dans l'organigramme public.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Division de direction"
        verbose_name_plural = "Divisions de direction"
        ordering = ["direction", "ordre_affichage", "nom"]

    def __str__(self) -> str:
        if self.sigle:
            return f"{self.nom} ({self.sigle})"
        return self.nom


class SectionDirection(models.Model):
    """
    Section rattachée à une direction (ex: Section état civil, Section ressources humaines).
    """

    direction = models.ForeignKey(
        DirectionMairie,
        on_delete=models.CASCADE,
        related_name="sections",
        help_text="Direction à laquelle cette section est rattachée (pour compatibilité).",
    )
    division = models.ForeignKey(
        "DivisionDirection",
        on_delete=models.CASCADE,
        related_name="sections",
        null=True,
        blank=True,
        help_text="Division à laquelle cette section est rattachée (niveau intermédiaire).",
    )
    nom = models.CharField(
        max_length=255,
        help_text="Nom complet de la section.",
    )
    sigle = models.CharField(
        max_length=50,
        blank=True,
        help_text="Sigle de la section (facultatif).",
    )
    chef_section = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nom du Chef de section.",
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage de la section à l'intérieur de la direction.",
    )
    est_active = models.BooleanField(
        default=True,
        help_text="Afficher cette section dans l'organigramme public.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Section de direction"
        verbose_name_plural = "Sections de direction"
        ordering = ["direction", "ordre_affichage", "nom"]

    def __str__(self) -> str:
        if self.sigle:
            return f"{self.nom} ({self.sigle})"
        return self.nom


class PersonnelSection(models.Model):
    """
    Personnel rattaché à une section (organigramme détaillé du personnel).
    """

    section = models.ForeignKey(
        SectionDirection,
        on_delete=models.CASCADE,
        related_name="personnels",
        help_text="Section à laquelle ce membre du personnel est rattaché.",
    )
    nom_prenoms = models.CharField(
        max_length=255,
        help_text="Nom et prénoms du membre du personnel.",
    )
    adresse = models.CharField(
        max_length=255,
        blank=True,
        help_text="Adresse (facultatif).",
    )
    contact = models.CharField(
        max_length=100,
        blank=True,
        help_text="Contact téléphonique ou email.",
    )
    fonction = models.CharField(
        max_length=255,
        help_text="Fonction occupée dans la section.",
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage dans la section.",
    )
    est_actif = models.BooleanField(
        default=True,
        help_text="Afficher ce membre du personnel dans l'organigramme public.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Personnel de section"
        verbose_name_plural = "Personnel des sections"
        ordering = ["section", "ordre_affichage", "nom_prenoms"]

    def __str__(self) -> str:
        return f"{self.nom_prenoms} - {self.fonction}"


class ServiceSection(models.Model):
    """
    Service rattaché à une section (ex: Service état civil, Service ressources humaines).
    """

    section = models.ForeignKey(
        SectionDirection,
        on_delete=models.CASCADE,
        related_name="services",
        help_text="Section à laquelle ce service est rattaché.",
    )
    titre = models.CharField(
        max_length=255,
        help_text="Titre du service.",
    )
    description = models.TextField(
        blank=True,
        help_text="Description des missions et activités du service (facultatif).",
    )
    responsable = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nom du responsable du service (facultatif).",
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage du service dans la section.",
    )
    est_actif = models.BooleanField(
        default=True,
        help_text="Afficher ce service dans l'organigramme public.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service de section"
        verbose_name_plural = "Services de section"
        ordering = ["section", "ordre_affichage", "titre"]

    def __str__(self) -> str:
        return self.titre


class InformationMairie(models.Model):
    """Informations générales sur la mairie (contacts, horaires, etc.)."""
    
    TYPE_INFO_CHOICES = [
        ("contact", "Contact"),
        ("horaire", "Horaires"),
        ("adresse", "Adresse"),
        ("mission", "Mission/Vision"),
        ("histoire", "Histoire"),
        ("pdc", "PDC"),
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


class InformationMairieImage(models.Model):
    """
    Image(s) associée(s) à une information de la mairie (bloc 'Informations Utiles').
    Permet d'illustrer des contenus comme la mission/vision avec une ou plusieurs images.
    """

    information = models.ForeignKey(
        InformationMairie,
        on_delete=models.CASCADE,
        related_name="images",
        help_text="Information à laquelle cette image est rattachée.",
    )
    image = models.ImageField(
        upload_to="mairie/informations/",
        validators=[validate_file_size],
        help_text="Image illustrative pour ce bloc d'information.",
    )
    legende = models.CharField(
        max_length=255,
        blank=True,
        help_text="Légende facultative affichée sous l'image.",
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage des images pour cette information.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Image pour information mairie"
        verbose_name_plural = "Images pour informations mairie"
        ordering = ["information", "ordre_affichage", "pk"]

    def __str__(self):
        return f"Image pour {self.information.titre} (#{self.pk})"


class AppelOffre(models.Model):
    """Appel d'offres lancé par la mairie, ouvert à un ou plusieurs publics cibles."""

    PUBLIC_CIBLE_CHOICES = [
        ("entreprises", "Entreprises / Acteurs économiques"),
        ("institutions", "Institutions financières"),
        ("entreprises_institutions", "Entreprises et Institutions financières"),
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
        max_length=30,
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


class ImageCarousel(models.Model):
    """Images pour le carousel de la page d'accueil."""
    
    image = models.ImageField(
        upload_to="mairie/carousel/",
        help_text="Image pour le carousel (recommandé: 1920x800px ou ratio 16:9)"
    )
    titre = models.CharField(
        max_length=255,
        blank=True,
        help_text="Titre optionnel pour l'image"
    )
    description = models.TextField(
        blank=True,
        help_text="Description optionnelle pour l'image"
    )
    # Jusqu'à 3 boutons d'action affichés sur l'image du carousel
    bouton1_texte = models.CharField(
        max_length=100,
        blank=True,
        help_text="Texte du premier bouton (ex: 'En savoir plus'). Laisser vide pour utiliser un texte par défaut."
    )
    bouton1_url = models.URLField(
        blank=True,
        help_text="URL du premier bouton. Si vide, le bouton n'apparaîtra pas."
    )
    bouton2_texte = models.CharField(
        max_length=100,
        blank=True,
        help_text="Texte du deuxième bouton (facultatif)."
    )
    bouton2_url = models.URLField(
        blank=True,
        help_text="URL du deuxième bouton (facultatif)."
    )
    bouton3_texte = models.CharField(
        max_length=100,
        blank=True,
        help_text="Texte du troisième bouton (facultatif)."
    )
    bouton3_url = models.URLField(
        blank=True,
        help_text="URL du troisième bouton (facultatif)."
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage (0 = premier, plus grand = plus bas)"
    )
    est_actif = models.BooleanField(
        default=True,
        help_text="Afficher cette image dans le carousel"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Image carousel"
        verbose_name_plural = "Images carousel"
        ordering = ["ordre_affichage", "-date_creation"]
        
    def __str__(self):
        return f"Image carousel - {self.titre or f'Image #{self.pk}'}"


class ConfigurationMairie(models.Model):
    nom_commune = models.CharField(max_length=255, default="Mairie de Kloto 1")
    logo = models.ImageField(upload_to="mairie/logo/", blank=True, null=True, validators=[validate_file_size])
    favicon = models.FileField(upload_to="mairie/favicon/", blank=True, null=True, validators=[validate_file_size])
    est_active = models.BooleanField(default=True)
    
    # Informations de contact
    adresse = models.CharField(
        max_length=255,
        blank=True,
        default="Hôtel de Ville de Kpalimé",
        help_text="Adresse de la mairie (ex: Hôtel de Ville de Kpalimé)"
    )
    telephone = models.CharField(
        max_length=50,
        blank=True,
        default="+228 XX XX XX XX",
        help_text="Numéro de téléphone (ex: +228 XX XX XX XX)"
    )
    whatsapp = models.CharField(
        max_length=50,
        blank=True,
        help_text="Numéro WhatsApp (ex: +228 XX XX XX XX). Format: +228XXXXXXXXX (sans espaces ni tirets)"
    )
    pdc_pdf = models.FileField(
        upload_to="mairie/pdc/",
        blank=True,
        null=True,
        validators=[validate_file_size],
        help_text="Plan de Développement Communal (PDF). Ce fichier sera accessible via un bouton flottant sur le site."
    )
    email = models.EmailField(
        blank=True,
        default="contact@mairiekloto1.tg",
        help_text="Adresse email de contact"
    )
    horaires = models.CharField(
        max_length=255,
        blank=True,
        default="Lundi - Vendredi : 08h00 - 17h00",
        help_text="Horaires d'ouverture (ex: Lundi - Vendredi : 08h00 - 17h00)"
    )
    
    # Réseaux sociaux
    url_facebook = models.URLField(
        blank=True,
        help_text="URL de la page Facebook"
    )
    url_twitter = models.URLField(
        blank=True,
        help_text="URL du compte Twitter/X"
    )
    url_instagram = models.URLField(
        blank=True,
        help_text="URL du compte Instagram"
    )
    url_youtube = models.URLField(
        blank=True,
        help_text="URL de la chaîne YouTube"
    )
    
    # Syntaxes / numéros pour les dons (USSD ou numéros courts, non affichés aux citoyens)
    numero_yas_money = models.CharField(
        max_length=50,
        blank=True,
        help_text="Syntaxe ou code de transfert Mixx by Yas (ex: *145*1*...#). Ce code ne sera pas affiché, uniquement utilisé pour le lien."
    )
    numero_flooz_money = models.CharField(
        max_length=50,
        blank=True,
        help_text="Syntaxe ou code de transfert Flooz Money (ex: *155*1*...#). Ce code ne sera pas affiché, uniquement utilisé pour le lien."
    )
    numero_carte_bancaire = models.CharField(
        max_length=50,
        blank=True,
        help_text="Numéro de compte bancaire pour les dons (affiché publiquement sur le site)"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration de la mairie"
        verbose_name_plural = "Configuration de la mairie"
        ordering = ["-date_modification"]

    def __str__(self):
        return self.nom_commune


class CartographieCommune(models.Model):
    """
    Données de cartographie et de synthèse pour une commune.
    Relié à la configuration active afin d'avoir une seule fiche par commune.
    """

    configuration = models.OneToOneField(
        ConfigurationMairie,
        on_delete=models.CASCADE,
        related_name="cartographie",
        help_text="Configuration associée à cette commune.",
    )

    # Données générales
    superficie_km2 = models.PositiveIntegerField(
        help_text="Superficie totale de la commune en km² (ex: 146)."
    )
    population_totale = models.PositiveIntegerField(
        help_text="Population totale estimée de la commune."
    )
    densite_hab_km2 = models.PositiveIntegerField(
        help_text="Densité moyenne (habitants par km²)."
    )

    # Indicateurs démographiques
    taux_natalite_pour_mille = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Taux de natalité pour 1000 habitants (ex: 32.50).",
    )
    taux_mortalite_pour_mille = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Taux de mortalité pour 1000 habitants (ex: 7.80).",
    )
    taux_croissance_pourcent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Taux annuel moyen de croissance de la population en % (ex: 2.30).",
    )

    # Activités et infrastructures (texte libre, une entrée par ligne)
    principales_activites = models.TextField(
        help_text="Principales activités économiques (une activité par ligne)."
    )
    infrastructures_sante = models.TextField(
        help_text="Liste des infrastructures de santé (une par ligne)."
    )
    infrastructures_education = models.TextField(
        help_text="Liste des infrastructures éducatives (une par ligne)."
    )
    infrastructures_routes = models.TextField(
        help_text="Axes routiers, voiries, pistes (une par ligne)."
    )
    infrastructures_administration = models.TextField(
        help_text="Principales infrastructures administratives et de services publics (une par ligne)."
    )

    # Coordonnées pour la carte
    centre_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Latitude du centre de la commune pour la carte (ex: 6.900000).",
    )
    centre_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Longitude du centre de la commune pour la carte (ex: 0.630000).",
    )
    zoom_carte = models.PositiveIntegerField(
        default=13,
        help_text="Niveau de zoom par défaut de la carte (ex: 13).",
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cartographie de la commune"
        verbose_name_plural = "Cartographie de la commune"
        ordering = ["-date_modification"]

    def __str__(self):
        return f"Cartographie - {self.configuration.nom_commune}"

    @property
    def principales_activites_list(self):
        return [ligne.strip() for ligne in self.principales_activites.splitlines() if ligne.strip()]

    @property
    def infrastructures_sante_list(self):
        return [ligne.strip() for ligne in self.infrastructures_sante.splitlines() if ligne.strip()]

    @property
    def infrastructures_education_list(self):
        return [ligne.strip() for ligne in self.infrastructures_education.splitlines() if ligne.strip()]

    @property
    def infrastructures_routes_list(self):
        return [ligne.strip() for ligne in self.infrastructures_routes.splitlines() if ligne.strip()]

    @property
    def infrastructures_administration_list(self):
        return [ligne.strip() for ligne in self.infrastructures_administration.splitlines() if ligne.strip()]


class InfrastructureCommune(models.Model):
    """
    Point d'infrastructure géolocalisé sur la carte de la commune.
    Permet d'afficher les équipements (santé, éducation, voirie, administrations, etc.).
    """

    TYPE_INFRASTRUCTURE_CHOICES = [
        ("sante", "Infrastructure de santé"),
        ("education", "Infrastructure éducative"),
        ("voirie", "Réseau viaire et voirie"),
        ("administration", "Administration / service public"),
    ]

    cartographie = models.ForeignKey(
        CartographieCommune,
        on_delete=models.CASCADE,
        related_name="infrastructures",
        help_text="Fiche de cartographie à laquelle cette infrastructure est rattachée.",
    )
    type_infrastructure = models.CharField(
        max_length=20,
        choices=TYPE_INFRASTRUCTURE_CHOICES,
        help_text="Catégorie d'infrastructure (santé, éducation, voirie, administration).",
    )
    nom = models.CharField(
        max_length=255,
        help_text="Nom de l'infrastructure (ex: Centre de santé de Kpodzi).",
    )
    description = models.TextField(
        blank=True,
        help_text="Description synthétique de l'infrastructure et de ses services (facultatif).",
    )
    adresse = models.CharField(
        max_length=255,
        blank=True,
        help_text="Adresse ou quartier (facultatif).",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Latitude du point (ex: 6.903421).",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Longitude du point (ex: 0.627845).",
    )
    est_active = models.BooleanField(
        default=True,
        help_text="Afficher cette infrastructure sur la carte publique.",
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Infrastructure de la commune"
        verbose_name_plural = "Infrastructures de la commune"
        ordering = ["cartographie", "type_infrastructure", "nom"]

    def __str__(self):
        return f"{self.nom} ({self.get_type_infrastructure_display()})"


class VisiteSite(models.Model):
    """Enregistre une visite sur le site (à des fins de statistiques)."""
    
    date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True)
    path = models.CharField(max_length=255, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    class Meta:
        verbose_name = "Visite du site"
        verbose_name_plural = "Visites du site"
        ordering = ["-date"]

    def __str__(self):
        return f"Visite le {self.date.strftime('%d/%m/%Y %H:%M')} sur {self.path or '/'}"


class CampagnePublicitaire(models.Model):
    """Campagne de publicité achetée par une entreprise ou institution financière."""

    STATUT_CHOICES = [
        ("demande", "Demande en attente de validation"),
        ("acceptee", "Acceptée par la mairie (en attente de paiement)"),
        ("payee", "Payée (en attente d'activation)"),
        ("active", "Active"),
        ("terminee", "Terminée"),
    ]

    proprietaire = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="campagnes_publicitaires",
        help_text="Utilisateur propriétaire de la campagne (entreprise ou institution financière).",
    )
    titre = models.CharField(max_length=255)
    description = models.TextField(
        blank=True,
        help_text="Objectif de la campagne, produits ou services mis en avant…",
    )
    duree_jours = models.PositiveIntegerField(
        default=30, help_text="Durée standard de diffusion des publicités (en jours)."
    )
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Montant payé pour cette campagne (rempli par la mairie).",
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="demande",
        help_text="Statut de la campagne dans le circuit mairie / paiement.",
    )
    date_demande = models.DateTimeField(
        auto_now_add=True, help_text="Date de création de la demande de campagne."
    )
    date_debut = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date de début effective de diffusion (optionnelle, fixée par la mairie).",
    )
    date_fin = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date de fin effective de diffusion (optionnelle, fixée par la mairie).",
    )

    class Meta:
        verbose_name = "Campagne publicitaire"
        verbose_name_plural = "Campagnes publicitaires"
        ordering = ["-date_demande"]

    def __str__(self) -> str:
        return f"{self.titre} - {self.proprietaire.username}"

    @property
    def est_en_cours(self) -> bool:
        """Retourne True si la campagne est active et dans sa période de diffusion."""
        if self.statut not in ["active", "payee"]:
            return False
        maintenant = timezone.now()
        if self.date_debut and self.date_fin:
            return self.date_debut <= maintenant <= self.date_fin
        return True

    @property
    def peut_creer_publicites(self) -> bool:
        """Autorise la création de publicités une fois la campagne payée ou active."""
        return self.statut in ["payee", "active"]


class Publicite(models.Model):
    """Publicité individuelle affichée sur le site (modale aléatoire)."""

    campagne = models.ForeignKey(
        CampagnePublicitaire,
        on_delete=models.CASCADE,
        related_name="publicites",
        help_text="Campagne à laquelle cette publicité est rattachée.",
    )
    titre = models.CharField(max_length=255)
    texte = models.TextField(
        help_text="Texte du message publicitaire qui sera affiché dans la fenêtre modale."
    )
    image = models.ImageField(
        upload_to="mairie/publicites/",
        blank=True,
        null=True,
        validators=[validate_file_size],
        help_text="Visuel de la publicité (optionnel).",
    )
    url_cible = models.URLField(
        blank=True,
        help_text="Lien vers le site ou la page de l'entreprise (optionnel).",
    )
    est_active = models.BooleanField(
        default=True,
        help_text="Seules les publicités actives peuvent être affichées sur le site.",
    )
    date_debut = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date de début de diffusion de cette publicité (facultatif).",
    )
    date_fin = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date de fin de diffusion de cette publicité (facultatif).",
    )
    ordre_priorite = models.PositiveIntegerField(
        default=0,
        help_text="Permet de donner la priorité à certaines pubs (0 = priorité normale).",
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Publicité"
        verbose_name_plural = "Publicités"
        ordering = ["ordre_priorite", "-date_creation"]

    def __str__(self) -> str:
        return self.titre

    @property
    def est_diffusable(self) -> bool:
        """Retourne True si la publicité est active et dans sa période de diffusion."""
        if not self.est_active:
            return False
        if not self.campagne or not self.campagne.est_en_cours:
            return False
        maintenant = timezone.now()
        if self.date_debut and self.date_fin:
            return self.date_debut <= maintenant <= self.date_fin
        return True


class VideoSpot(models.Model):
    """Courte vidéo ou spot publicitaire mis en avant par la mairie."""

    titre = models.CharField(max_length=255)
    description = models.TextField(
        blank=True,
        help_text="Texte descriptif court de la vidéo ou du spot.",
    )
    fichier_video = models.FileField(
        upload_to="mairie/videos_spots/",
        blank=True,
        null=True,
        validators=[validate_video_size],
        help_text="Fichier vidéo court (ex: spot de 5 minutes, max 25 Mo).",
    )
    vignette = models.ImageField(
        upload_to="mairie/videos_spots/vignettes/",
        blank=True,
        null=True,
        validators=[validate_file_size],
        help_text="Vignette optionnelle pour illustrer la vidéo.",
    )
    url_externe = models.URLField(
        blank=True,
        help_text="Lien pour voir la suite (YouTube, Facebook, etc.).",
    )
    est_active = models.BooleanField(
        default=True,
        help_text="Afficher ce spot vidéo sur les pages d'accueil et d'actualités.",
    )
    date_debut = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date de début de diffusion de ce spot (facultatif).",
    )
    date_fin = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date de fin de diffusion de ce spot (facultatif).",
    )
    ordre_priorite = models.PositiveIntegerField(
        default=0,
        help_text="Permet de donner la priorité à certains spots (0 = priorité normale).",
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Spot vidéo"
        verbose_name_plural = "Spots vidéos"
        ordering = ["ordre_priorite", "-date_creation"]

    def __str__(self) -> str:
        return self.titre

    @property
    def est_diffusable(self) -> bool:
        """Retourne True si le spot est actif et dans sa période de diffusion."""
        if not self.est_active:
            return False
        maintenant = timezone.now()
        if self.date_debut and self.date_fin:
            return self.date_debut <= maintenant <= self.date_fin
        if self.date_debut and not self.date_fin:
            return self.date_debut <= maintenant
        if not self.date_debut and self.date_fin:
            return maintenant <= self.date_fin
        return True


class Projet(models.Model):
    """Projet de la mairie (en cours ou réalisé)."""
    
    STATUT_CHOICES = [
        ("en_cours", "En cours"),
        ("realise", "Réalisé"),
    ]
    
    titre = models.CharField(
        max_length=255,
        help_text="Titre du projet"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="Identifiant technique pour l'URL (ex: rehabilitation-marche-central)"
    )
    description = models.TextField(
        help_text="Description détaillée du projet"
    )
    resume = models.TextField(
        blank=True,
        help_text="Résumé court du projet (affiché dans la liste)"
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="en_cours",
        help_text="Statut du projet"
    )
    
    date_debut = models.DateField(
        help_text="Date de début du projet"
    )
    date_fin = models.DateField(
        blank=True,
        null=True,
        help_text="Date de fin du projet (surtout pour les projets réalisés)"
    )
    
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Budget alloué au projet (en FCFA)"
    )
    
    localisation = models.CharField(
        max_length=255,
        blank=True,
        help_text="Localisation du projet (quartier, secteur, etc.)"
    )
    
    photo_principale = models.ImageField(
        upload_to="mairie/projets/",
        blank=True,
        null=True,
        validators=[validate_file_size],
        help_text="Photo principale du projet"
    )
    
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage (0 = premier, plus grand = plus bas)"
    )
    
    est_visible = models.BooleanField(
        default=True,
        help_text="Afficher ce projet sur le site public"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ["ordre_affichage", "-date_debut", "-date_creation"]
    
    def __str__(self):
        return f"{self.titre} ({self.get_statut_display()})"
    
    def get_resume(self):
        """Retourne le résumé ou un extrait de la description."""
        if self.resume:
            return self.resume
        return self.description[:200] + "..." if len(self.description) > 200 else self.description


class ProjetPhoto(models.Model):
    """Photo supplémentaire pour illustrer un projet (en plus de la photo principale)."""
    
    projet = models.ForeignKey(
        Projet,
        on_delete=models.CASCADE,
        related_name="photos",
        help_text="Projet concerné"
    )
    image = models.ImageField(
        upload_to="mairie/projets/galerie/",
        validators=[validate_file_size],
        help_text="Photo descriptive du projet (max 5 Mo)"
    )
    legende = models.CharField(
        max_length=255,
        blank=True,
        help_text="Légende optionnelle pour décrire la photo"
    )
    ordre = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage (0 = première, 1 = deuxième, etc.)"
    )
    
    class Meta:
        verbose_name = "Photo du projet"
        verbose_name_plural = "Photos du projet"
        ordering = ["ordre", "pk"]
    
    def __str__(self):
        return f"Photo {self.ordre + 1} - {self.projet.titre}"


class Suggestion(models.Model):
    """Suggestion soumise par un visiteur via le formulaire de contact."""
    
    nom = models.CharField(
        max_length=255,
        help_text="Nom du visiteur"
    )
    email = models.EmailField(
        help_text="Adresse email du visiteur"
    )
    telephone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Numéro de téléphone (facultatif)"
    )
    sujet = models.CharField(
        max_length=255,
        help_text="Sujet de la suggestion"
    )
    message = models.TextField(
        help_text="Message détaillé de la suggestion"
    )
    date_soumission = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure de soumission"
    )
    est_lue = models.BooleanField(
        default=False,
        help_text="Marquer comme lue par l'administration"
    )
    date_lecture = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date de lecture par l'administration"
    )
    
    class Meta:
        verbose_name = "Suggestion"
        verbose_name_plural = "Suggestions"
        ordering = ["-date_soumission"]
    
    def __str__(self):
        return f"Suggestion de {self.nom} - {self.sujet} ({self.date_soumission.strftime('%d/%m/%Y')})"


class DonMairie(models.Model):
    """Enregistre un don fait à la mairie."""
    
    TYPE_DON_CHOICES = [
        ("yas_money", "Yas Money"),
        ("flooz_money", "Flooz Money"),
        ("carte_bancaire", "Carte Bancaire"),
    ]
    
    nom_donateur = models.CharField(
        max_length=255,
        help_text="Nom complet du donateur"
    )
    email = models.EmailField(
        help_text="Adresse email du donateur"
    )
    telephone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Numéro de téléphone (facultatif)"
    )
    type_don = models.CharField(
        max_length=20,
        choices=TYPE_DON_CHOICES,
        help_text="Moyen de paiement utilisé pour le don"
    )
    montant = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Montant du don en FCFA"
    )
    message = models.TextField(
        blank=True,
        help_text="Message optionnel du donateur"
    )
    date_don = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure du don"
    )
    est_confirme = models.BooleanField(
        default=False,
        help_text="Marquer comme confirmé après vérification du paiement"
    )
    date_confirmation = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date de confirmation du don"
    )
    notes_admin = models.TextField(
        blank=True,
        help_text="Notes internes de l'administration"
    )
    
    class Meta:
        verbose_name = "Don à la Mairie"
        verbose_name_plural = "Dons à la Mairie"
        ordering = ["-date_don"]
    
    def __str__(self):
        return f"Don de {self.nom_donateur} - {self.montant} FCFA ({self.get_type_don_display()})"


class NewsletterSubscription(models.Model):
    """Inscription à la newsletter de la mairie."""

    email = models.EmailField(
        unique=True,
        help_text="Adresse email de l'abonné à la newsletter.",
    )
    date_inscription = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure d'inscription.",
    )
    est_actif = models.BooleanField(
        default=True,
        help_text="Permet de désactiver un contact sans le supprimer.",
    )
    source = models.CharField(
        max_length=50,
        blank=True,
        help_text="Source d'inscription (ex: popup, formulaire footer...).",
    )

    class Meta:
        verbose_name = "Inscription à la newsletter"
        verbose_name_plural = "Inscriptions à la newsletter"
        ordering = ["-date_inscription"]

    def __str__(self):
        return f"{self.email} ({'actif' if self.est_actif else 'inactif'})"


class Partenaire(models.Model):
    """Partenaire de la mairie affiché dans le footer du site."""

    nom = models.CharField(
        max_length=200,
        help_text="Nom du partenaire",
    )
    logo = models.ImageField(
        upload_to="mairie/partenaires/",
        blank=True,
        null=True,
        validators=[validate_file_size],
        help_text="Logo du partenaire (optionnel)",
    )
    url_site = models.URLField(
        max_length=500,
        blank=True,
        help_text="Lien vers le site du partenaire (optionnel)",
    )
    ordre = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage (plus petit = plus haut)",
    )
    est_actif = models.BooleanField(
        default=True,
        help_text="Afficher ce partenaire dans le footer",
    )

    class Meta:
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"
        ordering = ["ordre", "nom"]

    def __str__(self):
        return self.nom


# --- Contribuables (marchés et places publiques) ---


class AgentCollecteur(models.Model):
    """
    Agent de la mairie chargé de collecter les recettes (cotisations et tickets marché)
    auprès des contribuables sur les marchés et places publiques.
    """
    STATUT_CHOICES = [
        ("actif", "Actif"),
        ("inactif", "Inactif"),
        ("suspendu", "Suspendu"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="agent_collecteur",
        help_text="Compte utilisateur de l'agent (pour connexion et authentification).",
    )
    matricule = models.CharField(
        max_length=50,
        unique=True,
        help_text="Matricule unique de l'agent (ex: AGT-2025-001).",
    )
    nom = models.CharField(max_length=100, help_text="Nom de famille.")
    prenom = models.CharField(max_length=150, help_text="Prénom(s).")
    telephone = models.CharField(
        max_length=30,
        help_text="Numéro de téléphone de l'agent.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Adresse email (si différente de celle du compte utilisateur).",
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="actif",
        help_text="Statut de l'agent.",
    )
    emplacements_assignes = models.ManyToManyField(
        "EmplacementMarche",
        related_name="agents_collecteurs",
        blank=True,
        help_text="Emplacements (marchés/places) assignés à cet agent pour la collecte.",
    )
    date_embauche = models.DateField(
        blank=True,
        null=True,
        help_text="Date d'embauche de l'agent.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Notes administratives sur l'agent (formations, observations, etc.).",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Agent collecteur"
        verbose_name_plural = "Agents collecteurs"
        ordering = ["matricule", "nom", "prenom"]

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"

    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenom}".strip()

    def montant_total_collecte(self, date_debut=None, date_fin=None):
        """
        Retourne le montant total collecté par cet agent (cotisations + tickets).
        Optionnellement filtré par période.
        """
        from django.db.models import Sum
        from django.utils import timezone

        if date_debut is None:
            date_debut = timezone.now().replace(day=1, month=1, hour=0, minute=0, second=0, microsecond=0)
        if date_fin is None:
            date_fin = timezone.now()

        # Cotisations collectées (import différé pour éviter référence circulaire)
        # Utilisation de get_model pour éviter les imports circulaires
        from django.apps import apps
        PaiementCotisation = apps.get_model('mairie', 'PaiementCotisation')
        TicketMarche = apps.get_model('mairie', 'TicketMarche')
        PaiementCotisationActeur = apps.get_model('mairie', 'PaiementCotisationActeur')
        PaiementCotisationInstitution = apps.get_model('mairie', 'PaiementCotisationInstitution')

        cotisations = PaiementCotisation.objects.filter(
            encaisse_par_agent=self,
            date_paiement__gte=date_debut,
            date_paiement__lte=date_fin,
        ).aggregate(total=Sum("montant_paye"))["total"] or 0

        # Tickets marché collectés
        tickets = TicketMarche.objects.filter(
            encaisse_par_agent=self,
            date__gte=date_debut.date() if hasattr(date_debut, "date") else date_debut,
            date__lte=date_fin.date() if hasattr(date_fin, "date") else date_fin,
        ).aggregate(total=Sum("montant"))["total"] or 0

        # Cotisations acteurs économiques collectées
        cotisations_acteurs = PaiementCotisationActeur.objects.filter(
            encaisse_par_agent=self,
            date_paiement__gte=date_debut,
            date_paiement__lte=date_fin,
        ).aggregate(total=Sum("montant_paye"))["total"] or 0

        # Cotisations institutions financières collectées
        cotisations_institutions = PaiementCotisationInstitution.objects.filter(
            encaisse_par_agent=self,
            date_paiement__gte=date_debut,
            date_paiement__lte=date_fin,
        ).aggregate(total=Sum("montant_paye"))["total"] or 0

        return cotisations + tickets + cotisations_acteurs + cotisations_institutions


class EmplacementMarche(models.Model):
    """
    Lieu (marché ou place publique) où se trouvent des boutiques/magasins ou étalages.
    Canton, village, quartier + nom du lieu (ex: Marché central, Place du marché).
    """
    canton = models.CharField(
        max_length=100,
        blank=True,
        help_text="Canton où se situe le marché ou la place.",
    )
    village = models.CharField(
        max_length=150,
        blank=True,
        help_text="Village (si applicable).",
    )
    quartier = models.CharField(
        max_length=150,
        help_text="Quartier ou secteur (ex: Centre-ville, Marché central).",
    )
    nom_lieu = models.CharField(
        max_length=255,
        help_text="Nom du lieu (ex: Marché central de Kpalimé, Place publique X).",
    )
    description = models.TextField(
        blank=True,
        help_text="Description du lieu (accès, horaires du marché, etc.).",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Emplacement (marché / place publique)"
        verbose_name_plural = "Emplacements (marchés / places publiques)"
        ordering = ["canton", "quartier", "nom_lieu"]

    def __str__(self):
        parts = [self.nom_lieu, self.quartier]
        if self.village:
            parts.append(self.village)
        if self.canton:
            parts.append(self.canton)
        return " - ".join(parts)


class Contribuable(models.Model):
    """
    Personne qui occupe un local (boutique/magasin) au marché ou dans une place publique,
    ou qui vend au détail avec un ticket (étalage). Données civiles pour la mairie.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="contribuable",
        help_text="Compte utilisateur pour « Mon compte » (consultation des cotisations).",
    )
    nom = models.CharField(max_length=100, help_text="Nom de famille.")
    prenom = models.CharField(max_length=150, help_text="Prénom(s).")
    telephone = models.CharField(
        max_length=30,
        help_text="Numéro de téléphone du contribuable.",
    )
    date_naissance = models.DateField(
        blank=True,
        null=True,
        help_text="Date de naissance.",
    )
    lieu_naissance = models.CharField(
        max_length=255,
        blank=True,
        help_text="Lieu de naissance.",
    )
    nationalite = models.CharField(
        max_length=100,
        default="Togolaise",
        help_text="Nationalité.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contribuable (marché / place publique)"
        verbose_name_plural = "Contribuables (marchés / places publiques)"
        ordering = ["nom", "prenom"]

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenom}".strip()


class BoutiqueMagasin(models.Model):
    """
    Magasin, boutique, local, terrain, kiosque ou réserve au marché ou dans une place publique.
    Peut être créé sans locataire (non occupé). Une fois occupé, on assigne un contribuable (locataire).
    Le locataire est rattaché à un ou des emplacements, gérés par les agents collecteurs.
    """
    TYPE_LOCAL_CHOICES = [
        ("magasin", "Magasin"),
        ("boutique", "Boutique"),
        ("local", "Local"),
        ("terrain", "Terrain"),
        ("kiosque", "Kiosque"),
        ("reserve", "Réserve"),
    ]

    matricule = models.CharField(
        max_length=50,
        unique=True,
        help_text="Matricule unique du local (ex: MKT-2025-001).",
    )
    emplacement = models.ForeignKey(
        EmplacementMarche,
        on_delete=models.PROTECT,
        related_name="boutiques_magasins",
        help_text="Marché ou place publique où se situe le local.",
    )
    type_local = models.CharField(
        max_length=20,
        choices=TYPE_LOCAL_CHOICES,
        default="boutique",
        help_text="Type de local.",
    )
    superficie_m2 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Superficie en m².",
    )
    prix_location_mensuel = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Prix de location mensuel (FCFA).",
    )
    prix_location_annuel = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Prix de location annuelle (FCFA), si différent de 12 × mensuel.",
    )
    contribuable = models.ForeignKey(
        Contribuable,
        on_delete=models.PROTECT,
        related_name="boutiques_magasins",
        null=True,
        blank=True,
        help_text="Locataire (contribuable) du local. Vide si local non encore loué.",
    )
    activite_vendue = models.CharField(
        max_length=255,
        blank=True,
        help_text="Activité exercée par le locataire (ex: légumes, vêtements). Vide si non occupé.",
    )
    agent_collecteur = models.ForeignKey(
        "AgentCollecteur",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="boutiques_magasins",
        help_text="Agent collecteur assigné à ce local pour la collecte des cotisations.",
    )
    description = models.TextField(
        blank=True,
        help_text="Description complémentaire du local ou de l'activité.",
    )
    est_actif = models.BooleanField(
        default=True,
        help_text="Local actuellement occupé / actif.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Boutique / Magasin (marché)"
        verbose_name_plural = "Boutiques / Magasins (marché)"
        ordering = ["emplacement", "matricule"]

    def __str__(self):
        if self.contribuable_id:
            return f"{self.matricule} - {self.contribuable.nom_complet} ({self.emplacement.nom_lieu})"
        return f"{self.matricule} - Non occupé ({self.emplacement.nom_lieu})"

    def get_prix_annuel(self):
        """Prix annuel effectif (champ ou 12 × mensuel)."""
        if self.prix_location_annuel is not None:
            return self.prix_location_annuel
        return self.prix_location_mensuel * 12


class CotisationAnnuelle(models.Model):
    """
    Une ligne par boutique/magasin par année. Permet de suivre les 12 mois de cotisation
    pour « Mon compte » et pour les agents qui encaissent.
    """
    boutique = models.ForeignKey(
        BoutiqueMagasin,
        on_delete=models.CASCADE,
        related_name="cotisations_annuelles",
        help_text="Boutique ou magasin concerné.",
    )
    annee = models.PositiveIntegerField(
        help_text="Année de cotisation (ex: 2025).",
    )
    montant_annuel_du = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Montant total dû pour l'année (FCFA).",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cotisation annuelle (boutique/magasin)"
        verbose_name_plural = "Cotisations annuelles (boutiques/magasins)"
        ordering = ["-annee", "boutique"]
        unique_together = [["boutique", "annee"]]

    def __str__(self):
        return f"{self.boutique.matricule} - {self.annee}"

    def montant_paye(self):
        """Somme des paiements enregistrés pour cette année."""
        from django.db.models import Sum
        result = self.paiements.aggregate(total=Sum("montant_paye"))
        return result["total"] or 0

    def reste_a_payer(self):
        """Montant restant à payer pour cette année."""
        return max(0, self.montant_annuel_du - self.montant_paye())

    def mois_payes(self):
        """Liste des numéros de mois (1-12) déjà payés."""
        return list(
            self.paiements.values_list("mois", flat=True).order_by("mois")
        )


class PaiementCotisation(models.Model):
    """
    Paiement d'une cotisation mensuelle (ou partiel) par un contribuable.
    Saisi par les agents de la mairie qui collectent les recettes.
    """
    MOIS_CHOICES = [(i, f"Mois {i}") for i in range(1, 13)]

    cotisation_annuelle = models.ForeignKey(
        CotisationAnnuelle,
        on_delete=models.CASCADE,
        related_name="paiements",
        help_text="Cotisation annuelle concernée.",
    )
    mois = models.PositiveSmallIntegerField(
        choices=MOIS_CHOICES,
        help_text="Mois concerné (1-12).",
    )
    montant_paye = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Montant payé (FCFA).",
    )
    date_paiement = models.DateTimeField(
        default=timezone.now,
        help_text="Date et heure du paiement.",
    )
    encaisse_par_agent = models.ForeignKey(
        "AgentCollecteur",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="paiements_cotisations_encaisses",
        help_text="Agent collecteur ayant encaissé ce paiement.",
    )
    encaisse_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="paiements_cotisations_encaisses",
        help_text="[Déprécié] Utiliser encaisse_par_agent. Conservé pour compatibilité.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Notes éventuelles (mode de paiement, reçu, etc.).",
    )

    class Meta:
        verbose_name = "Paiement de cotisation (mois)"
        verbose_name_plural = "Paiements de cotisation (mois)"
        ordering = ["cotisation_annuelle", "mois"]
        unique_together = [["cotisation_annuelle", "mois"]]

    def __str__(self):
        return f"{self.cotisation_annuelle} - Mois {self.mois} ({self.montant_paye} FCFA)"


class TicketMarche(models.Model):
    """
    Ticket vendu au marché pour les petits étalages qui n'ont pas de magasin ni boutique.
    Un ticket par jour de marché, par vendeur (ou par vente si pas de fiche contribuable).
    """
    date = models.DateField(
        help_text="Date du jour de marché.",
    )
    emplacement = models.ForeignKey(
        EmplacementMarche,
        on_delete=models.PROTECT,
        related_name="tickets_marche",
        help_text="Marché où le ticket a été vendu.",
    )
    contribuable = models.ForeignKey(
        Contribuable,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="tickets_marche",
        help_text="Contribuable identifié (si déjà enregistré).",
    )
    nom_vendeur = models.CharField(
        max_length=255,
        help_text="Nom du vendeur (étalage) si différent du contribuable.",
    )
    telephone_vendeur = models.CharField(
        max_length=30,
        blank=True,
        help_text="Téléphone du vendeur.",
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Montant du ticket (FCFA).",
    )
    encaisse_par_agent = models.ForeignKey(
        "AgentCollecteur",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="tickets_marche_encaisses",
        help_text="Agent collecteur ayant vendu ce ticket.",
    )
    encaisse_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="tickets_marche_encaisses",
        help_text="[Déprécié] Utiliser encaisse_par_agent. Conservé pour compatibilité.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Notes éventuelles.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ticket marché (étalage)"
        verbose_name_plural = "Tickets marché (étalages)"
        ordering = ["-date", "-date_creation"]

    def __str__(self):
        return f"Ticket {self.date} - {self.nom_vendeur} ({self.montant} FCFA)"


# ============================================================================
# COTISATIONS ANNUELLES POUR ACTEURS ÉCONOMIQUES ET INSTITUTIONS FINANCIÈRES
# ============================================================================

class CotisationAnnuelleActeur(models.Model):
    """
    Cotisation annuelle (paiement par AN) pour un acteur économique.
    Une ligne par acteur par année.
    """
    acteur = models.ForeignKey(
        "acteurs.ActeurEconomique",
        on_delete=models.CASCADE,
        related_name="cotisations_annuelles",
        help_text="Acteur économique concerné.",
    )
    annee = models.PositiveIntegerField(
        help_text="Année de cotisation (ex: 2025).",
    )
    montant_annuel_du = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Montant total dû pour l'année (FCFA).",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cotisation annuelle (acteur économique)"
        verbose_name_plural = "Cotisations annuelles (acteurs économiques)"
        ordering = ["-annee", "acteur"]
        unique_together = [["acteur", "annee"]]

    def __str__(self):
        return f"{self.acteur.raison_sociale} - {self.annee}"

    def montant_paye(self):
        """Somme des paiements enregistrés pour cette année."""
        from django.db.models import Sum
        result = self.paiements.aggregate(total=Sum("montant_paye"))
        return result["total"] or Decimal("0")

    def reste_a_payer(self):
        """Montant restant à payer pour cette année."""
        return max(Decimal("0"), self.montant_annuel_du - self.montant_paye())


class CotisationAnnuelleInstitution(models.Model):
    """
    Cotisation annuelle (paiement par AN) pour une institution financière.
    Une ligne par institution par année.
    """
    institution = models.ForeignKey(
        "acteurs.InstitutionFinanciere",
        on_delete=models.CASCADE,
        related_name="cotisations_annuelles",
        help_text="Institution financière concernée.",
    )
    annee = models.PositiveIntegerField(
        help_text="Année de cotisation (ex: 2025).",
    )
    montant_annuel_du = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Montant total dû pour l'année (FCFA).",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cotisation annuelle (institution financière)"
        verbose_name_plural = "Cotisations annuelles (institutions financières)"
        ordering = ["-annee", "institution"]
        unique_together = [["institution", "annee"]]

    def __str__(self):
        return f"{self.institution.nom_institution} - {self.annee}"

    def montant_paye(self):
        """Somme des paiements enregistrés pour cette année."""
        from django.db.models import Sum
        result = self.paiements.aggregate(total=Sum("montant_paye"))
        return result["total"] or Decimal("0")

    def reste_a_payer(self):
        """Montant restant à payer pour cette année."""
        return max(Decimal("0"), self.montant_annuel_du - self.montant_paye())


class PaiementCotisationActeur(models.Model):
    """
    Paiement annuel (en une fois) de la cotisation par un acteur économique.
    Saisi par les agents de la mairie qui collectent les recettes.
    """
    cotisation_annuelle = models.ForeignKey(
        CotisationAnnuelleActeur,
        on_delete=models.CASCADE,
        related_name="paiements",
        help_text="Cotisation annuelle concernée.",
    )
    montant_paye = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Montant payé (FCFA).",
    )
    date_paiement = models.DateTimeField(
        default=timezone.now,
        help_text="Date et heure du paiement.",
    )
    encaisse_par_agent = models.ForeignKey(
        AgentCollecteur,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="paiements_cotisations_acteurs_encaisses",
        help_text="Agent collecteur ayant encaissé ce paiement.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Notes éventuelles (mode de paiement, reçu, etc.).",
    )

    class Meta:
        verbose_name = "Paiement de cotisation (acteur économique)"
        verbose_name_plural = "Paiements de cotisation (acteurs économiques)"
        ordering = ["-date_paiement", "cotisation_annuelle"]

    def __str__(self):
        return f"{self.cotisation_annuelle} - {self.montant_paye} FCFA ({self.date_paiement.date()})"


class PaiementCotisationInstitution(models.Model):
    """
    Paiement annuel (en une fois) de la cotisation par une institution financière.
    Saisi par les agents de la mairie qui collectent les recettes.
    """
    cotisation_annuelle = models.ForeignKey(
        CotisationAnnuelleInstitution,
        on_delete=models.CASCADE,
        related_name="paiements",
        help_text="Cotisation annuelle concernée.",
    )
    montant_paye = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Montant payé (FCFA).",
    )
    date_paiement = models.DateTimeField(
        default=timezone.now,
        help_text="Date et heure du paiement.",
    )
    encaisse_par_agent = models.ForeignKey(
        AgentCollecteur,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="paiements_cotisations_institutions_encaisses",
        help_text="Agent collecteur ayant encaissé ce paiement.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Notes éventuelles (mode de paiement, reçu, etc.).",
    )

    class Meta:
        verbose_name = "Paiement de cotisation (institution financière)"
        verbose_name_plural = "Paiements de cotisation (institutions financières)"
        ordering = ["-date_paiement", "cotisation_annuelle"]

    def __str__(self):
        return f"{self.cotisation_annuelle} - {self.montant_paye} FCFA ({self.date_paiement.date()})"