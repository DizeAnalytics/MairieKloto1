from django.contrib import admin

from .models import ProfilEmploi


@admin.register(ProfilEmploi)
class ProfilEmploiAdmin(admin.ModelAdmin):
    """Administration des profils d'emploi (jeunes et retraités)."""
    
    # Configuration de l'affichage dans l'admin
    list_per_page = 25
    date_hierarchy = 'date_inscription'
    
    list_display = (
        "nom",
        "prenoms",
        "type_profil",
        "sexe",
        "niveau_etude",
        "domaine_competence",
        "quartier",
        "telephone1",
        "email",
        "est_resident_kloto",
        "est_valide_par_mairie",
        "date_inscription",
    )
    
    list_filter = (
        "type_profil",
        "sexe",
        "est_resident_kloto",
        "niveau_etude",
        "situation_actuelle",
        "disponibilite",
        "service_citoyen_obligatoire",
        "est_valide_par_mairie",
        "date_inscription",
    )
    
    search_fields = (
        "nom",
        "prenoms",
        "email",
        "telephone1",
        "telephone2",
        "domaine_competence",
        "quartier",
        "canton",
        "diplome_principal",
    )
    
    readonly_fields = ("date_inscription",)
    
    fieldsets = (
        ("Type de profil", {
            "fields": ("type_profil",)
        }),
        ("Informations personnelles", {
            "fields": (
                "nom",
                "prenoms",
                "sexe",
                "date_naissance",
                "nationalite",
            )
        }),
        ("Contact", {
            "fields": (
                "telephone1",
                "telephone2",
                "email",
            )
        }),
        ("Adresse", {
            "fields": (
                "quartier",
                "canton",
                "adresse_complete",
                "est_resident_kloto",
            )
        }),
        ("Formation et compétences", {
            "fields": (
                "niveau_etude",
                "diplome_principal",
                "domaine_competence",
                "experiences",
            )
        }),
        ("Situation professionnelle", {
            "fields": (
                "situation_actuelle",
                "employeur_actuel",
                "annees_experience",
            )
        }),
        ("Disponibilité et souhaits", {
            "fields": (
                "disponibilite",
                "type_contrat_souhaite",
                "salaire_souhaite",
            )
        }),
        ("Informations retraités", {
            "fields": (
                "caisse_retraite",
                "dernier_poste",
            ),
            "classes": ("collapse",),
        }),
        ("Validation", {
            "fields": (
                "accepte_rgpd",
                "accepte_contact",
                "service_citoyen_obligatoire",
                "est_valide_par_mairie",
                "date_inscription",
            )
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        """Masque les champs spécifiques aux retraités pour les jeunes."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.type_profil == "jeune":
            # Retirer le fieldset des retraités pour les jeunes
            fieldsets = [fs for fs in fieldsets if fs[0] != "Informations retraités"]
        return fieldsets


