from django import forms
from django.contrib.auth.models import User

from .models import ActeurEconomique, InstitutionFinanciere, SiteTouristique


class ActeurEconomiqueForm(forms.ModelForm):
    """Formulaire d’enregistrement des acteurs économiques."""

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
        model = ActeurEconomique
        fields = [
            "raison_sociale",
            "sigle",
            "type_acteur",
            "secteur_activite",
            "statut_juridique",
            "description",
            "rccm",
            "cfe",
            "numero_carte_operateur",
            "nif",
            "date_creation",
            "capital_social",
            "nom_responsable",
            "fonction_responsable",
            "telephone1",
            "telephone2",
            "email",
            "site_web",
            "quartier",
            "canton",
            "adresse_complete",
            "situation",
            "latitude",
            "longitude",
            "nombre_employes",
            "chiffre_affaires",
            "doc_registre",
            "doc_ifu",
            "autres_documents",
            "certifie_information",
            "accepte_conditions",
            "accepte_public",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "adresse_complete": forms.Textarea(attrs={"rows": 3}),
            "date_creation": forms.DateInput(attrs={"type": "date"}),
            "latitude": forms.NumberInput(attrs={"step": "any", "placeholder": "ex: 6.9057"}),
            "longitude": forms.NumberInput(attrs={"step": "any", "placeholder": "ex: 0.6287"}),
        }
        
        labels = {
            "cfe": "N° CFE",
            "numero_carte_operateur": "N° Carte d'Opérateur économique",
            "nif": "NIF",
            "latitude": "Latitude (GPS)",
            "longitude": "Longitude (GPS)",
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        username = cleaned_data.get("username")
        situation = cleaned_data.get("situation")
        quartier = cleaned_data.get("quartier")
        situation = cleaned_data.get("situation")
        quartier = cleaned_data.get("quartier")

        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "Ce nom d'utilisateur est déjà utilisé.")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")

        if situation == "dans_commune" and not quartier:
            self.add_error("quartier", "Veuillez renseigner le quartier pour une entreprise dans la commune.")
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields["quartier"].required = False
        self.fields["latitude"].required = True
        self.fields["longitude"].required = True
        if self.user and self.user.is_authenticated:
            if 'username' in self.fields:
                del self.fields['username']
            if 'password' in self.fields:
                del self.fields['password']
            if 'confirm_password' in self.fields:
                del self.fields['confirm_password']


class ActeurEconomiqueEditForm(forms.ModelForm):
    """Formulaire de modification des acteurs économiques."""

    class Meta:
        model = ActeurEconomique
        fields = [
            "raison_sociale",
            "sigle",
            "type_acteur",
            "secteur_activite",
            "statut_juridique",
            "description",
            "rccm",
            "cfe",
            "numero_carte_operateur",
            "nif",
            "date_creation",
            "capital_social",
            "nom_responsable",
            "fonction_responsable",
            "telephone1",
            "telephone2",
            "email",
            "site_web",
            "quartier",
            "canton",
            "adresse_complete",
            "situation",
            "latitude",
            "longitude",
            "nombre_employes",
            "chiffre_affaires",
            "doc_registre",
            "doc_ifu",
            "autres_documents",
            "certifie_information",
            "accepte_conditions",
            "accepte_public",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "adresse_complete": forms.Textarea(attrs={"rows": 3}),
            "date_creation": forms.DateInput(attrs={"type": "date"}),
            "latitude": forms.NumberInput(attrs={"step": "any", "placeholder": "ex: 6.9057"}),
            "longitude": forms.NumberInput(attrs={"step": "any", "placeholder": "ex: 0.6287"}),
        }
        
        labels = {
            "cfe": "N° CFE",
            "numero_carte_operateur": "N° Carte d'Opérateur économique",
            "nif": "NIF",
            "latitude": "Latitude (GPS)",
            "longitude": "Longitude (GPS)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["quartier"].required = False
        self.fields["latitude"].required = True
        self.fields["longitude"].required = True

    def clean(self):
        cleaned_data = super().clean()
        situation = cleaned_data.get("situation")
        quartier = cleaned_data.get("quartier")

        if situation == "dans_commune" and not quartier:
            self.add_error("quartier", "Veuillez renseigner le quartier pour une entreprise dans la commune.")

        return cleaned_data


class InstitutionFinanciereForm(forms.ModelForm):
    """Formulaire d’enregistrement des institutions financières."""

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

    SERVICES_CHOICES = [
        ("comptes", "Comptes bancaires"),
        ("epargne", "Épargne"),
        ("credits", "Crédits / Prêts"),
        ("microCredits", "Micro-crédits"),
        ("transfert", "Transfert d'argent"),
        ("mobile", "Mobile Banking"),
        ("pme", "Financement PME"),
        ("agricole", "Crédit agricole"),
        ("assurance", "Assurance"),
        ("change", "Change de devises"),
        ("conseil", "Conseil financier"),
        ("investissement", "Investissement"),
    ]

    services = forms.MultipleChoiceField(
        choices=SERVICES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Services disponibles",
    )

    class Meta:
        model = InstitutionFinanciere
        fields = [
            "type_institution",
            "nom_institution",
            "sigle",
            "annee_creation",
            "numero_agrement",
            "ifu",
            "description_services",
            "services",
            "taux_credit",
            "taux_epargne",
            "nom_responsable",
            "fonction_responsable",
            "telephone1",
            "telephone2",
            "whatsapp",
            "email",
            "site_web",
            "facebook",
            "quartier",
            "canton",
            "adresse_complete",
            "situation",
            "latitude",
            "longitude",
            "nombre_agences",
            "horaires",
            "doc_agrement",
            "logo",
            "brochure",
            "conditions_eligibilite",
            "public_cible",
            "certifie_info",
            "accepte_public",
            "accepte_contact",
            "engagement",
        ]

        widgets = {
            "description_services": forms.Textarea(attrs={"rows": 4}),
            "adresse_complete": forms.Textarea(attrs={"rows": 3}),
            "conditions_eligibilite": forms.Textarea(attrs={"rows": 3}),
            "public_cible": forms.Textarea(attrs={"rows": 3}),
            "latitude": forms.NumberInput(attrs={"step": "any", "placeholder": "ex: 6.9057"}),
            "longitude": forms.NumberInput(attrs={"step": "any", "placeholder": "ex: 0.6287"}),
        }

    def clean_services(self):
        """Transformer la liste de services en chaîne stockée dans le modèle."""
        values = self.cleaned_data.get("services", [])
        return ",".join(values)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        username = cleaned_data.get("username")
        situation = cleaned_data.get("situation")
        quartier = cleaned_data.get("quartier")

        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "Ce nom d'utilisateur est déjà utilisé.")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")

        if situation == "dans_commune" and not quartier:
            self.add_error("quartier", "Veuillez renseigner le quartier pour une institution située dans la commune.")
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields["quartier"].required = False
        self.fields["latitude"].required = True
        self.fields["longitude"].required = True
        if self.user and self.user.is_authenticated:
            if 'username' in self.fields:
                del self.fields['username']
            if 'password' in self.fields:
                del self.fields['password']
            if 'confirm_password' in self.fields:
                del self.fields['confirm_password']


class InstitutionFinanciereEditForm(forms.ModelForm):
    """Formulaire de modification des institutions financières."""

    SERVICES_CHOICES = [
        ("comptes", "Comptes bancaires"),
        ("epargne", "Épargne"),
        ("credits", "Crédits / Prêts"),
        ("microCredits", "Micro-crédits"),
        ("transfert", "Transfert d'argent"),
        ("mobile", "Mobile Banking"),
        ("pme", "Financement PME"),
        ("agricole", "Crédit agricole"),
        ("assurance", "Assurance"),
        ("change", "Change de devises"),
        ("conseil", "Conseil financier"),
        ("investissement", "Investissement"),
    ]

    services = forms.MultipleChoiceField(
        choices=SERVICES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Services disponibles",
    )

    class Meta:
        model = InstitutionFinanciere
        fields = [
            "type_institution",
            "nom_institution",
            "sigle",
            "annee_creation",
            "numero_agrement",
            "ifu",
            "description_services",
            "services",
            "taux_credit",
            "taux_epargne",
            "nom_responsable",
            "fonction_responsable",
            "telephone1",
            "telephone2",
            "whatsapp",
            "email",
            "site_web",
            "facebook",
            "quartier",
            "canton",
            "adresse_complete",
            "situation",
            "latitude",
            "longitude",
            "nombre_agences",
            "horaires",
            "doc_agrement",
            "logo",
            "brochure",
            "conditions_eligibilite",
            "public_cible",
            "certifie_info",
            "accepte_public",
            "accepte_contact",
            "engagement",
        ]

        widgets = {
            "description_services": forms.Textarea(attrs={"rows": 4}),
            "adresse_complete": forms.Textarea(attrs={"rows": 3}),
            "conditions_eligibilite": forms.Textarea(attrs={"rows": 3}),
            "public_cible": forms.Textarea(attrs={"rows": 3}),
            "latitude": forms.NumberInput(attrs={"step": "any", "placeholder": "ex: 6.9057"}),
            "longitude": forms.NumberInput(attrs={"step": "any", "placeholder": "ex: 0.6287"}),
        }

    def clean_services(self):
        """Transformer la liste de services en chaîne stockée dans le modèle."""
        values = self.cleaned_data.get("services", [])
        return ",".join(values)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["quartier"].required = False
        self.fields["latitude"].required = True
        self.fields["longitude"].required = True
        if self.instance and self.instance.pk and self.instance.services:
            self.initial['services'] = self.instance.services.split(',')

    def clean(self):
        cleaned_data = super().clean()
        situation = cleaned_data.get("situation")
        quartier = cleaned_data.get("quartier")

        if situation == "dans_commune" and not quartier:
            self.add_error("quartier", "Veuillez renseigner le quartier pour une institution située dans la commune.")

        return cleaned_data


class SiteTouristiqueForm(forms.ModelForm):
    class Meta:
        model = SiteTouristique
        fields = [
            "nom_site",
            "categorie_site",
            "description",
            "particularite",
            "prix_visite",
            "horaires_visite",
            "jours_ouverture",
            "quartier",
            "canton",
            "adresse_complete",
            "coordonnees_gps",
            "guide_disponible",
            "parking_disponible",
            "restauration_disponible",
            "acces_handicapes",
            "telephone_contact",
            "email_contact",
            "site_web",
            "photo_principale",
            "conditions_acces",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "particularite": forms.Textarea(attrs={"rows": 3}),
            "adresse_complete": forms.Textarea(attrs={"rows": 3}),
            "conditions_acces": forms.Textarea(attrs={"rows": 3}),
        }
