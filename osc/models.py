from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


def validate_osc_file(value):
    """Vérifie la taille (max 5 Mo) et l'extension PDF."""
    if not value:
        return
    limit = 5 * 1024 * 1024  # 5 Mo
    if value.size > limit:
        raise ValidationError("Le fichier est trop volumineux (max 5 Mo).")
    if not value.name.lower().endswith(".pdf"):
        raise ValidationError("Seuls les fichiers PDF sont acceptés.")

# Liste des types d'OSC (identique à celle du formulaire d'inscription)
OSC_TYPE_CHOICES = [
    ("", "Sélectionner un type"),
    ("CDQ", "CDQ (Comité de Développement de Quartier)"),
    ("CVD", "CVD (Comité Villageois de Développement)"),
    ("chefferie_traditionnelle", "Chefferie traditionnelle"),
    ("organisation_religieuse", "Organisation religieuse"),
    ("ong", "ONG"),
    ("representation_communautaire", "Représentation communautaire"),
    ("association_femmes", "Association de femmes"),
    ("association_jeunes", "Association de jeunes"),
    ("comite_developpement_local", "Comité de développement local"),
    ("association_culturelle_artistique", "Association culturelle et artistique"),
    ("association_sportive", "Association sportive"),
    ("cooperative", "Coopérative"),
    ("syndicat", "Syndicat"),
    ("association_commercants", "Association de commerçants"),
    ("organisation_producteurs", "Organisation de producteurs"),
    ("chambre_metiers", "Chambre de métiers"),
    ("ape", "Association de parents d'élèves (APE)"),
    ("club_scolaire_univ", "Club scolaire / universitaire"),
    ("centre_alphabetisation", "Centre d'alphabétisation"),
    ("association_etudiants", "Association d'étudiants"),
    ("association_sante", "Association communautaire de santé"),
    ("croix_rouge_humanitaire", "Croix-Rouge / Humanitaire"),
    ("organisation_personnes_handicapees", "Organisation de personnes handicapées"),
    ("association_entraide", "Association d'entraide / solidarité"),
    ("association_ecologique", "Association écologique"),
    ("comite_gestion_ressources", "Comité de gestion des ressources naturelles"),
    ("organisation_protection_env", "Organisation de protection eau / forêts"),
    ("organisation_droits_humains", "Organisation de défense des droits humains"),
    ("association_consommateurs", "Association de consommateurs"),
    ("observatoire_citoyen", "Observatoire citoyen"),
    ("organisation_veille_transparence", "Organisation de veille / transparence"),
    ("media_local", "Média local / Radio communautaire"),
    ("leader_opinion", "Leader d'opinion / Notable"),
    ("association_diaspora", "Association de la diaspora"),
    ("autre", "Autre"),
]


def get_osc_type_display(value):
    """Retourne le libellé du type d'OSC à partir de sa valeur (code)."""
    if not value:
        return ""
    d = dict(OSC_TYPE_CHOICES)
    return d.get(value, value)


class OrganisationSocieteCivile(models.Model):
    """Modèle pour l'enregistrement des Organisations de la Société Civile (OSC)."""

    nom_osc = models.CharField(max_length=255, verbose_name="Nom de l'OSC")
    sigle = models.CharField(max_length=100, blank=True, verbose_name="Sigle")
    type_osc = models.CharField(max_length=255, verbose_name="Type d'OSC")
    date_creation = models.DateField(null=True, blank=True, verbose_name="Date de création")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    telephone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")

    # Données structurées à partir des champs dynamiques du formulaire HTML
    domaines_intervention = models.TextField(
        blank=True,
        verbose_name="Domaines d'intervention",
        help_text="Liste des domaines d'intervention (un par ligne).",
    )
    membres_responsables = models.TextField(
        blank=True,
        verbose_name="Membres / Responsables",
        help_text="Liste des membres et de leurs fonctions (un par ligne).",
    )
    papiers_justificatifs = models.FileField(
        upload_to="osc/papiers/",
        blank=True,
        null=True,
        validators=[validate_osc_file],
        verbose_name="Papiers justificatifs (PDF)",
        help_text="Document PDF optionnel (statuts, récépissé, etc.). Max 5 Mo.",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organisations_societe_civile",
        verbose_name="Utilisateur associé",
    )
    date_enregistrement = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
    est_valide_par_mairie = models.BooleanField(
        default=False,
        verbose_name="Validé par la mairie",
    )

    class Meta:
        verbose_name = "Organisation de la Société Civile"
        verbose_name_plural = "Organisations de la Société Civile"
        ordering = ["-date_enregistrement"]

    def __str__(self) -> str:  # pragma: no cover - représentation simple
        return self.nom_osc

