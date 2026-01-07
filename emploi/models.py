from django.db import models
from django.contrib.auth.models import User


class ProfilEmploi(models.Model):
    """Profil d'une personne en recherche d'activité (jeune ou retraité actif)."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='profil_emploi')

    TYPE_PROFIL_CHOICES = [
        ("jeune", "Jeune en quête d'emploi"),
        ("retraite", "Retraité actif"),
    ]

    SEXE_CHOICES = [
        ("masculin", "Masculin"),
        ("feminin", "Féminin"),
        ("autre", "Autre"),
    ]

    NIVEAU_ETUDE_CHOICES = [
        ("aucun", "Aucun diplôme formel"),
        ("cep", "CEP"),
        ("bepc", "BEPC"),
        ("bac", "BAC"),
        ("bts", "BTS / DUT"),
        ("licence", "Licence"),
        ("master", "Master"),
        ("doctorat", "Doctorat"),
        ("autre", "Autre"),
    ]

    DISPONIBILITE_CHOICES = [
        ("immediate", "Immédiate"),
        ("1_mois", "Sous 1 mois"),
        ("3_mois", "Sous 3 mois"),
        ("autre", "Autre"),
    ]

    TYPE_CONTRAT_CHOICES = [
        ("cdi", "CDI"),
        ("cdd", "CDD"),
        ("stage", "Stage"),
        ("mission", "Mission / Temps partiel"),
        ("benevolat", "Bénévolat"),
    ]

    SITUATION_ACTUELLE_CHOICES = [
        ("sans_emploi", "Sans emploi"),
        ("en_emploi", "En emploi"),
        ("etudiant", "Étudiant"),
        ("retraite", "Retraité"),
        ("autre", "Autre"),
    ]

    type_profil = models.CharField(max_length=10, choices=TYPE_PROFIL_CHOICES)

    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=150)
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES)
    date_naissance = models.DateField()
    nationalite = models.CharField(max_length=100, blank=True)

    telephone1 = models.CharField(max_length=30)
    telephone2 = models.CharField(max_length=30, blank=True)
    email = models.EmailField()

    quartier = models.CharField(max_length=255)
    canton = models.CharField(max_length=100, blank=True)
    adresse_complete = models.TextField()
    est_resident_kloto = models.BooleanField(
        default=True,
        help_text="Cochez si la personne réside dans la commune de Kloto 1.",
    )

    niveau_etude = models.CharField(
        max_length=20, choices=NIVEAU_ETUDE_CHOICES, blank=True
    )
    diplome_principal = models.CharField(max_length=150, blank=True)
    domaine_competence = models.TextField(help_text="Compétences principales, métiers.")
    experiences = models.TextField(
        blank=True, help_text="Brève description des expériences professionnelles."
    )
    situation_actuelle = models.CharField(
        max_length=20, choices=SITUATION_ACTUELLE_CHOICES, default="sans_emploi"
    )
    employeur_actuel = models.CharField(max_length=255, blank=True)

    disponibilite = models.CharField(
        max_length=20, choices=DISPONIBILITE_CHOICES, default="immediate"
    )
    type_contrat_souhaite = models.CharField(
        max_length=20, choices=TYPE_CONTRAT_CHOICES, blank=True
    )
    salaire_souhaite = models.CharField(max_length=50, blank=True)
    caisse_retraite = models.CharField(
        max_length=150,
        blank=True,
        help_text="Caisse de retraite / régime de pension (CNSS, CACIT, etc.).",
    )
    dernier_poste = models.CharField(
        max_length=255,
        blank=True,
        help_text="Dernier poste occupé (surtout pour les retraités).",
    )
    annees_experience = models.PositiveIntegerField(
        blank=True, null=True, help_text="Nombre d'années d'expérience."
    )

    accepte_rgpd = models.BooleanField(
        default=False,
        help_text="J'accepte que mes données soient traitées par la Mairie de Kloto 1.",
    )
    accepte_contact = models.BooleanField(
        default=False,
        help_text="J'accepte d'être contacté par des employeurs via la plateforme.",
    )

    est_valide_par_mairie = models.BooleanField(default=False)
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_inscription"]
        verbose_name = "Profil emploi"
        verbose_name_plural = "Profils emploi"

    def __str__(self) -> str:
        return f"{self.nom} {self.prenoms} ({self.get_type_profil_display()})"


