from django import forms

from .models import Candidature, CampagnePublicitaire, Publicite


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
