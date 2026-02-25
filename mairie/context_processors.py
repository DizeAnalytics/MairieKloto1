from django.db import models
from django.utils import timezone

from .models import (
    ConfigurationMairie,
    Publicite,
    Partenaire,
    NewsletterSubscription,
    VideoSpot,
)


def mairie_config(request):
    """
    Contexte global de configuration de la mairie.
    Ajoute aussi un indicateur pour savoir si l'utilisateur est déjà inscrit à la newsletter.
    """
    config = ConfigurationMairie.objects.filter(est_active=True).order_by(
        "-date_modification"
    ).first()

    newsletter_deja_inscrit = False

    # 1) Si un cookie dédié est présent, on considère l'utilisateur comme inscrit
    if request.COOKIES.get("newsletter_subscribed") == "1":
        newsletter_deja_inscrit = True
    else:
        # 2) Sinon, si l'utilisateur est connecté et possède un email,
        #    on vérifie dans la base s'il est abonné actif.
        user = getattr(request, "user", None)
        if getattr(user, "is_authenticated", False) and getattr(user, "email", ""):
            email = user.email.strip()
            if email:
                newsletter_deja_inscrit = NewsletterSubscription.objects.filter(
                    email__iexact=email,
                    est_actif=True,
                ).exists()

    return {
        "mairie_config": config,
        "newsletter_deja_inscrit": newsletter_deja_inscrit,
    }


def publicite_globale(request):
    """
    Fournit une publicité aléatoire et les informations de l'entreprise à toutes les pages,
    sauf sur certaines vues sensibles (connexion, inscription, profil, tableau de bord, etc.).
    Retourne aussi afficher_popup_newsletter pour afficher le popup d'inscription newsletter
    même en l'absence de publicité (entrée sur le site ou toutes les 10 min).
    """
    resolver = getattr(request, "resolver_match", None)
    if not resolver:
        return {}

    namespace = getattr(resolver, "namespace", "") or ""
    url_name = getattr(resolver, "url_name", "") or ""

    # Pages spéciales : accueil et liste des actualités
    # Sur ces pages, on affiche un spot vidéo dédié à la place des publicités classiques.
    is_home = namespace == "mairie" and url_name == "accueil"
    is_actualites_list = namespace == "actualites" and url_name == "liste"

    if is_home or is_actualites_list:
        maintenant = timezone.now()
        video_qs = VideoSpot.objects.filter(
            est_active=True,
        ).filter(
            models.Q(date_debut__isnull=True) | models.Q(date_debut__lte=maintenant),
            models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=maintenant),
        ).order_by("ordre_priorite", "?")

        spot = video_qs.first()
        if not spot:
            # Aucun spot vidéo disponible : ne rien afficher (ni publicité ni newsletter)
            return {
                "afficher_popup_newsletter": False,
                "publicite_aleatoire": None,
                "publicite_entreprise": None,
                "video_spot": None,
            }

        return {
            "afficher_popup_newsletter": True,
            "publicite_aleatoire": None,
            "publicite_entreprise": None,
            "video_spot": spot,
        }

    # Exclure certaines routes (mon compte, auth, tableau de bord admin)
    excluded_names = {
        "connexion",
        "inscription",
        "profil",
        "tableau_bord",
        "gestion_publicites",
    }
    excluded_namespaces = {"admin"}

    if url_name in excluded_names or namespace in excluded_namespaces:
        return {}

    # Toujours afficher le popup newsletter/publicité sur les pages non exclues
    result = {
        "afficher_popup_newsletter": True,
        "publicite_aleatoire": None,
        "publicite_entreprise": None,
        "video_spot": None,
    }

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
        return result

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

    result["publicite_aleatoire"] = publicite_aleatoire
    result["publicite_entreprise"] = publicite_entreprise
    return result


def partenaires_footer(request):
    """Fournit les partenaires actifs pour l'affichage dans le footer."""
    partenaires = Partenaire.objects.filter(est_actif=True)
    return {"partenaires": list(partenaires)}
