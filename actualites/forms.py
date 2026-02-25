from django import forms

from .models import CommentaireActualite


class CommentaireActualiteForm(forms.ModelForm):
    class Meta:
        model = CommentaireActualite
        # Nom et e-mail sont remplis automatiquement à partir du compte utilisateur
        # Seul le texte est saisi par le citoyen connecté.
        fields = ["texte"]
        widgets = {
            "texte": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Votre commentaire"}
            ),
        }
        labels = {
            "texte": "Commentaire",
        }

