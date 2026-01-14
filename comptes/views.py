from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_http_methods

from .models import Notification
from mairie.models import CampagnePublicitaire
from mairie.forms import CampagnePublicitaireForm, PubliciteForm

User = get_user_model()


def get_recipient_display_name(user):
    """Retourne le nom d'affichage approprié selon le type de profil de l'utilisateur."""
    if hasattr(user, 'acteur_economique') and user.acteur_economique:
        return user.acteur_economique.raison_sociale
    elif hasattr(user, 'institution_financiere') and user.institution_financiere:
        return user.institution_financiere.nom_institution
    elif hasattr(user, 'profil_emploi') and user.profil_emploi:
        profil = user.profil_emploi
        return f"{profil.nom} {profil.prenoms}"
    return user.get_username()


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

    can_request_ads = False
    campagne_publicitaire = None
    can_create_ads = False
    campagne_peut_renouveler = False

    # Vérifier les profils liés
    if hasattr(user, 'acteur_economique') and user.acteur_economique:
        context['profile'] = user.acteur_economique
        context['profile_type'] = 'Acteur Économique'
        context['status'] = user.acteur_economique.est_valide_par_mairie
        can_request_ads = bool(user.acteur_economique.est_valide_par_mairie)
    elif hasattr(user, 'institution_financiere') and user.institution_financiere:
        context['profile'] = user.institution_financiere
        context['profile_type'] = 'Institution Financière'
        context['status'] = user.institution_financiere.est_valide_par_mairie
        can_request_ads = bool(user.institution_financiere.est_valide_par_mairie)
    elif hasattr(user, 'profil_emploi') and user.profil_emploi:
        context['profile'] = user.profil_emploi
        context['profile_type'] = user.profil_emploi.get_type_profil_display()
        context['status'] = user.profil_emploi.est_valide_par_mairie
    else:
        context['profile'] = None
        context['profile_type'] = 'Utilisateur standard'

    # Campagne publicitaire éventuelle pour ce compte
    if can_request_ads:
        campagne_publicitaire = (
            CampagnePublicitaire.objects.filter(proprietaire=user)
            .order_by('-date_demande')
            .first()
        )
        if campagne_publicitaire and campagne_publicitaire.peut_creer_publicites:
            can_create_ads = True
        # Une campagne peut être renouvelée si elle est terminée ou si sa période est échue
        if campagne_publicitaire:
            from django.utils import timezone
            maintenant = timezone.now()
            if (
                campagne_publicitaire.statut == "terminee"
                or (
                    campagne_publicitaire.date_fin
                    and campagne_publicitaire.date_fin < maintenant
                )
            ):
                campagne_peut_renouveler = True

    # Récupérer les candidatures aux appels d'offres
    # On importe ici pour éviter les imports circulaires
    from mairie.models import Candidature
    candidatures = Candidature.objects.filter(candidat=user).order_by('-date_soumission')
    context['candidatures'] = candidatures
    
    # Notifications
    notifications = Notification.objects.filter(recipient=user).order_by('-created_at')
    context['notifications'] = notifications
    context['notifications_unread_count'] = notifications.filter(is_read=False).count()

    context['can_request_ads'] = can_request_ads
    context['campagne_publicitaire'] = campagne_publicitaire
    context['can_create_ads'] = can_create_ads
    context['campagne_peut_renouveler'] = campagne_peut_renouveler

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


class UserAutocompleteView(View):
    """Vue d'autocomplete personnalisée pour User avec affichage des noms corrects."""
    
    def get(self, request):
        """Gère les requêtes GET pour l'autocomplete."""
        term = request.GET.get('term', '') or request.GET.get('q', '')
        
        # Filtrer pour n'inclure que les utilisateurs avec un profil
        qs = User.objects.filter(
            Q(acteur_economique__isnull=False) |
            Q(institution_financiere__isnull=False) |
            Q(profil_emploi__isnull=False)
        ).select_related("acteur_economique", "institution_financiere", "profil_emploi").distinct()
        
        # Recherche
        if term:
            qs = qs.filter(
                Q(username__icontains=term) |
                Q(email__icontains=term) |
                Q(acteur_economique__raison_sociale__icontains=term) |
                Q(institution_financiere__nom_institution__icontains=term) |
                Q(profil_emploi__nom__icontains=term) |
                Q(profil_emploi__prenoms__icontains=term)
            )
        
        # Limiter les résultats
        qs = qs[:20]
        
        # Formater les résultats au format attendu par Django Admin
        # Django Admin utilise Select2 qui attend: {'results': [{'id': ..., 'text': ...}]}
        results = []
        for user in qs:
            results.append({
                'id': str(user.pk),
                'text': get_recipient_display_name(user)
            })
        
        return JsonResponse({'results': results})


@login_required
def demander_campagne_publicitaire(request):
    """Permet à une entreprise / institution financière de demander une campagne de publicité."""

    user = request.user

    # Vérifier le type de profil et la validation par la mairie
    profil_valide = False
    if hasattr(user, "acteur_economique") and user.acteur_economique:
        profil_valide = bool(user.acteur_economique.est_valide_par_mairie)
    elif hasattr(user, "institution_financiere") and user.institution_financiere:
        profil_valide = bool(user.institution_financiere.est_valide_par_mairie)

    if not profil_valide:
        messages.error(
            request,
            "Votre compte doit être validé par la mairie pour pouvoir demander une campagne de publicité.",
        )
        return redirect("comptes:profil")

    # Empêcher plusieurs campagnes simultanées non terminées
    campagne_existante = CampagnePublicitaire.objects.filter(
        proprietaire=user
    ).exclude(statut="terminee").first()
    if campagne_existante:
        messages.warning(
            request,
            "Vous avez déjà une campagne de publicité en cours ou en attente. "
            "Merci de contacter la mairie si vous souhaitez la modifier.",
        )
        return redirect("comptes:profil")

    if request.method == "POST":
        form = CampagnePublicitaireForm(request.POST)
        if form.is_valid():
            campagne = form.save(commit=False)
            campagne.proprietaire = user
            campagne.statut = "demande"
            campagne.save()
            messages.success(
                request,
                "Votre demande de campagne publicitaire a été transmise à la mairie. "
                "Vous serez informé(e) lorsque le maire l'aura validée.",
            )
            return redirect("comptes:profil")
    else:
        form = CampagnePublicitaireForm()

    return render(request, "comptes/demande_publicite.html", {"form": form})


@login_required
def creer_publicite(request):
    """Permet de créer une publicité une fois la campagne payée / active."""

    user = request.user

    campagne = (
        CampagnePublicitaire.objects.filter(
            proprietaire=user,
            statut__in=["payee", "active"],
        )
        .order_by("-date_demande")
        .first()
    )

    if not campagne or not campagne.peut_creer_publicites:
        messages.error(
            request,
            "Vous ne pouvez pas encore créer de publicité. "
            "La mairie doit d'abord accepter votre demande et enregistrer votre paiement.",
        )
        return redirect("comptes:profil")

    if request.method == "POST":
        form = PubliciteForm(request.POST, request.FILES)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.campagne = campagne
            if not pub.date_debut:
                pub.date_debut = timezone.now()
            if not pub.date_fin and campagne.duree_jours:
                pub.date_fin = pub.date_debut + timezone.timedelta(days=campagne.duree_jours)
            pub.save()
            messages.success(
                request,
                "Votre publicité a été créée avec succès. Elle sera affichée sur le site durant la période définie.",
            )
            return redirect("comptes:profil")
    else:
        form = PubliciteForm()

    return render(
        request,
        "comptes/creer_publicite.html",
        {
            "form": form,
            "campagne": campagne,
        },
    )
