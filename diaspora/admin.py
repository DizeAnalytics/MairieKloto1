from django.contrib import admin
from .models import MembreDiaspora


@admin.register(MembreDiaspora)
class MembreDiasporaAdmin(admin.ModelAdmin):
    """Administration des membres de la diaspora."""
    
    # Configuration de l'affichage
    list_per_page = 25
    date_hierarchy = 'date_inscription'
    
    list_display = (
        'nom',
        'prenoms',
        'pays_residence_actuelle',
        'ville_residence_actuelle',
        'profession_actuelle',
        'secteur_activite',
        'email',
        'telephone_whatsapp',
        'est_valide_par_mairie',
        'date_inscription',
    )
    
    list_filter = (
        'est_valide_par_mairie',
        'pays_residence_actuelle',
        'secteur_activite',
        'statut_professionnel',
        'niveau_etudes',
        'frequence_retour_pays',
        'disposition_participation',
        'date_inscription',
        # Filtres pour les types d'appui
        'appui_investissement_projets',
        'transfert_competences',
        'creation_entreprise_locale',
        'participation_activites_communales',
    )
    
    search_fields = (
        'nom',
        'prenoms',
        'email',
        'telephone_whatsapp',
        'pays_residence_actuelle',
        'ville_residence_actuelle',
        'profession_actuelle',
        'domaine_formation',
        'quartier_village_origine',
        'nom_parent_tuteur_originaire',
    )
    
    readonly_fields = ('date_inscription', 'date_modification')
    
    fieldsets = (
        ('Informations d\'identification', {
            'fields': (
                'nom', 'prenoms', 'sexe', 'date_naissance', 'nationalites',
                'numero_piece_identite', 'pays_residence_actuelle', 
                'ville_residence_actuelle', 'adresse_complete_etranger'
            )
        }),
        
        ('Lien avec la commune', {
            'fields': (
                'commune_origine', 'quartier_village_origine', 'nom_parent_tuteur_originaire',
                'annee_depart_pays', 'frequence_retour_pays'
            )
        }),
        
        ('Informations de contact', {
            'fields': (
                'telephone_whatsapp', 'email', 'reseaux_sociaux',
                'contact_au_pays_nom', 'contact_au_pays_telephone'
            )
        }),
        
        ('Situation professionnelle', {
            'fields': (
                'niveau_etudes', 'domaine_formation', 'profession_actuelle',
                'secteur_activite', 'secteur_activite_autre', 'annees_experience'
            )
        }),
        
        ('Statut dans le pays de résidence', {
            'fields': (
                'statut_professionnel', 'type_titre_sejour'
            )
        }),
        
        ('Appui financier', {
            'fields': (
                'appui_investissement_projets', 'appui_financement_infrastructures',
                'appui_parrainage_communautaire', 'appui_jeunes_femmes_entrepreneurs'
            ),
            'classes': ('collapse',),
        }),
        
        ('Appui technique & compétences', {
            'fields': (
                'transfert_competences', 'formation_jeunes', 'appui_digitalisation',
                'conseils_techniques', 'encadrement_mentorat'
            ),
            'classes': ('collapse',),
        }),
        
        ('Création d\'emplois', {
            'fields': (
                'creation_entreprise_locale', 'appui_pme_locales', 'recrutement_jeunes_commune'
            ),
            'classes': ('collapse',),
        }),
        
        ('Partenariats & relations internationales', {
            'fields': (
                'mise_relation_ong', 'cooperation_decentralisee',
                'recherche_financements_internationaux', 'promotion_commune_international'
            ),
            'classes': ('collapse',),
        }),
        
        ('Engagement citoyen', {
            'fields': (
                'participation_activites_communales', 'participation_reunions_diaspora',
                'appui_actions_sociales_culturelles'
            ),
            'classes': ('collapse',),
        }),
        
        ('Questions clés', {
            'fields': (
                'comment_contribuer', 'disposition_participation', 'domaine_intervention_prioritaire'
            )
        }),
        
        ('Validation et métadonnées', {
            'fields': (
                'user', 'accepte_rgpd', 'accepte_contact', 'est_valide_par_mairie',
                'date_inscription', 'date_modification'
            )
        }),
    )
    
    # Actions personnalisées
    actions = ['valider_membres', 'invalider_membres']
    
    def valider_membres(self, request, queryset):
        """Action pour valider plusieurs membres à la fois."""
        updated = queryset.update(est_valide_par_mairie=True)
        self.message_user(
            request, 
            f'{updated} membre(s) de la diaspora validé(s) avec succès.'
        )
    valider_membres.short_description = "Valider les membres sélectionnés"
    
    def invalider_membres(self, request, queryset):
        """Action pour invalider plusieurs membres à la fois."""
        updated = queryset.update(est_valide_par_mairie=False)
        self.message_user(
            request, 
            f'{updated} membre(s) de la diaspora invalidé(s) avec succès.'
        )
    invalider_membres.short_description = "Invalider les membres sélectionnés"
    
    # Personnalisation de l'affichage des champs
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Masquer certains champs selon le statut
        if obj and obj.secteur_activite != 'autre':
            if 'secteur_activite_autre' in form.base_fields:
                form.base_fields['secteur_activite_autre'].widget.attrs['readonly'] = True
        
        return form