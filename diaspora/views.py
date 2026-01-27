from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator

from .forms import MembreDiasporaForm, MembreDiasporaEditForm
from .models import MembreDiaspora


@require_http_methods(["GET", "POST"])
def inscription_diaspora(request):
    """Inscription des membres de la diaspora."""

    if request.method == "POST":
        form = MembreDiasporaForm(request.POST, user=request.user)
        if form.is_valid():
            # Gestion de l'utilisateur
            if request.user.is_authenticated:
                user = request.user
            else:
                # Créer un nouveau compte utilisateur
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                
                # Vérifier si l'email existe déjà comme username
                if User.objects.filter(username=username).exists():
                    messages.error(request, "Un compte avec ce nom d'utilisateur existe déjà.")
                    context = {
                        "form": form,
                        "titre": "Inscription de la Diaspora",
                    }
                    return render(request, "diaspora/inscription.html", context)
                
                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=username, 
                    email=email, 
                    password=password
                )
                
                # Connecter l'utilisateur
                login(request, user, backend='mairie_kloto_platform.backends.EmailOrUsernameBackend')
            
            # Sauvegarder le profil diaspora
            membre = form.save(commit=False)
            membre.user = user
            membre.save()
            
            messages.success(
                request, 
                "Inscription réussie ! Bienvenue dans la communauté de la diaspora de Kloto 1."
            )
            return redirect('comptes:profil')
    else:
        form = MembreDiasporaForm(user=request.user)

    context = {
        "form": form,
        "titre": "Inscription de la Diaspora",
    }
    return render(request, "diaspora/inscription.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def modifier_diaspora(request):
    """Modification du profil des membres de la diaspora."""
    
    # Vérifier si l'utilisateur a un profil diaspora
    if not hasattr(request.user, 'membre_diaspora'):
        messages.error(request, "Vous n'avez pas de profil diaspora.")
        return redirect('comptes:profil')
        
    membre = request.user.membre_diaspora
    
    if request.method == "POST":
        form = MembreDiasporaEditForm(request.POST, instance=membre)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été mises à jour avec succès.")
            return redirect('comptes:profil')
    else:
        form = MembreDiasporaEditForm(instance=membre)
        
    context = {
        "form": form,
        "membre": membre,
        "titre": "Modification du profil Diaspora",
        "is_edit": True,
    }
    return render(request, "diaspora/modifier.html", context)


@login_required
def liste_diaspora(request):
    """Liste des membres de la diaspora (pour l'administration)."""
    
    # Vérifier si l'utilisateur est staff
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('mairie:accueil')
    
    # Filtrage
    pays_filtre = request.GET.get('pays', '')
    secteur_filtre = request.GET.get('secteur', '')
    statut_filtre = request.GET.get('statut', '')
    valide_filtre = request.GET.get('valide', '')
    
    membres = MembreDiaspora.objects.all()
    
    if pays_filtre:
        membres = membres.filter(pays_residence_actuelle__icontains=pays_filtre)
    
    if secteur_filtre:
        membres = membres.filter(secteur_activite=secteur_filtre)
    
    if statut_filtre:
        membres = membres.filter(statut_professionnel=statut_filtre)
    
    if valide_filtre:
        if valide_filtre == 'oui':
            membres = membres.filter(est_valide_par_mairie=True)
        elif valide_filtre == 'non':
            membres = membres.filter(est_valide_par_mairie=False)
    
    # Pagination
    paginator = Paginator(membres, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': MembreDiaspora.objects.count(),
        'valides': MembreDiaspora.objects.filter(est_valide_par_mairie=True).count(),
        'en_attente': MembreDiaspora.objects.filter(est_valide_par_mairie=False).count(),
        'pays_unique': MembreDiaspora.objects.values('pays_residence_actuelle').distinct().count(),
    }
    
    context = {
        'page_obj': page_obj,
        'membres': page_obj,
        'stats': stats,
        'pays_filtre': pays_filtre,
        'secteur_filtre': secteur_filtre,
        'statut_filtre': statut_filtre,
        'valide_filtre': valide_filtre,
        'secteur_choices': MembreDiaspora.SECTEUR_ACTIVITE_CHOICES,
        'statut_choices': MembreDiaspora.STATUT_PROFESSIONNEL_CHOICES,
    }
    
    return render(request, "diaspora/liste.html", context)


@login_required
def detail_diaspora(request, membre_id):
    """Détail d'un membre de la diaspora."""
    
    # Vérifier si l'utilisateur est staff ou s'il s'agit de son propre profil
    if not request.user.is_staff and (not hasattr(request.user, 'membre_diaspora') or request.user.membre_diaspora.id != membre_id):
        messages.error(request, "Accès non autorisé.")
        return redirect('mairie:accueil')
    
    try:
        membre = MembreDiaspora.objects.get(id=membre_id)
    except MembreDiaspora.DoesNotExist:
        messages.error(request, "Membre de la diaspora introuvable.")
        return redirect('diaspora:liste')
    
    context = {
        'membre': membre,
    }
    
    return render(request, "diaspora/detail.html", context)


@login_required
def valider_membre(request, membre_id):
    """Valider/invalider un membre de la diaspora (pour les administrateurs)."""
    
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Accès non autorisé'})
    
    try:
        membre = MembreDiaspora.objects.get(id=membre_id)
        # Toggle du statut de validation
        membre.est_valide_par_mairie = not membre.est_valide_par_mairie
        membre.save()
        
        statut = "validé" if membre.est_valide_par_mairie else "invalidé"
        return JsonResponse({
            'success': True, 
            'message': f'Membre {statut} avec succès',
            'nouveau_statut': membre.est_valide_par_mairie
        })
        
    except MembreDiaspora.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Membre introuvable'})


def statistiques_diaspora(request):
    """Statistiques publiques de la diaspora."""
    
    # Compter les membres par pays
    pays_stats = {}
    for membre in MembreDiaspora.objects.filter(est_valide_par_mairie=True):
        pays = membre.pays_residence_actuelle
        if pays in pays_stats:
            pays_stats[pays] += 1
        else:
            pays_stats[pays] = 1
    
    # Compter par secteur d'activité
    secteur_stats = {}
    for secteur_key, secteur_label in MembreDiaspora.SECTEUR_ACTIVITE_CHOICES:
        count = MembreDiaspora.objects.filter(
            est_valide_par_mairie=True,
            secteur_activite=secteur_key
        ).count()
        if count > 0:
            secteur_stats[secteur_label] = count
    
    # Statistiques générales
    total_membres = MembreDiaspora.objects.filter(est_valide_par_mairie=True).count()
    
    # Types d'appui proposés (agrégation)
    appuis_financiers = MembreDiaspora.objects.filter(
        est_valide_par_mairie=True,
        appui_investissement_projets=True
    ).count() + MembreDiaspora.objects.filter(
        est_valide_par_mairie=True,
        appui_financement_infrastructures=True
    ).count()
    
    appuis_techniques = MembreDiaspora.objects.filter(
        est_valide_par_mairie=True,
        transfert_competences=True
    ).count() + MembreDiaspora.objects.filter(
        est_valide_par_mairie=True,
        formation_jeunes=True
    ).count()
    
    context = {
        'total_membres': total_membres,
        'pays_stats': pays_stats,
        'secteur_stats': secteur_stats,
        'appuis_financiers': appuis_financiers,
        'appuis_techniques': appuis_techniques,
    }
    
    return render(request, "diaspora/statistiques.html", context)