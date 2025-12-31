from django import forms

from .models import ProfilEmploi


class ProfilJeuneForm(forms.ModelForm):
    """Formulaire d'inscription pour les jeunes en quête d'emploi."""

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
        ]:
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
            self.fields[name].required = True

        # Situation fixée à "retraite" pour ce formulaire
        situation_field = self.fields.get("situation_actuelle")
        if situation_field is not None:
            situation_field.choices = [("retraite", "Retraité")]
            situation_field.initial = "retraite"
