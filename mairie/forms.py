from django import forms
from django.contrib.auth.models import User

from .models import (
    Candidature,
    CampagnePublicitaire,
    Publicite,
    Suggestion,
    DonMairie,
    NewsletterSubscription,
    Contribuable,
    DirectionMairie,
    SectionDirection,
    PersonnelSection,
    ServiceSection,
)


class CandidatureForm(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = ["fichier_dossier", "message_accompagnement"]
        widgets = {
            "message_accompagnement": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Message optionnel pour accompagner votre dossier...",
                    "class": "form-control",
                }
            ),
            "fichier_dossier": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf",
                }
            ),
        }

    def clean_fichier_dossier(self):
        fichier = self.cleaned_data.get("fichier_dossier")
        if fichier and not fichier.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Seuls les fichiers PDF sont acceptés.")
        return fichier


class CampagnePublicitaireForm(forms.ModelForm):
    """Formulaire utilisé par l'entreprise / institution pour demander une campagne."""

    class Meta:
        model = CampagnePublicitaire
        fields = ["titre", "description", "duree_jours"]
        widgets = {
            "titre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: Campagne promotionnelle 2026",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Décrivez brièvement le contenu de la campagne, les produits ou services mis en avant…",
                }
            ),
            "duree_jours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
        }


class PubliciteForm(forms.ModelForm):
    """Formulaire de création d'une publicité individuelle dans une campagne."""

    class Meta:
        model = Publicite
        fields = ["titre", "texte", "image", "url_cible", "date_debut", "date_fin"]
        widgets = {
            "titre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Titre accrocheur de la publicité",
                }
            ),
            "texte": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Texte qui sera affiché dans la fenêtre de publicité.",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "url_cible": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://www.votre-entreprise.com",
                }
            ),
            "date_debut": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "date_fin": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
        }


class SuggestionForm(forms.ModelForm):
    """Formulaire de suggestion pour les visiteurs."""
    
    class Meta:
        model = Suggestion
        fields = ["nom", "email", "telephone", "sujet", "message"]
        widgets = {
            "nom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Votre nom complet",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "votre.email@exemple.com",
                    "required": True,
                }
            ),
            "telephone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+228 XX XX XX XX (facultatif)",
                }
            ),
            "sujet": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sujet de votre suggestion",
                    "required": True,
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Décrivez votre suggestion en détail...",
                    "required": True,
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nom"].required = True
        self.fields["email"].required = True
        self.fields["sujet"].required = True
        self.fields["message"].required = True


class DonForm(forms.ModelForm):
    """Formulaire pour faire un don à la mairie."""
    
    class Meta:
        model = DonMairie
        fields = ["nom_donateur", "email", "telephone", "type_don", "montant", "message"]
        widgets = {
            "nom_donateur": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Votre nom complet",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "votre.email@exemple.com",
                    "required": True,
                }
            ),
            "telephone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+228 XX XX XX XX (facultatif)",
                }
            ),
            "type_don": forms.Select(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),
            "montant": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Montant en FCFA",
                    "min": 1,
                    "step": 0.01,
                    "required": True,
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Message optionnel (ex: pour quel projet, dédicace, etc.)",
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nom_donateur"].required = True
        self.fields["email"].required = True
        self.fields["type_don"].required = True
        self.fields["montant"].required = True
        self.fields["type_don"].label = "Moyen de paiement"
    
    def clean_montant(self):
        montant = self.cleaned_data.get("montant")
        if montant and montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return montant


class NewsletterSubscriptionForm(forms.ModelForm):
    """Formulaire très simple pour l'inscription à la newsletter (email uniquement)."""

    class Meta:
        model = NewsletterSubscription
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Votre email pour recevoir les actualités",
                    "required": True,
                }
            ),
        }


class ContribuableForm(forms.ModelForm):
    """Formulaire d'inscription des contribuables (marchés / places publiques)."""

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
        model = Contribuable
        fields = [
            "nom",
            "prenom",
            "telephone",
            "date_naissance",
            "lieu_naissance",
            "nationalite",
        ]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "prenom": forms.TextInput(attrs={"class": "form-control"}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
            "date_naissance": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "lieu_naissance": forms.TextInput(attrs={"class": "form-control"}),
            "nationalite": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "nom": "Nom de famille",
            "prenom": "Prénom(s)",
            "telephone": "Numéro de téléphone",
            "date_naissance": "Date de naissance",
            "lieu_naissance": "Lieu de naissance",
            "nationalite": "Nationalité",
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


class DirectionMairieForm(forms.ModelForm):
    """Formulaire pour créer ou modifier une Direction de la mairie depuis le tableau de bord."""

    class Meta:
        model = DirectionMairie
        fields = ["nom", "sigle", "chef_direction", "ordre_affichage", "est_active"]
        widgets = {
            "nom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom complet de la direction",
                    "required": True,
                }
            ),
            "sigle": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sigle (ex: DAF, DST…)",
                }
            ),
            "chef_direction": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom du directeur / de la directrice",
                    "required": True,
                }
            ),
            "ordre_affichage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
            "est_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class SectionDirectionForm(forms.ModelForm):
    """Formulaire pour créer une Section rattachée à une Direction."""

    class Meta:
        model = SectionDirection
        fields = ["direction", "nom", "sigle", "chef_section", "ordre_affichage", "est_active"]
        widgets = {
            "direction": forms.Select(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),
            "nom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom complet de la section",
                    "required": True,
                }
            ),
            "sigle": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sigle (facultatif)",
                }
            ),
            "chef_section": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom du chef de section (facultatif)",
                }
            ),
            "ordre_affichage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
            "est_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class PersonnelSectionForm(forms.ModelForm):
    """Formulaire pour créer un membre du personnel rattaché à une Section."""

    class Meta:
        model = PersonnelSection
        fields = [
            "section",
            "nom_prenoms",
            "adresse",
            "contact",
            "fonction",
            "ordre_affichage",
            "est_actif",
        ]
        widgets = {
            "section": forms.Select(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),
            "nom_prenoms": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom et prénoms",
                    "required": True,
                }
            ),
            "adresse": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Adresse (facultatif)",
                }
            ),
            "contact": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Téléphone ou email (facultatif)",
                }
            ),
            "fonction": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Fonction occupée dans la section",
                    "required": True,
                }
            ),
            "ordre_affichage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
            "est_actif": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class ServiceSectionForm(forms.ModelForm):
    """Formulaire pour créer ou modifier un service rattaché à une Section."""

    class Meta:
        model = ServiceSection
        fields = [
            "section",
            "titre",
            "responsable",
            "description",
            "ordre_affichage",
            "est_actif",
        ]
        widgets = {
            "section": forms.Select(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),
            "titre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Titre du service",
                    "required": True,
                }
            ),
            "responsable": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Responsable du service (facultatif)",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Description des missions du service (facultatif)",
                }
            ),
            "ordre_affichage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
            "est_actif": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
