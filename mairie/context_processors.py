from django.db import models
from django.utils import timezone

from .models import ConfigurationMairie, Publicite

def mairie_config(request):
    config = ConfigurationMairie.objects.filter(est_active=True).order_by("-date_modification").first()
    return {"mairie_config": config}


def publicite_globale(request):
    """
    Fournit une publicité aléatoire et les informations de l'entreprise à toutes les pages,
    sauf sur certaines vues sensibles (connexion, inscription, profil, tableau de bord, etc.).
    """
    # Exclure certaines routes (mon compte, auth, tableau de bord admin)
    resolver = getattr(request, "resolver_match", None)
    if not resolver:
        return {}

    excluded_names = {
        "connexion",
        "inscription",
        "profil",
        "tableau_bord",
        "gestion_publicites",
    }
    excluded_namespaces = {"admin"}

    if resolver.url_name in excluded_names or resolver.namespace in excluded_namespaces:
        return {}

    maintenant = timezone.now()
    publicites_qs = (
        Publicite.objects.filter(
            est_active=True,
            campagne__statut__in=["payee", "active"],
        )
        .select_related("campagne", "campagne__proprietaire")
        .filter(
            models.Q(date_debut__isnull=True) | models.Q(date_debut__lte=maintenant),
            models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=maintenant),
        )
        .order_by("?")
    )

    publicite_aleatoire = publicites_qs.first()
    if not publicite_aleatoire:
        return {}

    # Préparer les informations entreprise/institution
    campagne = publicite_aleatoire.campagne
    proprietaire = campagne.proprietaire
    acteur = getattr(proprietaire, "acteur_economique", None)
    institution = getattr(proprietaire, "institution_financiere", None)

    display_name = None
    telephone_principal = None
    telephone_secondaire = None
    logo_url = None

    if acteur:
        display_name = acteur.raison_sociale
        telephone_principal = acteur.telephone1
        telephone_secondaire = acteur.telephone2 or ""
    elif institution:
        display_name = institution.nom_institution
        telephone_principal = institution.telephone1
        telephone_secondaire = institution.telephone2 or institution.whatsapp or ""
        if institution.logo and hasattr(institution.logo, "url"):
            logo_url = institution.logo.url

    if not display_name:
        display_name = proprietaire.get_full_name() or proprietaire.get_username()

    publicite_entreprise = {
        "nom": display_name,
        "telephone_principal": telephone_principal,
        "telephone_secondaire": telephone_secondaire,
        "logo_url": logo_url,
    }

    return {
        "publicite_aleatoire": publicite_aleatoire,
        "publicite_entreprise": publicite_entreprise,
    }
