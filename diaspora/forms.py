from django import forms
from django.contrib.auth.models import User
from .models import MembreDiaspora


class MembreDiasporaForm(forms.ModelForm):
    """Formulaire d'inscription pour les membres de la diaspora."""

    # Champs pour la création du compte utilisateur
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nom d'utilisateur",
        help_text="Choisissez un nom d'utilisateur unique pour votre compte.",
        required=False  # Sera requis seulement si l'utilisateur n'est pas connecté
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mot de passe",
        help_text="Créez un mot de passe pour accéder à votre espace personnel.",
        required=False  # Sera requis seulement si l'utilisateur n'est pas connecté
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmer le mot de passe",
        required=False  # Sera requis seulement si l'utilisateur n'est pas connecté
    )

    class Meta:
        model = MembreDiaspora
        fields = [
            # A. Informations d'identification
            'nom', 'prenoms', 'sexe', 'date_naissance', 'nationalites',
            'numero_piece_identite', 'pays_residence_actuelle', 'ville_residence_actuelle',
            'adresse_complete_etranger',
            
            # B. Lien avec la commune
            'commune_origine', 'quartier_village_origine', 'nom_parent_tuteur_originaire',
            'annee_depart_pays', 'frequence_retour_pays',
            
            # C. Informations de contact
            'telephone_whatsapp', 'email', 'reseaux_sociaux',
            'contact_au_pays_nom', 'contact_au_pays_telephone',
            
            # D. Situation professionnelle
            'niveau_etudes', 'domaine_formation', 'profession_actuelle',
            'secteur_activite', 'secteur_activite_autre', 'annees_experience',
            
            # E. Statut dans le pays de résidence
            'statut_professionnel', 'type_titre_sejour',
            
            # Comment la diaspora peut aider - A. Appui financier
            'appui_investissement_projets', 'appui_financement_infrastructures',
            'appui_parrainage_communautaire', 'appui_jeunes_femmes_entrepreneurs',
            
            # B. Appui technique & compétences
            'transfert_competences', 'formation_jeunes', 'appui_digitalisation',
            'conseils_techniques', 'encadrement_mentorat',
            
            # C. Création d'emplois
            'creation_entreprise_locale', 'appui_pme_locales', 'recrutement_jeunes_commune',
            
            # D. Partenariats & relations internationales
            'mise_relation_ong', 'cooperation_decentralisee', 'recherche_financements_internationaux',
            'promotion_commune_international',
            
            # E. Engagement citoyen
            'participation_activites_communales', 'participation_reunions_diaspora',
            'appui_actions_sociales_culturelles',
            
            # Questions clés
            'comment_contribuer', 'disposition_participation', 'domaine_intervention_prioritaire',
            
            # Validation
            'accepte_rgpd', 'accepte_contact',
        ]

        widgets = {
            # Dates
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # Zones de texte
            'adresse_complete_etranger': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'comment_contribuer': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'domaine_intervention_prioritaire': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            
            # Champs texte standards
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenoms': forms.TextInput(attrs={'class': 'form-control'}),
            'nationalites': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_piece_identite': forms.TextInput(attrs={'class': 'form-control'}),
            'pays_residence_actuelle': forms.TextInput(attrs={'class': 'form-control'}),
            'ville_residence_actuelle': forms.TextInput(attrs={'class': 'form-control'}),
            'commune_origine': forms.TextInput(attrs={'class': 'form-control'}),
            'quartier_village_origine': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_parent_tuteur_originaire': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone_whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'reseaux_sociaux': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_au_pays_nom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_au_pays_telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'domaine_formation': forms.TextInput(attrs={'class': 'form-control'}),
            'profession_actuelle': forms.TextInput(attrs={'class': 'form-control'}),
            'secteur_activite_autre': forms.TextInput(attrs={'class': 'form-control'}),
            'type_titre_sejour': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Champs numériques
            'annee_depart_pays': forms.NumberInput(attrs={'class': 'form-control', 'min': '1950', 'max': '2026'}),
            'annees_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            
            # Sélecteurs
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'frequence_retour_pays': forms.Select(attrs={'class': 'form-control'}),
            'niveau_etudes': forms.Select(attrs={'class': 'form-control'}),
            'secteur_activite': forms.Select(attrs={'class': 'form-control'}),
            'statut_professionnel': forms.Select(attrs={'class': 'form-control'}),
            'disposition_participation': forms.Select(attrs={'class': 'form-control'}),
            
            # Checkboxes
            'appui_investissement_projets': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appui_financement_infrastructures': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appui_parrainage_communautaire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appui_jeunes_femmes_entrepreneurs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'transfert_competences': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'formation_jeunes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appui_digitalisation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'conseils_techniques': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'encadrement_mentorat': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'creation_entreprise_locale': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appui_pme_locales': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recrutement_jeunes_commune': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mise_relation_ong': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cooperation_decentralisee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recherche_financements_internationaux': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'promotion_commune_international': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'participation_activites_communales': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'participation_reunions_diaspora': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appui_actions_sociales_culturelles': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'accepte_rgpd': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'accepte_contact': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        username = cleaned_data.get("username")

        # Validation des mots de passe seulement si ils sont fournis
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")

        # Validation du nom d'utilisateur seulement s'il est fourni
        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "Ce nom d'utilisateur est déjà utilisé.")

        # Validation du secteur d'activité "autre"
        secteur_activite = cleaned_data.get("secteur_activite")
        secteur_activite_autre = cleaned_data.get("secteur_activite_autre")
        if secteur_activite == "autre" and not secteur_activite_autre:
            self.add_error('secteur_activite_autre', "Veuillez préciser votre secteur d'activité.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Si l'utilisateur est connecté, on n'affiche pas les champs de création de compte
        if self.user and self.user.is_authenticated:
            if 'username' in self.fields:
                del self.fields['username']
            if 'password' in self.fields:
                del self.fields['password']
            if 'confirm_password' in self.fields:
                del self.fields['confirm_password']

        # Champs obligatoires
        required_fields = [
            'nom', 'prenoms', 'sexe', 'date_naissance', 'nationalites',
            'numero_piece_identite', 'pays_residence_actuelle', 'ville_residence_actuelle',
            'adresse_complete_etranger', 'quartier_village_origine', 'nom_parent_tuteur_originaire',
            'annee_depart_pays', 'frequence_retour_pays', 'telephone_whatsapp', 'email',
            'contact_au_pays_nom', 'contact_au_pays_telephone', 'niveau_etudes',
            'domaine_formation', 'profession_actuelle', 'secteur_activite', 'annees_experience',
            'statut_professionnel', 'comment_contribuer', 'disposition_participation',
            'domaine_intervention_prioritaire', 'accepte_rgpd', 'accepte_contact'
        ]

        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True


class MembreDiasporaEditForm(forms.ModelForm):
    """Formulaire de modification pour les membres de la diaspora."""

    class Meta:
        model = MembreDiaspora
        fields = [
            # A. Informations d'identification
            'nom', 'prenoms', 'sexe', 'date_naissance', 'nationalites',
            'numero_piece_identite', 'pays_residence_actuelle', 'ville_residence_actuelle',
            'adresse_complete_etranger',
            
            # B. Lien avec la commune
            'commune_origine', 'quartier_village_origine', 'nom_parent_tuteur_originaire',
            'annee_depart_pays', 'frequence_retour_pays',
            
            # C. Informations de contact
            'telephone_whatsapp', 'email', 'reseaux_sociaux',
            'contact_au_pays_nom', 'contact_au_pays_telephone',
            
            # D. Situation professionnelle
            'niveau_etudes', 'domaine_formation', 'profession_actuelle',
            'secteur_activite', 'secteur_activite_autre', 'annees_experience',
            
            # E. Statut dans le pays de résidence
            'statut_professionnel', 'type_titre_sejour',
            
            # Comment la diaspora peut aider - A. Appui financier
            'appui_investissement_projets', 'appui_financement_infrastructures',
            'appui_parrainage_communautaire', 'appui_jeunes_femmes_entrepreneurs',
            
            # B. Appui technique & compétences
            'transfert_competences', 'formation_jeunes', 'appui_digitalisation',
            'conseils_techniques', 'encadrement_mentorat',
            
            # C. Création d'emplois
            'creation_entreprise_locale', 'appui_pme_locales', 'recrutement_jeunes_commune',
            
            # D. Partenariats & relations internationales
            'mise_relation_ong', 'cooperation_decentralisee', 'recherche_financements_internationaux',
            'promotion_commune_international',
            
            # E. Engagement citoyen
            'participation_activites_communales', 'participation_reunions_diaspora',
            'appui_actions_sociales_culturelles',
            
            # Questions clés
            'comment_contribuer', 'disposition_participation', 'domaine_intervention_prioritaire',
            
            # Validation
            'accepte_rgpd', 'accepte_contact',
        ]

        widgets = {
            # Dates
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # Zones de texte
            'adresse_complete_etranger': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'comment_contribuer': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'domaine_intervention_prioritaire': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            
            # Champs texte standards
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenoms': forms.TextInput(attrs={'class': 'form-control'}),
            'nationalites': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_piece_identite': forms.TextInput(attrs={'class': 'form-control'}),
            'pays_residence_actuelle': forms.TextInput(attrs={'class': 'form-control'}),
            'ville_residence_actuelle': forms.TextInput(attrs={'class': 'form-control'}),
            'commune_origine': forms.TextInput(attrs={'class': 'form-control'}),
            'quartier_village_origine': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_parent_tuteur_originaire': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone_whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'reseaux_sociaux': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_au_pays_nom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_au_pays_telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'domaine_formation': forms.TextInput(attrs={'class': 'form-control'}),
            'profession_actuelle': forms.TextInput(attrs={'class': 'form-control'}),
            'secteur_activite_autre': forms.TextInput(attrs={'class': 'form-control'}),
            'type_titre_sejour': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Champs numériques
            'annee_depart_pays': forms.NumberInput(attrs={'class': 'form-control', 'min': '1950', 'max': '2026'}),
            'annees_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            
            # Sélecteurs
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'frequence_retour_pays': forms.Select(attrs={'class': 'form-control'}),
            'niveau_etudes': forms.Select(attrs={'class': 'form-control'}),
            'secteur_activite': forms.Select(attrs={'class': 'form-control'}),
            'statut_professionnel': forms.Select(attrs={'class': 'form-control'}),
            'disposition_participation': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Champs obligatoires
        required_fields = [
            'nom', 'prenoms', 'sexe', 'date_naissance', 'nationalites',
            'numero_piece_identite', 'pays_residence_actuelle', 'ville_residence_actuelle',
            'adresse_complete_etranger', 'quartier_village_origine', 'nom_parent_tuteur_originaire',
            'annee_depart_pays', 'frequence_retour_pays', 'telephone_whatsapp', 'email',
            'contact_au_pays_nom', 'contact_au_pays_telephone', 'niveau_etudes',
            'domaine_formation', 'profession_actuelle', 'secteur_activite', 'annees_experience',
            'statut_professionnel', 'comment_contribuer', 'disposition_participation',
            'domaine_intervention_prioritaire', 'accepte_rgpd', 'accepte_contact'
        ]

        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True