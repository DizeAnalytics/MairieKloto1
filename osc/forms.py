from django import forms
from django.contrib.auth.models import User

from .models import OrganisationSocieteCivile, OSC_TYPE_CHOICES


class OrganisationSocieteCivileForm(forms.ModelForm):
    """Formulaire d'enregistrement des OSC, avec création optionnelle de compte utilisateur."""

    # Champs pour la création du compte utilisateur (si l'utilisateur n'est pas connecté)
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Nom d'utilisateur",
        help_text="Choisissez un nom d'utilisateur unique pour votre compte.",
        required=False,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Mot de passe",
        help_text="Créez un mot de passe pour accéder à votre espace personnel.",
        required=False,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirmer le mot de passe",
        required=False,
    )

    class Meta:
        model = OrganisationSocieteCivile
        fields = [
            "nom_osc",
            "sigle",
            "type_osc",
            "date_creation",
            "adresse",
            "telephone",
            "email",
            "papiers_justificatifs",
        ]
        widgets = {
            "nom_osc": forms.TextInput(attrs={"class": "form-control"}),
            "sigle": forms.TextInput(attrs={"class": "form-control"}),
            "type_osc": forms.Select(
                attrs={"class": "form-control"},
                choices=OSC_TYPE_CHOICES,
            ),
            "date_creation": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "adresse": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "papiers_justificatifs": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Si l'utilisateur est connecté, on masque les champs de création de compte
        if self.user and self.user.is_authenticated:
            self.fields.pop("username", None)
            self.fields.pop("password", None)
            self.fields.pop("confirm_password", None)

        # Champs obligatoires principaux
        required_fields = ["nom_osc"]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Validation des mots de passe
        if password or confirm_password:
            if password != confirm_password:
                self.add_error("confirm_password", "Les mots de passe ne correspondent pas.")

        # Validation du nom d'utilisateur
        if username and User.objects.filter(username=username).exists():
            self.add_error("username", "Ce nom d'utilisateur est déjà utilisé.")

        return cleaned_data

