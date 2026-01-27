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
    CampagnePublicitaire,
    Publicite,
    Projet,
    ProjetPhoto,
    Suggestion,
    DonMairie,
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
    search_fields = ("nom_commune", "email", "telephone", "whatsapp")
    fieldsets = (
        ("Identité", {
            "fields": ("nom_commune", "logo", "favicon", "est_active")
        }),
        ("Informations de contact", {
            "fields": ("adresse", "telephone", "whatsapp", "email", "horaires"),
            "description": "Ces informations seront affichées dans le footer du site. Le numéro WhatsApp sera utilisé pour le bouton flottant de contact."
        }),
        ("Documents", {
            "fields": ("pdc_pdf",),
            "description": "Le Plan de Développement Communal (PDC) sera accessible via un bouton flottant sur le site."
        }),
        ("Réseaux sociaux", {
            "fields": ("url_facebook", "url_twitter", "url_instagram", "url_youtube"),
            "description": "URLs des réseaux sociaux. Laissez vide si vous ne souhaitez pas afficher un réseau social."
        }),
        ("Numéros de compte pour les dons", {
            "fields": ("numero_yas_money", "numero_flooz_money", "numero_carte_bancaire"),
            "description": "Numéros de compte pour recevoir les dons. Ces numéros seront affichés sur la page de contact."
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
    
    class Media:
        js = ('mairie/js/information_mairie_icons.js',)


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
        ("Boutons d'action (max 3)", {
            "fields": (
                "bouton1_texte",
                "bouton1_url",
                "bouton2_texte",
                "bouton2_url",
                "bouton3_texte",
                "bouton3_url",
            ),
            "description": "Vous pouvez définir jusqu'à 3 boutons qui s'afficheront sur cette image du carousel. Un bouton n'est visible que si son URL est renseignée."
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


@admin.register(CampagnePublicitaire)
class CampagnePublicitaireAdmin(admin.ModelAdmin):
    """Administration des campagnes publicitaires achetées par les entreprises / institutions."""

    list_display = (
        "titre",
        "proprietaire",
        "statut",
        "montant",
        "duree_jours",
        "date_demande",
        "date_debut",
        "date_fin",
    )
    list_filter = ("statut", "date_demande", "date_debut", "date_fin")
    search_fields = ("titre", "proprietaire__username", "proprietaire__email")

    fieldsets = (
        (
            "Informations générales",
            {
                "fields": (
                    "proprietaire",
                    "titre",
                    "description",
                )
            },
        ),
        (
            "Paramètres de diffusion",
            {
                "fields": (
                    "duree_jours",
                    "montant",
                    "statut",
                    "date_debut",
                    "date_fin",
                )
            },
        ),
        (
            "Suivi",
            {
                "fields": (
                    "date_demande",
                )
            },
        ),
    )

    readonly_fields = ("date_demande",)


@admin.register(Publicite)
class PubliciteAdmin(admin.ModelAdmin):
    """Administration des publicités affichées sur le site."""

    list_display = (
        "titre",
        "campagne",
        "est_active",
        "ordre_priorite",
        "date_debut",
        "date_fin",
        "date_creation",
    )
    list_filter = ("est_active", "date_debut", "date_fin", "campagne__statut")
    search_fields = ("titre", "campagne__titre", "campagne__proprietaire__username")

    fieldsets = (
        (
            "Contenu",
            {
                "fields": (
                    "campagne",
                    "titre",
                    "texte",
                    "image",
                    "url_cible",
                )
            },
        ),
        (
            "Diffusion",
            {
                "fields": (
                    "est_active",
                    "ordre_priorite",
                    "date_debut",
                    "date_fin",
                )
            },
        ),
        (
            "Suivi",
            {
                "fields": (
                    "date_creation",
                )
            },
        ),
    )

    readonly_fields = ("date_creation",)


class ProjetPhotoInline(admin.TabularInline):
    model = ProjetPhoto
    extra = 3
    fields = ("image", "legende", "ordre")
    verbose_name = "Photo supplémentaire"
    verbose_name_plural = "Photos supplémentaires (3 pour mieux décrire le projet)"


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    """Administration des projets de la mairie."""
    
    inlines = (ProjetPhotoInline,)
    
    list_display = (
        "titre",
        "statut",
        "date_debut",
        "date_fin",
        "budget",
        "localisation",
        "ordre_affichage",
        "est_visible",
        "date_modification",
    )
    
    list_filter = (
        "statut",
        "est_visible",
        "date_debut",
        "date_fin",
    )
    
    search_fields = (
        "titre",
        "description",
        "resume",
        "localisation",
    )
    
    prepopulated_fields = {"slug": ("titre",)}
    
    fieldsets = (
        ("Informations générales", {
            "fields": (
                "titre",
                "slug",
                "statut",
                "description",
                "resume",
            )
        }),
        ("Calendrier", {
            "fields": (
                "date_debut",
                "date_fin",
            )
        }),
        ("Informations complémentaires", {
            "fields": (
                "budget",
                "localisation",
                "photo_principale",
            )
        }),
        ("Affichage", {
            "fields": (
                "ordre_affichage",
                "est_visible",
            )
        }),
        ("Dates", {
            "fields": (
                "date_creation",
                "date_modification",
            )
        }),
    )
    
    readonly_fields = ("date_creation", "date_modification")


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    """Administration des suggestions soumises par les visiteurs."""
    
    list_display = (
        "nom",
        "email",
        "sujet",
        "date_soumission",
        "est_lue",
        "date_lecture",
    )
    
    list_filter = (
        "est_lue",
        "date_soumission",
        "date_lecture",
    )
    
    search_fields = (
        "nom",
        "email",
        "telephone",
        "sujet",
        "message",
    )
    
    readonly_fields = ("date_soumission",)
    
    fieldsets = (
        ("Informations du visiteur", {
            "fields": (
                "nom",
                "email",
                "telephone",
            )
        }),
        ("Contenu de la suggestion", {
            "fields": (
                "sujet",
                "message",
            )
        }),
        ("Suivi", {
            "fields": (
                "est_lue",
                "date_lecture",
                "date_soumission",
            )
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Marquer automatiquement comme lue si l'admin modifie."""
        if change and obj.est_lue and not obj.date_lecture:
            from django.utils import timezone
            obj.date_lecture = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(DonMairie)
class DonMairieAdmin(admin.ModelAdmin):
    """Administration des dons à la mairie."""
    
    list_display = (
        "nom_donateur",
        "email",
        "type_don",
        "montant",
        "date_don",
        "est_confirme",
        "date_confirmation",
    )
    
    list_filter = (
        "type_don",
        "est_confirme",
        "date_don",
        "date_confirmation",
    )
    
    search_fields = (
        "nom_donateur",
        "email",
        "telephone",
        "message",
    )
    
    readonly_fields = ("date_don",)
    
    fieldsets = (
        ("Informations du donateur", {
            "fields": (
                "nom_donateur",
                "email",
                "telephone",
            )
        }),
        ("Détails du don", {
            "fields": (
                "type_don",
                "montant",
                "message",
            )
        }),
        ("Suivi", {
            "fields": (
                "est_confirme",
                "date_confirmation",
                "notes_admin",
                "date_don",
            )
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Marquer automatiquement la date de confirmation si confirmé."""
        if change and obj.est_confirme and not obj.date_confirmation:
            from django.utils import timezone
            obj.date_confirmation = timezone.now()
        super().save_model(request, obj, form, change)
