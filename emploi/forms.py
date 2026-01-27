from django import forms
from django.contrib.auth.models import User

from .models import ProfilEmploi


class ProfilJeuneForm(forms.ModelForm):
    """Formulaire d'inscription pour les jeunes en quête d'emploi."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nom d'utilisateur",
        help_text="Choisissez un nom d'utilisateur unique pour votre compte."
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mot de passe",
        help_text="Créez un mot de passe pour accéder à votre espace personnel."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmer le mot de passe"
    )

    class Meta:
        model = ProfilEmploi
        # type_profil est fixé dans la vue
        fields = [
            "nom",
            "prenoms",
            "sexe",
            "date_naissance",
            "nationalite",
            "telephone1",
            "telephone2",
            "email",
            "quartier",
            "canton",
            "adresse_complete",
            "est_resident_kloto",
            "niveau_etude",
            "diplome_principal",
            "situation_actuelle",
            "employeur_actuel",
            "domaine_competence",
            "experiences",
            "disponibilite",
            "type_contrat_souhaite",
            "salaire_souhaite",
            "accepte_rgpd",
            "accepte_contact",
            "service_citoyen_obligatoire",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
            "adresse_complete": forms.Textarea(attrs={"rows": 3}),
            "domaine_competence": forms.Textarea(attrs={"rows": 3}),
            "experiences": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        username = cleaned_data.get("username")

        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "Ce nom d'utilisateur est déjà utilisé.")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            if 'username' in self.fields:
                del self.fields['username']
            if 'password' in self.fields:
                del self.fields['password']
            if 'confirm_password' in self.fields:
                del self.fields['confirm_password']

        # Champs obligatoires côté formulaire pour un jeune
        for name in [
            "nom",
            "prenoms",
            "sexe",
            "date_naissance",
            "telephone1",
            "email",
            "quartier",
            "adresse_complete",
            "domaine_competence",
            "disponibilite",
            "accepte_rgpd",
            "accepte_contact",
            "service_citoyen_obligatoire",
        ]:
            if name in self.fields:
                self.fields[name].required = True

        # Un jeune ne peut pas avoir la situation "retraite"
        situation_field = self.fields.get("situation_actuelle")
        if situation_field is not None:
            situation_field.choices = [
                choice
                for choice in situation_field.choices
                if choice[0] != "retraite"
            ]


class ProfilJeuneEditForm(forms.ModelForm):
    """Formulaire de modification pour les jeunes en quête d'emploi."""

    class Meta:
        model = ProfilEmploi
        # type_profil est fixé dans la vue
        fields = [
            "nom",
            "prenoms",
            "sexe",
            "date_naissance",
            "nationalite",
            "telephone1",
            "telephone2",
            "email",
            "quartier",
            "canton",
            "adresse_complete",
            "est_resident_kloto",
            "niveau_etude",
            "diplome_principal",
            "situation_actuelle",
            "employeur_actuel",
            "domaine_competence",
            "experiences",
            "disponibilite",
            "type_contrat_souhaite",
            "salaire_souhaite",
            "accepte_rgpd",
            "accepte_contact",
            "service_citoyen_obligatoire",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
            "adresse_complete": forms.Textarea(attrs={"rows": 3}),
            "domaine_competence": forms.Textarea(attrs={"rows": 3}),
            "experiences": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Champs obligatoires côté formulaire pour un jeune
        for name in [
            "nom",
            "prenoms",
            "sexe",
            "date_naissance",
            "telephone1",
            "email",
            "quartier",
            "adresse_complete",
            "domaine_competence",
            "disponibilite",
            "accepte_rgpd",
            "accepte_contact",
            "service_citoyen_obligatoire",
        ]:
            if name in self.fields:
                self.fields[name].required = True

        # Un jeune ne peut pas avoir la situation "retraite"
        situation_field = self.fields.get("situation_actuelle")
        if situation_field is not None:
            situation_field.choices = [
                choice
                for choice in situation_field.choices
                if choice[0] != "retraite"
            ]


class ProfilRetraiteForm(forms.ModelForm):
    """Formulaire d'inscription pour les retraités actifs."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nom d'utilisateur",
        help_text="Choisissez un nom d'utilisateur unique pour votre compte."
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mot de passe",
        help_text="Créez un mot de passe pour accéder à votre espace personnel."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmer le mot de passe"
    )

    class Meta:
        model = ProfilEmploi
        fields = [
            "nom",
            "prenoms",
            "sexe",
            "date_naissance",
            "nationalite",
            "telephone1",
            "telephone2",
            "email",
            "quartier",
            "canton",
            "adresse_complete",
            "est_resident_kloto",
            "niveau_etude",
            "diplome_principal",
            "situation_actuelle",
            "employeur_actuel",
            "domaine_competence",
            "experiences",
            "caisse_retraite",
            "dernier_poste",
            "annees_experience",
            "disponibilite",
            "type_contrat_souhaite",
            "salaire_souhaite",
            "accepte_rgpd",
            "accepte_contact",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
            "adresse_complete": forms.Textarea(attrs={"rows": 3}),
            "domaine_competence": forms.Textarea(attrs={"rows": 3}),
            "experiences": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        username = cleaned_data.get("username")

        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "Ce nom d'utilisateur est déjà utilisé.")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            if 'username' in self.fields:
                del self.fields['username']
            if 'password' in self.fields:
                del self.fields['password']
            if 'confirm_password' in self.fields:
                del self.fields['confirm_password']

        # Champs obligatoires côté formulaire pour un retraité
        for name in [
            "nom",
            "prenoms",
            "sexe",
            "date_naissance",
            "telephone1",
            "email",
            "quartier",
            "adresse_complete",
            "domaine_competence",
            "dernier_poste",
            "annees_experience",
            "disponibilite",
            "accepte_rgpd",
            "accepte_contact",
        ]:
            if name in self.fields:
                self.fields[name].required = True

        # Situation fixée à "retraite" pour ce formulaire
        situation_field = self.fields.get("situation_actuelle")
        if situation_field is not None:
            situation_field.choices = [("retraite", "Retraité")]
            situation_field.initial = "retraite"


class ProfilRetraiteEditForm(forms.ModelForm):
    """Formulaire de modification pour les retraités actifs."""

    class Meta:
        model = ProfilEmploi
        fields = [
            "nom",
            "prenoms",
            "sexe",
            "date_naissance",
            "nationalite",
            "telephone1",
            "telephone2",
            "email",
            "quartier",
            "canton",
            "adresse_complete",
            "est_resident_kloto",
            "niveau_etude",
            "diplome_principal",
            "situation_actuelle",
            "employeur_actuel",
            "domaine_competence",
            "experiences",
            "caisse_retraite",
            "dernier_poste",
            "annees_experience",
            "disponibilite",
            "type_contrat_souhaite",
            "salaire_souhaite",
            "accepte_rgpd",
            "accepte_contact",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
            "adresse_complete": forms.Textarea(attrs={"rows": 3}),
            "domaine_competence": forms.Textarea(attrs={"rows": 3}),
            "experiences": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Champs obligatoires côté formulaire pour un retraité
        for name in [
            "nom",
            "prenoms",
            "sexe",
            "date_naissance",
            "telephone1",
            "email",
            "quartier",
            "adresse_complete",
            "domaine_competence",
            "dernier_poste",
            "annees_experience",
            "disponibilite",
            "accepte_rgpd",
            "accepte_contact",
        ]:
            if name in self.fields:
                self.fields[name].required = True

        # Situation fixée à "retraite" pour ce formulaire
        situation_field = self.fields.get("situation_actuelle")
        if situation_field is not None:
            situation_field.choices = [("retraite", "Retraité")]
            situation_field.initial = "retraite"
