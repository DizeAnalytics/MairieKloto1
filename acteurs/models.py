from django.db import models
from django.contrib.auth.models import User


class ActeurEconomique(models.Model):
    """Représente une entreprise / acteur économique dans la commune."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='acteur_economique')

    TYPE_ACTEUR_CHOICES = [
        ("entreprise", "Entreprise"),
        ("commerce", "Commerce"),
        ("artisan", "Artisan"),
        ("pme", "PME"),
        ("pmi", "PMI"),
        ("ong", "ONG"),
        ("association", "Association"),
        ("autre", "Autre"),
    ]

    SECTEUR_ACTIVITE_CHOICES = [
        ("commerce", "Commerce général"),
        ("artisanat", "Artisanat"),
        ("service", "Services"),
        ("industrie", "Industrie"),
        ("agriculture", "Agriculture"),
        ("batiment", "Bâtiment et Travaux Publics"),
        ("transport", "Transport"),
        ("technologie", "Technologie et Informatique"),
        ("sante", "Santé"),
        ("education", "Éducation et Formation"),
        ("hotellerie", "Hôtellerie et Restauration"),
        ("finance", "Finance et Assurance"),
        ("bar", "Bar"),
        ("restaurant", "Restaurant"),
        ("auberge", "Auberge"),
        ("traiteur", "Service Traiteur"),
        ("pharmacie", "Pharmacie"),
        ("depot_pharmacie", "Dépôt de Pharmacie"),
        ("ecole_publique", "Écoles Publiques"),
        ("ecole_privee", "Écoles Privées"),
        ("supermarche", "Supermarché"),
        ("boutique", "Boutique"),
        ("alimentation", "Alimentation générale"),
        ("pret_a_porter", "Prêt-à-porter"),
        ("quincaillerie", "Quincaillerie"),
        ("tourisme", "Tourisme"),
        ("autre", "Autre"),
    ]

    STATUT_JURIDIQUE_CHOICES = [
        ("sarl", "SARL - Société à Responsabilité Limitée"),
        ("sa", "SA - Société Anonyme"),
        ("ei", "EI - Entreprise Individuelle"),
        ("snc", "SNC - Société en Nom Collectif"),
        ("association", "Association"),
        ("ong", "ONG"),
        ("cooperative", "Coopérative"),
        ("autre", "Autre"),
    ]

    NB_EMPLOYES_CHOICES = [
        ("1-5", "1 à 5"),
        ("6-10", "6 à 10"),
        ("11-50", "11 à 50"),
        ("51-100", "51 à 100"),
        ("100+", "Plus de 100"),
    ]

    CA_CHOICES = [
        ("0-5M", "Moins de 5 millions"),
        ("5M-20M", "5 à 20 millions"),
        ("20M-50M", "20 à 50 millions"),
        ("50M-100M", "50 à 100 millions"),
        ("100M+", "Plus de 100 millions"),
    ]

    SITUATION_CHOICES = [
        ("dans_commune", "Dans la commune"),
        ("hors_commune", "Hors commune"),
    ]

    raison_sociale = models.CharField(max_length=255)
    sigle = models.CharField(max_length=50, blank=True)
    type_acteur = models.CharField(max_length=20, choices=TYPE_ACTEUR_CHOICES)
    secteur_activite = models.CharField(max_length=30, choices=SECTEUR_ACTIVITE_CHOICES)
    statut_juridique = models.CharField(max_length=20, choices=STATUT_JURIDIQUE_CHOICES)
    description = models.TextField()

    rccm = models.CharField(max_length=100, blank=True)
    cfe = models.CharField(max_length=100, blank=True)
    numero_carte_operateur = models.CharField(max_length=100, blank=True)
    nif = models.CharField(max_length=100, blank=True)
    date_creation = models.DateField(blank=True, null=True)
    capital_social = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )

    nom_responsable = models.CharField(max_length=255)
    fonction_responsable = models.CharField(max_length=255)
    telephone1 = models.CharField(max_length=30)
    telephone2 = models.CharField(max_length=30, blank=True)
    email = models.EmailField()
    site_web = models.URLField(blank=True)

    quartier = models.CharField(max_length=255)
    canton = models.CharField(max_length=100, blank=True)
    adresse_complete = models.TextField()
    situation = models.CharField(
        max_length=20, choices=SITUATION_CHOICES, default="dans_commune"
    )

    # Géolocalisation (obligatoire à l'enregistrement pour la carte du tableau de bord)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Latitude GPS (ex: 6.9057 pour Kpalimé)"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Longitude GPS (ex: 0.6287 pour Kpalimé)"
    )

    nombre_employes = models.CharField(
        max_length=20, choices=NB_EMPLOYES_CHOICES, blank=True
    )
    chiffre_affaires = models.CharField(
        max_length=20, choices=CA_CHOICES, blank=True
    )

    doc_registre = models.FileField(upload_to="documents/registre/", blank=True)
    doc_ifu = models.FileField(upload_to="documents/ifu/", blank=True)
    autres_documents = models.FileField(
        upload_to="documents/autres/", blank=True, null=True
    )

    accepte_public = models.BooleanField(default=False)
    certifie_information = models.BooleanField(default=False)
    accepte_conditions = models.BooleanField(default=False)

    est_valide_par_mairie = models.BooleanField(default=False)
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    # Agents collecteurs assignés pour la collecte des cotisations
    agents_collecteurs = models.ManyToManyField(
        "mairie.AgentCollecteur",
        related_name="acteurs_economiques",
        blank=True,
        help_text="Agents collecteurs assignés pour la collecte des cotisations de cet acteur.",
    )

    class Meta:
        ordering = ["-date_enregistrement"]
        verbose_name = "Acteur économique"
        verbose_name_plural = "Acteurs économiques"

    def __str__(self) -> str:
        return self.raison_sociale


class InstitutionFinanciere(models.Model):
    """Représente une institution financière (banque, IMF, etc.) partenaire de la commune."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='institution_financiere')

    TYPE_INSTITUTION_CHOICES = [
        ("banque", "Banque commerciale"),
        ("microfinance", "Institution de microfinance (IMF)"),
        ("bailleur", "Bailleur de fonds"),
        ("ong", "ONG de financement"),
        ("association", "Association"),
        ("fondation", "Fondation"),
        ("cooperative", "Coopérative d'épargne et de crédit"),
        ("assurance", "Compagnie d'assurance"),
        ("investissement", "Société d'investissement"),
        ("autre", "Autre"),
    ]
    SITUATION_CHOICES = ActeurEconomique.SITUATION_CHOICES

    type_institution = models.CharField(max_length=30, choices=TYPE_INSTITUTION_CHOICES)
    nom_institution = models.CharField(max_length=255)
    sigle = models.CharField(max_length=50, blank=True)
    annee_creation = models.PositiveIntegerField(blank=True, null=True)
    numero_agrement = models.CharField(max_length=100, blank=True)
    ifu = models.CharField(max_length=100, blank=True)

    description_services = models.TextField()
    # Services sélectionnés (valeurs techniques des cases à cocher, séparées par des virgules)
    services = models.CharField(max_length=255, blank=True)
    taux_credit = models.CharField(max_length=50, blank=True)
    taux_epargne = models.CharField(max_length=50, blank=True)

    nom_responsable = models.CharField(max_length=255)
    fonction_responsable = models.CharField(max_length=255)
    telephone1 = models.CharField(max_length=30)
    telephone2 = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    email = models.EmailField()
    site_web = models.URLField(blank=True)
    facebook = models.URLField(blank=True)

    quartier = models.CharField(max_length=255)
    canton = models.CharField(max_length=100, blank=True)
    adresse_complete = models.TextField()
    situation = models.CharField(
        max_length=20, choices=SITUATION_CHOICES, default="dans_commune"
    )

    # Géolocalisation (obligatoire à l'inscription pour la carte du tableau de bord)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Latitude GPS (ex: 6.9057 pour Kpalimé)"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Longitude GPS (ex: 0.6287 pour Kpalimé)"
    )

    nombre_agences = models.PositiveIntegerField(blank=True, null=True)
    horaires = models.CharField(max_length=255)

    doc_agrement = models.FileField(upload_to="institutions/agrements/", blank=True)
    logo = models.FileField(upload_to="institutions/logos/", blank=True)
    brochure = models.FileField(upload_to="institutions/brochures/", blank=True)

    conditions_eligibilite = models.TextField(blank=True)
    public_cible = models.TextField(blank=True)

    certifie_info = models.BooleanField(default=False)
    accepte_public = models.BooleanField(default=False)
    accepte_contact = models.BooleanField(default=False)
    engagement = models.BooleanField(default=False)

    est_valide_par_mairie = models.BooleanField(default=False)
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    # Agents collecteurs assignés pour la collecte des cotisations
    agents_collecteurs = models.ManyToManyField(
        "mairie.AgentCollecteur",
        related_name="institutions_financieres",
        blank=True,
        help_text="Agents collecteurs assignés pour la collecte des cotisations de cette institution.",
    )

    class Meta:
        ordering = ["-date_enregistrement"]
        verbose_name = "Institution financière"
        verbose_name_plural = "Institutions financières"

    def __str__(self) -> str:
        return self.nom_institution


class SiteTouristique(models.Model):
    """Représente un site touristique de la commune."""

    CATEGORIE_SITE_CHOICES = [
        ("cascade", "Cascade"),
        ("montagne", "Montagne"),
        ("foret", "Forêt"),
        ("plage", "Plage"),
        ("parc", "Parc"),
        ("monument", "Monument"),
        ("musee", "Musée"),
        ("site_culturel", "Site culturel"),
        ("site_historique", "Site historique"),
        ("autre", "Autre"),
    ]

    nom_site = models.CharField(max_length=255)
    categorie_site = models.CharField(max_length=30, choices=CATEGORIE_SITE_CHOICES)
    description = models.TextField()
    particularite = models.TextField(blank=True)

    prix_visite = models.DecimalField(max_digits=10, decimal_places=2)
    horaires_visite = models.CharField(max_length=255)
    jours_ouverture = models.CharField(max_length=255, blank=True)

    quartier = models.CharField(max_length=255)
    canton = models.CharField(max_length=100, blank=True)
    adresse_complete = models.TextField()
    coordonnees_gps = models.CharField(max_length=100, blank=True)

    guide_disponible = models.BooleanField(default=False)
    parking_disponible = models.BooleanField(default=False)
    restauration_disponible = models.BooleanField(default=False)
    acces_handicapes = models.BooleanField(default=False)

    telephone_contact = models.CharField(max_length=30, blank=True)
    email_contact = models.EmailField(blank=True)
    site_web = models.URLField(blank=True)

    photo_principale = models.FileField(upload_to="sites/photos/", blank=True)

    conditions_acces = models.TextField(blank=True)

    est_valide_par_mairie = models.BooleanField(default=False)
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_enregistrement"]
        verbose_name = "Site touristique"
        verbose_name_plural = "Sites touristiques"

    def __str__(self) -> str:
        return self.nom_site
