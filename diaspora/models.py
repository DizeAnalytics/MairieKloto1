from django.db import models
from django.contrib.auth.models import User


class MembreDiaspora(models.Model):
    """Modèle pour l'enregistrement des membres de la diaspora de Kloto 1."""

    # === A. INFORMATIONS D'IDENTIFICATION ===
    SEXE_CHOICES = [
        ('masculin', 'Masculin'),
        ('feminin', 'Féminin'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenoms = models.CharField(max_length=150, verbose_name="Prénoms")
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES, verbose_name="Sexe")
    date_naissance = models.DateField(verbose_name="Date de naissance")
    nationalites = models.CharField(
        max_length=200, 
        verbose_name="Nationalité(s)", 
        help_text="Indiquez vos nationalités (ex: Togolaise, Française)"
    )
    numero_piece_identite = models.CharField(
        max_length=50, 
        verbose_name="Numéro de pièce d'identité (CNI/Passeport)"
    )
    pays_residence_actuelle = models.CharField(
        max_length=100, 
        verbose_name="Pays de résidence actuelle"
    )
    ville_residence_actuelle = models.CharField(
        max_length=100, 
        verbose_name="Ville de résidence actuelle"
    )
    adresse_complete_etranger = models.TextField(
        verbose_name="Adresse complète à l'étranger"
    )

    # === B. LIEN AVEC LA COMMUNE ===
    commune_origine = models.CharField(
        max_length=100, 
        verbose_name="Commune d'origine", 
        default="Kloto 1"
    )
    quartier_village_origine = models.CharField(
        max_length=100, 
        verbose_name="Quartier / Village d'origine"
    )
    nom_parent_tuteur_originaire = models.CharField(
        max_length=150, 
        verbose_name="Nom du parent ou tuteur originaire de la commune"
    )
    annee_depart_pays = models.PositiveIntegerField(
        verbose_name="Année de départ du pays"
    )

    FREQUENCE_RETOUR_CHOICES = [
        ('chaque_annee', 'Chaque année'),
        ('tous_2_3_ans', 'Tous les 2-3 ans'),
        ('rarement', 'Rarement'),
    ]
    frequence_retour_pays = models.CharField(
        max_length=20, 
        choices=FREQUENCE_RETOUR_CHOICES,
        verbose_name="Fréquence de retour au pays"
    )

    # === C. INFORMATIONS DE CONTACT ===
    telephone_whatsapp = models.CharField(
        max_length=30, 
        verbose_name="Téléphone (WhatsApp)"
    )
    email = models.EmailField(verbose_name="Email")
    reseaux_sociaux = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Réseaux sociaux (facultatif)",
        help_text="Facebook, LinkedIn, Instagram, etc."
    )
    contact_au_pays_nom = models.CharField(
        max_length=100, 
        verbose_name="Contact au pays - Nom"
    )
    contact_au_pays_telephone = models.CharField(
        max_length=30, 
        verbose_name="Contact au pays - Téléphone"
    )

    # === D. SITUATION PROFESSIONNELLE ===
    NIVEAU_ETUDES_CHOICES = [
        ('aucun', 'Aucun diplôme formel'),
        ('primaire', 'Primaire'),
        ('secondaire', 'Secondaire'),
        ('bts_dut', 'BTS / DUT'),
        ('licence', 'Licence'),
        ('master', 'Master'),
        ('doctorat', 'Doctorat'),
        ('autre', 'Autre'),
    ]

    niveau_etudes = models.CharField(
        max_length=20, 
        choices=NIVEAU_ETUDES_CHOICES,
        verbose_name="Niveau d'études"
    )
    domaine_formation = models.CharField(
        max_length=150, 
        verbose_name="Domaine de formation"
    )
    profession_actuelle = models.CharField(
        max_length=150, 
        verbose_name="Profession actuelle"
    )

    SECTEUR_ACTIVITE_CHOICES = [
        ('sante', 'Santé'),
        ('education', 'Éducation'),
        ('informatique', 'Informatique'),
        ('btp', 'BTP'),
        ('commerce', 'Commerce'),
        ('agriculture', 'Agriculture'),
        ('autre', 'Autre'),
    ]

    secteur_activite = models.CharField(
        max_length=20, 
        choices=SECTEUR_ACTIVITE_CHOICES,
        verbose_name="Secteur d'activité"
    )
    secteur_activite_autre = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Autre secteur (à préciser)"
    )
    annees_experience = models.PositiveIntegerField(
        verbose_name="Années d'expérience"
    )

    # === E. STATUT DANS LE PAYS DE RÉSIDENCE ===
    STATUT_PROFESSIONNEL_CHOICES = [
        ('salarie', 'Travailleur salarié'),
        ('entrepreneur', 'Entrepreneur / Chef d\'entreprise'),
        ('etudiant', 'Étudiant'),
        ('sans_emploi', 'Sans emploi'),
    ]

    statut_professionnel = models.CharField(
        max_length=20, 
        choices=STATUT_PROFESSIONNEL_CHOICES,
        verbose_name="Statut professionnel"
    )
    type_titre_sejour = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Type de titre de séjour (facultatif)"
    )

    # === COMMENT LA DIASPORA PEUT AIDER LA COMMUNE ===
    
    # A. Appui financier
    appui_investissement_projets = models.BooleanField(
        default=False, 
        verbose_name="Investissement dans des projets communaux"
    )
    appui_financement_infrastructures = models.BooleanField(
        default=False, 
        verbose_name="Financement d'infrastructures (forages, écoles, routes)"
    )
    appui_parrainage_communautaire = models.BooleanField(
        default=False, 
        verbose_name="Parrainage de projets communautaires"
    )
    appui_jeunes_femmes_entrepreneurs = models.BooleanField(
        default=False, 
        verbose_name="Appui aux jeunes et femmes entrepreneurs"
    )

    # B. Appui technique & compétences
    transfert_competences = models.BooleanField(
        default=False, 
        verbose_name="Transfert de compétences"
    )
    formation_jeunes = models.BooleanField(
        default=False, 
        verbose_name="Formation des jeunes"
    )
    appui_digitalisation = models.BooleanField(
        default=False, 
        verbose_name="Appui à la digitalisation de la commune"
    )
    conseils_techniques = models.BooleanField(
        default=False, 
        verbose_name="Conseils techniques / expertise"
    )
    encadrement_mentorat = models.BooleanField(
        default=False, 
        verbose_name="Encadrement à distance (mentorat)"
    )

    # C. Création d'emplois
    creation_entreprise_locale = models.BooleanField(
        default=False, 
        verbose_name="Création d'entreprise locale"
    )
    appui_pme_locales = models.BooleanField(
        default=False, 
        verbose_name="Appui aux PME locales"
    )
    recrutement_jeunes_commune = models.BooleanField(
        default=False, 
        verbose_name="Recrutement de jeunes de la commune"
    )

    # D. Partenariats & relations internationales
    mise_relation_ong = models.BooleanField(
        default=False, 
        verbose_name="Mise en relation avec ONG"
    )
    cooperation_decentralisee = models.BooleanField(
        default=False, 
        verbose_name="Coopération décentralisée"
    )
    recherche_financements_internationaux = models.BooleanField(
        default=False, 
        verbose_name="Recherche de financements internationaux"
    )
    promotion_commune_international = models.BooleanField(
        default=False, 
        verbose_name="Promotion de la commune à l'international"
    )

    # E. Engagement citoyen
    participation_activites_communales = models.BooleanField(
        default=False, 
        verbose_name="Participation aux activités communales"
    )
    participation_reunions_diaspora = models.BooleanField(
        default=False, 
        verbose_name="Participation aux réunions de la diaspora"
    )
    appui_actions_sociales_culturelles = models.BooleanField(
        default=False, 
        verbose_name="Appui aux actions sociales et culturelles"
    )

    # === QUESTIONS CLÉS ===
    DISPOSITION_PARTICIPATION_CHOICES = [
        ('oui', 'Oui'),
        ('non', 'Non'),
        ('a_etudier', 'À étudier'),
    ]

    comment_contribuer = models.TextField(
        verbose_name="Comment souhaitez-vous contribuer au développement de la commune ?",
        help_text="Décrivez en détail vos intentions et projets"
    )
    disposition_participation = models.CharField(
        max_length=20, 
        choices=DISPOSITION_PARTICIPATION_CHOICES,
        verbose_name="Êtes-vous disposé à participer à des projets communaux ?"
    )
    domaine_intervention_prioritaire = models.TextField(
        verbose_name="Dans quel domaine souhaitez-vous intervenir en priorité ?",
        help_text="Décrivez vos domaines d'intervention prioritaires"
    )

    # === VALIDATION ET MÉTADONNÉES ===
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='membre_diaspora'
    )
    accepte_rgpd = models.BooleanField(
        default=False,
        verbose_name="J'accepte que mes données soient traitées par la Mairie de Kloto 1"
    )
    accepte_contact = models.BooleanField(
        default=False,
        verbose_name="J'accepte d'être contacté par la mairie pour des projets"
    )
    est_valide_par_mairie = models.BooleanField(
        default=False,
        verbose_name="Validé par la mairie"
    )
    date_inscription = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Membre de la Diaspora"
        verbose_name_plural = "Membres de la Diaspora"
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.nom} {self.prenoms} ({self.pays_residence_actuelle})"

    def get_appuis_financiers(self):
        """Retourne la liste des types d'appui financier sélectionnés."""
        appuis = []
        if self.appui_investissement_projets:
            appuis.append("Investissement dans des projets communaux")
        if self.appui_financement_infrastructures:
            appuis.append("Financement d'infrastructures")
        if self.appui_parrainage_communautaire:
            appuis.append("Parrainage de projets communautaires")
        if self.appui_jeunes_femmes_entrepreneurs:
            appuis.append("Appui aux jeunes et femmes entrepreneurs")
        return appuis

    def get_competences_techniques(self):
        """Retourne la liste des compétences techniques proposées."""
        competences = []
        if self.transfert_competences:
            competences.append("Transfert de compétences")
        if self.formation_jeunes:
            competences.append("Formation des jeunes")
        if self.appui_digitalisation:
            competences.append("Appui à la digitalisation")
        if self.conseils_techniques:
            competences.append("Conseils techniques / expertise")
        if self.encadrement_mentorat:
            competences.append("Encadrement à distance (mentorat)")
        return competences