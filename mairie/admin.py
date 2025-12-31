from django.contrib import admin

from .models import MotMaire, Collaborateur, InformationMairie, AppelOffre


@admin.register(MotMaire)
class MotMaireAdmin(admin.ModelAdmin):
    """Administration du mot du maire."""
    
    list_display = (
        "titre",
        "nom_maire",
        "est_actif",
        "date_creation",
        "date_modification",
    )
    
    list_filter = ("est_actif", "date_creation")
    
    search_fields = ("titre", "nom_maire", "contenu")
    
    fieldsets = (
        ("Contenu", {
            "fields": (
                "titre",
                "contenu",
                "nom_maire",
            )
        }),
        ("Médias", {
            "fields": (
                "photo_maire",
                "signature",
            )
        }),
        ("Affichage", {
            "fields": ("est_actif",)
        }),
    )
    
    readonly_fields = ("date_creation", "date_modification")


@admin.register(AppelOffre)
class AppelOffreAdmin(admin.ModelAdmin):
    """Administration des appels d'offres de la mairie."""

    list_display = (
        "titre",
        "reference",
        "public_cible",
        "statut",
        "date_debut",
        "date_fin",
        "est_publie_sur_site",
        "date_creation",
    )

    list_filter = (
        "public_cible",
        "statut",
        "est_publie_sur_site",
        "date_debut",
        "date_fin",
        "date_creation",
    )

    search_fields = (
        "titre",
        "reference",
        "description",
        "criteres_selection",
    )

    fieldsets = (
        (
            "Informations générales",
            {
                "fields": (
                    "titre",
                    "reference",
                    "description",
                    "public_cible",
                )
            },
        ),
        (
            "Calendrier",
            {
                "fields": (
                    "date_debut",
                    "date_fin",
                )
            },
        ),
        (
            "Aspects financiers",
            {
                "fields": (
                    "budget_estime",
                )
            },
        ),
        (
            "Documents et critères",
            {
                "fields": (
                    "document_officiel",
                    "criteres_selection",
                )
            },
        ),
        (
            "Publication et statut",
            {
                "fields": (
                    "statut",
                    "est_publie_sur_site",
                    "date_creation",
                    "date_modification",
                )
            },
        ),
    )

    readonly_fields = ("date_creation", "date_modification")


@admin.register(Collaborateur)
class CollaborateurAdmin(admin.ModelAdmin):
    """Administration des collaborateurs."""
    
    list_display = (
        "nom",
        "prenoms",
        "fonction",
        "bureau",
        "telephone",
        "email",
        "ordre_affichage",
        "est_visible",
    )
    
    list_filter = (
        "fonction",
        "est_visible",
    )
    
    search_fields = (
        "nom",
        "prenoms",
        "fonction",
        "email",
        "telephone",
    )
    
    fieldsets = (
        ("Informations personnelles", {
            "fields": (
                "nom",
                "prenoms",
                "photo",
            )
        }),
        ("Fonction", {
            "fields": (
                "fonction",
                "fonction_custom",
                "bureau",
                "description",
            )
        }),
        ("Contact", {
            "fields": (
                "telephone",
                "email",
            )
        }),
        ("Affichage", {
            "fields": (
                "ordre_affichage",
                "est_visible",
            )
        }),
    )
    
    readonly_fields = ("date_creation", "date_modification")


@admin.register(InformationMairie)
class InformationMairieAdmin(admin.ModelAdmin):
    """Administration des informations de la mairie."""
    
    list_display = (
        "titre",
        "type_info",
        "icone",
        "ordre_affichage",
        "est_visible",
        "date_modification",
    )
    
    list_filter = (
        "type_info",
        "est_visible",
    )
    
    search_fields = ("titre", "contenu")
    
    fieldsets = (
        ("Contenu", {
            "fields": (
                "type_info",
                "titre",
                "contenu",
                "icone",
            )
        }),
        ("Affichage", {
            "fields": (
                "ordre_affichage",
                "est_visible",
            )
        }),
    )
    
    readonly_fields = ("date_creation", "date_modification")
