from django import forms

from .models import ActeurEconomique, InstitutionFinanciere, SiteTouristique


class ActeurEconomiqueForm(forms.ModelForm):
    """Formulaire d’enregistrement des acteurs économiques."""

    class Meta:
        model = ActeurEconomique
        fields = [
            "raison_sociale",
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
        }
        
        labels = {
            "cfe": "N° CFE",
            "numero_carte_operateur": "N° Carte d'Opérateur économique",
            "nif": "NIF",
        }


class InstitutionFinanciereForm(forms.ModelForm):
    """Formulaire d’inscription des institutions financières."""

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
        }

    def clean_services(self):
        """Transformer la liste de services en chaîne stockée dans le modèle."""
        values = self.cleaned_data.get("services", [])
        return ",".join(values)


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
