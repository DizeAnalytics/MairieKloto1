from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count

from acteurs.models import ActeurEconomique, InstitutionFinanciere
from emploi.models import ProfilEmploi
from mairie.models import Candidature


def home(request):
    """Page d'accueil de la plateforme (page Enregistrement)."""

    context = {}
    return render(request, "mairie-kloto-platform.html", context)


def fake_admin(request):
    """Fausse route admin pour sécuriser l'accès à l'administration Django."""
    return render(request, "admin_fake.html", status=404)


def is_staff_user(user):
    """Vérifie si l'utilisateur est staff ou superuser."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(is_staff_user)
def tableau_bord(request):
    """Tableau de bord administrateur."""
    
    # Statistiques générales
    stats = {
        'acteurs_economiques': ActeurEconomique.objects.count(),
        'institutions_financieres': InstitutionFinanciere.objects.count(),
        'jeunes': ProfilEmploi.objects.filter(type_profil='jeune').count(),
        'retraites': ProfilEmploi.objects.filter(type_profil='retraite').count(),
        'candidatures': Candidature.objects.count(),
        'total_inscriptions': (
            ActeurEconomique.objects.count() +
            InstitutionFinanciere.objects.count() +
            ProfilEmploi.objects.count()
        ),
    }
    
    context = {
        'stats': stats,
    }
    
    return render(request, "admin/tableau_bord.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_acteurs_economiques(request):
    """Liste des acteurs économiques enregistrés."""
    
    acteurs = ActeurEconomique.objects.all().order_by('-date_enregistrement')
    
    context = {
        'acteurs': acteurs,
        'titre': 'Acteurs Économiques',
    }
    
    return render(request, "admin/liste_inscriptions.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_institutions_financieres(request):
    """Liste des institutions financières enregistrées."""
    
    institutions = InstitutionFinanciere.objects.all().order_by('-date_enregistrement')
    
    context = {
        'institutions': institutions,
        'titre': 'Institutions Financières',
    }
    
    return render(request, "admin/liste_institutions.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_jeunes(request):
    """Liste des jeunes demandeurs d'emploi."""
    
    jeunes = ProfilEmploi.objects.filter(type_profil='jeune').order_by('-date_inscription')
    
    context = {
        'profils': jeunes,
        'titre': 'Jeunes Demandeurs d\'Emploi',
        'type_profil': 'jeune',
    }
    
    return render(request, "admin/liste_profils_emploi.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_retraites(request):
    """Liste des retraités actifs."""
    
    retraites = ProfilEmploi.objects.filter(type_profil='retraite').order_by('-date_inscription')
    
    context = {
        'profils': retraites,
        'titre': 'Retraités Actifs',
        'type_profil': 'retraite',
    }
    
    return render(request, "admin/liste_profils_emploi.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_candidatures(request):
    """Liste des candidatures aux appels d'offres."""
    
    candidatures = Candidature.objects.all().order_by('-date_soumission')
    
    context = {
        'candidatures': candidatures,
        'titre': 'Candidatures aux Appels d\'Offres',
    }
    
    return render(request, "admin/liste_candidatures.html", context)

