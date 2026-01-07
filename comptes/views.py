from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404


def inscription(request):
    """Vue pour l'inscription des utilisateurs."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Connexion automatique après inscription
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {username} ! Votre compte a été créé avec succès.')
                return redirect('enregistrement')
    else:
        form = UserCreationForm()
    
    return render(request, 'comptes/inscription.html', {'form': form})


def connexion(request):
    """Vue pour la connexion des utilisateurs."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            # Rediriger vers la page demandée ou la page par défaut
            next_url = request.GET.get('next', 'enregistrement')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'comptes/connexion.html')


@login_required
def deconnexion(request):
    """Vue pour la déconnexion des utilisateurs."""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('mairie:accueil')


@login_required
def profil(request):
    """Vue pour afficher le profil de l'utilisateur (Mon compte)."""
    user = request.user
    context = {}
    
    # Vérifier les profils liés
    if hasattr(user, 'acteur_economique'):
        context['profile'] = user.acteur_economique
        context['profile_type'] = 'Acteur Économique'
        context['status'] = user.acteur_economique.est_valide_par_mairie
    elif hasattr(user, 'institution_financiere'):
        context['profile'] = user.institution_financiere
        context['profile_type'] = 'Institution Financière'
        context['status'] = user.institution_financiere.est_valide_par_mairie
    elif hasattr(user, 'profil_emploi'):
        context['profile'] = user.profil_emploi
        context['profile_type'] = user.profil_emploi.get_type_profil_display()
        context['status'] = user.profil_emploi.est_valide_par_mairie
    else:
        context['profile'] = None
        context['profile_type'] = 'Utilisateur standard'

    # Récupérer les candidatures aux appels d'offres
    # On importe ici pour éviter les imports circulaires
    from mairie.models import Candidature
    candidatures = Candidature.objects.filter(candidat=user).order_by('-date_soumission')
    context['candidatures'] = candidatures
    
    # Notifications
    notifications = Notification.objects.filter(recipient=user).order_by('-created_at')
    context['notifications'] = notifications
    context['notifications_unread_count'] = notifications.filter(is_read=False).count()
    
    return render(request, 'comptes/profil.html', context)


@login_required
@require_http_methods(["POST"])
def notification_mark_read(request, pk: int):
    """Marque une notification comme lue pour l'utilisateur connecté."""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save()
        messages.success(request, "Notification marquée comme lue.")
    return redirect('comptes:profil')


@login_required
@require_http_methods(["POST"])
def notifications_mark_all_read(request):
    """Marque toutes les notifications comme lues pour l'utilisateur connecté."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Toutes les notifications ont été marquées comme lues.")
    return redirect('comptes:profil')
