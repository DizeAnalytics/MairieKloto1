from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import (
    MotMaire,
    Collaborateur,
    InformationMairie,
    EtatCivilPage,
    AppelOffre,
    ImageCarousel,
    ConfigurationMairie,
)


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


@admin.register(ConfigurationMairie)
class ConfigurationMairieAdmin(admin.ModelAdmin):
    list_display = ("nom_commune", "est_active", "date_modification")
    list_filter = ("est_active",)
    search_fields = ("nom_commune", "email", "telephone")
    fieldsets = (
        ("Identité", {
            "fields": ("nom_commune", "logo", "favicon", "est_active")
        }),
        ("Informations de contact", {
            "fields": ("adresse", "telephone", "email", "horaires"),
            "description": "Ces informations seront affichées dans le footer du site."
        }),
        ("Réseaux sociaux", {
            "fields": ("url_facebook", "url_twitter", "url_instagram", "url_youtube"),
            "description": "URLs des réseaux sociaux. Laissez vide si vous ne souhaitez pas afficher un réseau social."
        }),
        ("Dates", {
            "fields": ("date_creation", "date_modification")
        }),
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


@admin.register(EtatCivilPage)
class EtatCivilPageAdmin(admin.ModelAdmin):
    """Administration des rubriques d'état civil."""

    list_display = (
        "titre",
        "slug",
        "ordre_affichage",
        "est_visible",
        "date_modification",
    )

    list_filter = ("est_visible",)

    search_fields = ("titre", "resume", "contenu")

    prepopulated_fields = {"slug": ("titre",)}

    fieldsets = (
        ("Contenu", {"fields": ("titre", "slug", "resume", "contenu")}),
        ("Affichage", {"fields": ("ordre_affichage", "est_visible")}),
    )

    readonly_fields = ("date_creation", "date_modification")


@admin.register(ImageCarousel)
class ImageCarouselAdmin(admin.ModelAdmin):
    """Administration des images du carousel."""
    
    list_display = (
        "titre",
        "ordre_affichage",
        "est_actif",
        "date_creation",
        "date_modification",
    )
    
    list_filter = ("est_actif", "date_creation")
    
    search_fields = ("titre", "description")
    
    fieldsets = (
        ("Image", {
            "fields": (
                "image",
                "titre",
                "description",
            )
        }),
        ("Affichage", {
            "fields": (
                "ordre_affichage",
                "est_actif",
            )
        }),
    )
    
    readonly_fields = ("date_creation", "date_modification")
    
    def save_model(self, request, obj, form, change):
        """Limiter à 5 images actives maximum."""
        if obj.est_actif:
            # Compter les images actives existantes (exclure l'objet actuel si modification)
            images_actives = ImageCarousel.objects.filter(est_actif=True)
            if change:
                images_actives = images_actives.exclude(pk=obj.pk)
            
            if images_actives.count() >= 5:
                raise ValidationError(
                    "Vous ne pouvez avoir que 5 images actives maximum dans le carousel. "
                    "Désactivez d'abord une image existante."
                )
        super().save_model(request, obj, form, change)
