from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import (
    MotMaire,
    Collaborateur,
    DirectionMairie,
    SectionDirection,
    PersonnelSection,
    InformationMairie,
    AppelOffre,
    ImageCarousel,
    ConfigurationMairie,
    CartographieCommune,
    InfrastructureCommune,
    CampagnePublicitaire,
    Publicite,
    VideoSpot,
    Projet,
    ProjetPhoto,
    Suggestion,
    DonMairie,
    NewsletterSubscription,
    Partenaire,
    AgentCollecteur,
    EmplacementMarche,
    Contribuable,
    BoutiqueMagasin,
    CotisationAnnuelle,
    PaiementCotisation,
    TicketMarche,
    CotisationAnnuelleActeur,
    CotisationAnnuelleInstitution,
    PaiementCotisationActeur,
    PaiementCotisationInstitution,
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


@admin.register(CartographieCommune)
class CartographieCommuneAdmin(admin.ModelAdmin):
    """Administration des données de cartographie de la commune."""

    list_display = (
        "configuration",
        "population_totale",
        "superficie_km2",
        "densite_hab_km2",
        "taux_croissance_pourcent",
        "date_modification",
    )
    search_fields = ("configuration__nom_commune",)
    readonly_fields = ("date_creation", "date_modification")


@admin.register(InfrastructureCommune)
class InfrastructureCommuneAdmin(admin.ModelAdmin):
    """Administration des infrastructures géolocalisées de la commune."""

    list_display = (
        "nom",
        "type_infrastructure",
        "cartographie",
        "latitude",
        "longitude",
        "est_active",
    )
    list_filter = ("type_infrastructure", "est_active", "cartographie")
    search_fields = ("nom", "description", "adresse")
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


class SectionDirectionInline(admin.TabularInline):
    """Sections rattachées à une direction (niveau intermédiaire de l'organigramme)."""

    model = SectionDirection
    extra = 1
    fields = ("nom", "sigle", "chef_section", "ordre_affichage", "est_active")


@admin.register(DirectionMairie)
class DirectionMairieAdmin(admin.ModelAdmin):
    """Administration des directions de la mairie (organigramme)."""

    list_display = (
        "nom",
        "sigle",
        "chef_direction",
        "ordre_affichage",
        "est_active",
        "date_modification",
    )
    list_filter = ("est_active",)
    search_fields = ("nom", "sigle", "chef_direction")
    inlines = (SectionDirectionInline,)
    readonly_fields = ("date_creation", "date_modification")


class PersonnelSectionInline(admin.TabularInline):
    """Personnel rattaché à une section (niveau détaillé)."""

    model = PersonnelSection
    extra = 1
    fields = ("nom_prenoms", "fonction", "contact", "ordre_affichage", "est_actif")


@admin.register(SectionDirection)
class SectionDirectionAdmin(admin.ModelAdmin):
    """Administration des sections de direction (organigramme)."""

    list_display = (
        "nom",
        "sigle",
        "direction",
        "chef_section",
        "ordre_affichage",
        "est_active",
        "date_modification",
    )
    list_filter = ("direction", "est_active")
    search_fields = ("nom", "sigle", "chef_section", "direction__nom", "direction__sigle")
    inlines = (PersonnelSectionInline,)
    readonly_fields = ("date_creation", "date_modification")


@admin.register(PersonnelSection)
class PersonnelSectionAdmin(admin.ModelAdmin):
    """Administration du personnel des sections (organigramme)."""

    list_display = (
        "nom_prenoms",
        "fonction",
        "section",
        "contact",
        "est_actif",
        "ordre_affichage",
        "date_modification",
    )
    list_filter = ("section", "est_actif")
    search_fields = ("nom_prenoms", "fonction", "section__nom", "section__sigle")
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


@admin.register(VideoSpot)
class VideoSpotAdmin(admin.ModelAdmin):
    """Administration des spots vidéo / courtes vidéos de la mairie."""

    list_display = (
        "titre",
        "est_active",
        "date_debut",
        "date_fin",
        "ordre_priorite",
        "date_creation",
    )
    list_filter = ("est_active", "date_debut", "date_fin")
    search_fields = ("titre", "description")
    fieldsets = (
        (
            "Contenu",
            {
                "fields": (
                    "titre",
                    "description",
                    "fichier_video",
                    "vignette",
                    "url_externe",
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


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    """Administration des abonnés à la newsletter."""

    list_display = ("email", "est_actif", "source", "date_inscription")
    list_filter = ("est_actif", "source", "date_inscription")
    search_fields = ("email", "source")


@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    """Administration des partenaires affichés dans le footer."""

    list_display = ("nom", "logo", "url_site", "ordre", "est_actif")
    list_filter = ("est_actif",)
    search_fields = ("nom",)
    list_editable = ("ordre", "est_actif")


# --- Contribuables (marchés / places publiques) ---


@admin.register(AgentCollecteur)
class AgentCollecteurAdmin(admin.ModelAdmin):
    """Administration des agents collecteurs de taxes."""

    list_display = (
        "matricule",
        "nom_complet",
        "telephone",
        "statut",
        "date_embauche",
        "nombre_emplacements",
    )
    list_filter = ("statut", "date_embauche")
    search_fields = ("matricule", "nom", "prenom", "telephone", "email")
    filter_horizontal = ("emplacements_assignes",)
    fieldsets = (
        (
            "Informations personnelles",
            {
                "fields": (
                    "user",
                    "matricule",
                    "nom",
                    "prenom",
                    "telephone",
                    "email",
                )
            },
        ),
        (
            "Statut et affectation",
            {
                "fields": (
                    "statut",
                    "date_embauche",
                    "emplacements_assignes",
                )
            },
        ),
        ("Notes", {"fields": ("notes",)}),
        (
            "Dates",
            {
                "fields": ("date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("date_creation", "date_modification")

    def nombre_emplacements(self, obj):
        """Affiche le nombre d'emplacements assignés."""
        return obj.emplacements_assignes.count()

    nombre_emplacements.short_description = "Emplacements assignés"


@admin.register(CotisationAnnuelleActeur)
class CotisationAnnuelleActeurAdmin(admin.ModelAdmin):
    """Administration des cotisations annuelles des acteurs économiques."""

    list_display = (
        "acteur",
        "annee",
        "montant_annuel_du",
        "montant_paye_display",
        "reste_a_payer_display",
    )
    list_filter = ("annee",)
    search_fields = ("acteur__raison_sociale", "acteur__sigle")
    readonly_fields = ("date_creation", "date_modification")

    def montant_paye_display(self, obj):
        return f"{obj.montant_paye():,.0f} FCFA"

    montant_paye_display.short_description = "Montant payé"

    def reste_a_payer_display(self, obj):
        reste = obj.reste_a_payer()
        if reste > 0:
            return f"{reste:,.0f} FCFA"
        return "0 FCFA (payé)"

    reste_a_payer_display.short_description = "Reste à payer"


@admin.register(CotisationAnnuelleInstitution)
class CotisationAnnuelleInstitutionAdmin(admin.ModelAdmin):
    """Administration des cotisations annuelles des institutions financières."""

    list_display = (
        "institution",
        "annee",
        "montant_annuel_du",
        "montant_paye_display",
        "reste_a_payer_display",
    )
    list_filter = ("annee",)
    search_fields = ("institution__nom_institution", "institution__sigle")
    readonly_fields = ("date_creation", "date_modification")

    def montant_paye_display(self, obj):
        return f"{obj.montant_paye():,.0f} FCFA"

    montant_paye_display.short_description = "Montant payé"

    def reste_a_payer_display(self, obj):
        reste = obj.reste_a_payer()
        if reste > 0:
            return f"{reste:,.0f} FCFA"
        return "0 FCFA (payé)"

    reste_a_payer_display.short_description = "Reste à payer"


@admin.register(PaiementCotisationActeur)
class PaiementCotisationActeurAdmin(admin.ModelAdmin):
    """Administration des paiements de cotisation des acteurs économiques."""

    list_display = (
        "cotisation_annuelle",
        "montant_paye",
        "date_paiement",
        "encaisse_par_agent",
    )
    list_filter = ("date_paiement", "encaisse_par_agent")
    search_fields = (
        "cotisation_annuelle__acteur__raison_sociale",
        "cotisation_annuelle__acteur__sigle",
    )
    readonly_fields = ("date_paiement",)


@admin.register(PaiementCotisationInstitution)
class PaiementCotisationInstitutionAdmin(admin.ModelAdmin):
    """Administration des paiements de cotisation des institutions financières."""

    list_display = (
        "cotisation_annuelle",
        "montant_paye",
        "date_paiement",
        "encaisse_par_agent",
    )
    list_filter = ("date_paiement", "encaisse_par_agent")
    search_fields = (
        "cotisation_annuelle__institution__nom_institution",
        "cotisation_annuelle__institution__sigle",
    )
    readonly_fields = ("date_paiement",)


@admin.register(EmplacementMarche)
class EmplacementMarcheAdmin(admin.ModelAdmin):
    """Administration des emplacements (marchés, places publiques)."""

    list_display = ("nom_lieu", "quartier", "village", "canton", "date_modification")
    list_filter = ("canton",)
    search_fields = ("nom_lieu", "quartier", "village", "canton")
    fieldsets = (
        ("Localisation", {"fields": ("canton", "village", "quartier", "nom_lieu")}),
        ("Description", {"fields": ("description",)}),
    )
    readonly_fields = ("date_creation", "date_modification")


class BoutiqueMagasinInline(admin.TabularInline):
    """Inline pour afficher et gérer les boutiques d'un contribuable."""
    model = BoutiqueMagasin
    extra = 1
    fields = (
        "matricule",
        "emplacement",
        "type_local",
        "superficie_m2",
        "activite_vendue",
        "prix_location_mensuel",
        "est_actif",
    )
    verbose_name = "Boutique/Magasin"
    verbose_name_plural = "Boutiques/Magasins du contribuable"
    raw_id_fields = ("emplacement",)


@admin.register(Contribuable)
class ContribuableAdmin(admin.ModelAdmin):
    """Administration des contribuables (locataires marché / étalages)."""

    list_display = (
        "nom",
        "prenom",
        "telephone",
        "nationalite",
        "nombre_boutiques",
        "user",
        "date_creation",
    )
    list_filter = ("nationalite",)
    search_fields = ("nom", "prenom", "telephone")
    raw_id_fields = ("user",)
    inlines = (BoutiqueMagasinInline,)
    fieldsets = (
        ("Compte (Mon compte)", {"fields": ("user",)}),
        (
            "État civil",
            {
                "fields": (
                    "nom",
                    "prenom",
                    "telephone",
                    "date_naissance",
                    "lieu_naissance",
                    "nationalite",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": ("date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("date_creation", "date_modification")

    def nombre_boutiques(self, obj):
        """Affiche le nombre de boutiques/magasins du contribuable."""
        count = obj.boutiques_magasins.count()
        if count > 0:
            return f"{count} boutique(s)"
        return "Aucune"
    
    nombre_boutiques.short_description = "Boutiques/Magasins"


class PaiementCotisationInline(admin.TabularInline):
    model = PaiementCotisation
    extra = 0
    max_num = 12
    fields = ("mois", "montant_paye", "date_paiement", "encaisse_par", "notes")
    verbose_name = "Paiement (mois)"
    verbose_name_plural = "Paiements des 12 mois"


@admin.register(CotisationAnnuelle)
class CotisationAnnuelleAdmin(admin.ModelAdmin):
    """Administration des cotisations annuelles (une ligne par boutique par année)."""

    list_display = (
        "boutique",
        "annee",
        "montant_annuel_du",
        "date_creation",
    )
    list_filter = ("annee",)
    search_fields = ("boutique__matricule", "boutique__contribuable__nom")
    inlines = (PaiementCotisationInline,)
    raw_id_fields = ("boutique",)
    readonly_fields = ("date_creation", "date_modification")


@admin.register(BoutiqueMagasin)
class BoutiqueMagasinAdmin(admin.ModelAdmin):
    """Administration des boutiques et magasins au marché."""

    list_display = (
        "matricule",
        "emplacement",
        "contribuable",
        "type_local",
        "activite_vendue",
        "prix_location_mensuel",
        "est_actif",
        "date_modification",
    )
    list_filter = ("type_local", "est_actif", "emplacement")
    search_fields = (
        "matricule",
        "contribuable__nom",
        "contribuable__prenom",
        "activite_vendue",
    )
    raw_id_fields = ("emplacement", "contribuable")
    fieldsets = (
        (
            "Identification",
            {"fields": ("matricule", "emplacement", "type_local", "est_actif")},
        ),
        (
            "Local",
            {
                "fields": (
                    "superficie_m2",
                    "prix_location_mensuel",
                    "prix_location_annuel",
                    "description",
                )
            },
        ),
        (
            "Locataire",
            {"fields": ("contribuable", "activite_vendue")},
        ),
    )
    readonly_fields = ("date_creation", "date_modification")


@admin.register(PaiementCotisation)
class PaiementCotisationAdmin(admin.ModelAdmin):
    """Administration des paiements mensuels de cotisation (agents mairie)."""

    list_display = (
        "cotisation_annuelle",
        "mois",
        "montant_paye",
        "date_paiement",
        "encaisse_par_agent",
        "encaisse_par",
    )
    list_filter = ("mois", "date_paiement", "encaisse_par_agent")
    search_fields = (
        "cotisation_annuelle__boutique__matricule",
        "cotisation_annuelle__boutique__contribuable__nom",
        "encaisse_par_agent__matricule",
        "encaisse_par_agent__nom",
    )
    raw_id_fields = ("cotisation_annuelle", "encaisse_par_agent", "encaisse_par")
    date_hierarchy = "date_paiement"


@admin.register(TicketMarche)
class TicketMarcheAdmin(admin.ModelAdmin):
    """Administration des tickets marché (petits étalages sans boutique)."""

    list_display = (
        "date",
        "emplacement",
        "nom_vendeur",
        "telephone_vendeur",
        "montant",
        "encaisse_par_agent",
        "encaisse_par",
        "date_creation",
    )
    list_filter = ("date", "emplacement", "encaisse_par_agent")
    search_fields = (
        "nom_vendeur",
        "telephone_vendeur",
        "contribuable__nom",
        "contribuable__prenom",
        "encaisse_par_agent__matricule",
        "encaisse_par_agent__nom",
    )
    raw_id_fields = ("emplacement", "contribuable", "encaisse_par_agent", "encaisse_par")
    date_hierarchy = "date"
    readonly_fields = ("date_creation",)
