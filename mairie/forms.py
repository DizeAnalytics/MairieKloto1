from django import forms

from .models import Candidature, CampagnePublicitaire, Publicite, Suggestion, DonMairie


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
