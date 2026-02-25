from django.contrib import admin

from .models import ActeurEconomique, InstitutionFinanciere, SiteTouristique


@admin.register(ActeurEconomique)
class ActeurEconomiqueAdmin(admin.ModelAdmin):
    """Administration des acteurs économiques."""
    
    list_display = (
        "raison_sociale",
        "type_acteur",
        "secteur_activite",
        "statut_juridique",
        "nom_responsable",
        "telephone1",
        "email",
        "quartier",
        "est_valide_par_mairie",
        "date_enregistrement",
    )
    
    list_filter = (
        "type_acteur",
        "secteur_activite",
        "statut_juridique",
        "est_valide_par_mairie",
        "date_enregistrement",
    )
    
    search_fields = (
        "raison_sociale",
        "nom_responsable",
        "email",
        "telephone1",
        "telephone2",
        "quartier",
        "canton",
        "rccm",
        "cfe",
        "nif",
        "numero_carte_operateur",
    )
    
    readonly_fields = ("date_enregistrement",)
    
    fieldsets = (
        ("Informations générales", {
            "fields": (
                "raison_sociale",
                "type_acteur",
                "secteur_activite",
                "statut_juridique",
                "description",
            )
        }),
        ("Informations légales", {
            "fields": (
                "rccm",
                "cfe",
                "numero_carte_operateur",
                "nif",
                "date_creation",
                "capital_social",
            )
        }),
        ("Responsable", {
            "fields": (
                "nom_responsable",
                "fonction_responsable",
                "telephone1",
                "telephone2",
                "email",
                "site_web",
            )
        }),
        ("Adresse", {
            "fields": (
                "quartier",
                "canton",
                "adresse_complete",
                "latitude",
                "longitude",
            )
        }),
        ("Activité", {
            "fields": (
                "nombre_employes",
                "chiffre_affaires",
            )
        }),
        ("Documents", {
            "fields": (
                "doc_registre",
                "doc_ifu",
                "autres_documents",
            ),
            "classes": ("collapse",),
        }),
        ("Agents collecteurs", {
            "fields": (
                "agents_collecteurs",
            )
        }),
        ("Validation", {
            "fields": (
                "accepte_public",
                "certifie_information",
                "accepte_conditions",
                "est_valide_par_mairie",
                "date_enregistrement",
            )
        }),
    )
    filter_horizontal = ("agents_collecteurs",)


@admin.register(InstitutionFinanciere)
class InstitutionFinanciereAdmin(admin.ModelAdmin):
    """Administration des institutions financières."""
    
    list_display = (
        "nom_institution",
        "sigle",
        "type_institution",
        "nom_responsable",
        "telephone1",
        "email",
        "quartier",
        "nombre_agences",
        "est_valide_par_mairie",
        "date_enregistrement",
    )
    
    list_filter = (
        "type_institution",
        "est_valide_par_mairie",
        "date_enregistrement",
    )
    
    search_fields = (
        "nom_institution",
        "sigle",
        "nom_responsable",
        "email",
        "telephone1",
        "telephone2",
        "whatsapp",
        "quartier",
        "canton",
        "numero_agrement",
        "ifu",
    )
    
    readonly_fields = ("date_enregistrement",)
    
    fieldsets = (
        ("Informations générales", {
            "fields": (
                "type_institution",
                "nom_institution",
                "sigle",
                "annee_creation",
                "description_services",
            )
        }),
        ("Informations légales", {
            "fields": (
                "numero_agrement",
                "ifu",
            )
        }),
        ("Services", {
            "fields": (
                "services",
                "taux_credit",
                "taux_epargne",
            )
        }),
        ("Responsable", {
            "fields": (
                "nom_responsable",
                "fonction_responsable",
                "telephone1",
                "telephone2",
                "whatsapp",
                "email",
                "site_web",
                "facebook",
            )
        }),
        ("Adresse et horaires", {
            "fields": (
                "quartier",
                "canton",
                "adresse_complete",
                "latitude",
                "longitude",
                "nombre_agences",
                "horaires",
            )
        }),
        ("Documents", {
            "fields": (
                "doc_agrement",
                "logo",
                "brochure",
            ),
            "classes": ("collapse",),
        }),
        ("Informations complémentaires", {
            "fields": (
                "conditions_eligibilite",
                "public_cible",
            ),
            "classes": ("collapse",),
        }),
        ("Agents collecteurs", {
            "fields": (
                "agents_collecteurs",
            )
        }),
        ("Validation", {
            "fields": (
                "certifie_info",
                "accepte_public",
                "accepte_contact",
                "engagement",
                "est_valide_par_mairie",
                "date_enregistrement",
            )
        }),
    )
    filter_horizontal = ("agents_collecteurs",)
    
    def get_services_display(self, obj):
        """Affiche les services de manière lisible."""
        if obj.services:
            services_list = obj.services.split(",")
            # Vous pouvez créer un mapping des services si nécessaire
            return ", ".join(services_list)
        return "-"
    
    get_services_display.short_description = "Services"


@admin.register(SiteTouristique)
class SiteTouristiqueAdmin(admin.ModelAdmin):
    list_display = (
        "nom_site",
        "categorie_site",
        "prix_visite",
        "quartier",
        "est_valide_par_mairie",
        "date_enregistrement",
    )
    list_filter = (
        "categorie_site",
        "quartier",
        "est_valide_par_mairie",
        "date_enregistrement",
    )
    search_fields = (
        "nom_site",
        "quartier",
        "canton",
        "coordonnees_gps",
    )
    readonly_fields = ("date_enregistrement",)
    fieldsets = (
        ("Informations générales", {
            "fields": (
                "nom_site",
                "categorie_site",
                "description",
                "particularite",
            )
        }),
        ("Visite", {
            "fields": (
                "prix_visite",
                "horaires_visite",
                "jours_ouverture",
            )
        }),
        ("Localisation", {
            "fields": (
                "quartier",
                "canton",
                "adresse_complete",
                "coordonnees_gps",
            )
        }),
        ("Options", {
            "fields": (
                "guide_disponible",
                "parking_disponible",
                "restauration_disponible",
                "acces_handicapes",
            )
        }),
        ("Contact et média", {
            "fields": (
                "telephone_contact",
                "email_contact",
                "site_web",
                "photo_principale",
            )
        }),
        ("Accès et validation", {
            "fields": (
                "conditions_acces",
                "est_valide_par_mairie",
                "date_enregistrement",
            )
        }),
    )
