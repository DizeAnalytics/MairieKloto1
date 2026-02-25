from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from .models import Notification
from mairie.models import (
    CampagnePublicitaire, AgentCollecteur, Contribuable, BoutiqueMagasin, 
    CotisationAnnuelle, PaiementCotisation, TicketMarche, EmplacementMarche,
    CotisationAnnuelleActeur, CotisationAnnuelleInstitution,
    PaiementCotisationActeur, PaiementCotisationInstitution
)
from acteurs.models import ActeurEconomique, InstitutionFinanciere
from mairie.forms import CampagnePublicitaireForm, PubliciteForm
from django.db.models import Q, Sum
from datetime import datetime
from decimal import Decimal, InvalidOperation

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


def get_user_display_name_for_welcome(user):
    """Retourne le nom et prénom (ou raison sociale) pour le message de bienvenue."""
    if hasattr(user, 'contribuable') and user.contribuable:
        return user.contribuable.nom_complet
    if hasattr(user, 'profil_emploi') and user.profil_emploi:
        p = user.profil_emploi
        return f"{p.nom} {p.prenoms}".strip()
    if hasattr(user, 'membre_diaspora') and user.membre_diaspora:
        p = user.membre_diaspora
        return f"{p.nom} {p.prenoms}".strip()
    if hasattr(user, 'acteur_economique') and user.acteur_economique:
        return user.acteur_economique.raison_sociale
    if hasattr(user, 'institution_financiere') and user.institution_financiere:
        return user.institution_financiere.nom_institution
    return user.get_full_name() or user.get_username()


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
            
            # Vérifier si l'utilisateur est un agent collecteur actif
            # Vérifier directement avec une requête pour éviter les problèmes de relation
            try:
                agent = AgentCollecteur.objects.get(user=user)
                if agent.statut == 'actif':
                    # Rediriger vers l'espace agent (ignorer le paramètre next pour les agents)
                    return redirect(reverse('comptes:espace_agent'))
            except AgentCollecteur.DoesNotExist:
                # L'utilisateur n'est pas un agent collecteur, continuer avec la redirection normale
                pass
            
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

    # Profils liés potentiels
    acteur_profile = getattr(user, "acteur_economique", None)
    institution_profile = getattr(user, "institution_financiere", None)
    emploi_profile = getattr(user, "profil_emploi", None)
    contribuable_profile = getattr(user, "contribuable", None)

    osc_manager = getattr(user, "organisations_societe_civile", None)
    osc_list = osc_manager.all() if osc_manager is not None else []
    diaspora_profile = getattr(user, "membre_diaspora", None)

    # Liste des types de profil pour affichage (un utilisateur peut avoir plusieurs rôles)
    profile_types_list = []
    if acteur_profile:
        profile_types_list.append("Acteur Économique")
    if institution_profile:
        profile_types_list.append("Institution Financière")
    if emploi_profile:
        profile_types_list.append(emploi_profile.get_type_profil_display())
    if osc_list:
        profile_types_list.append("Organisation de la Société Civile (OSC)")
    if diaspora_profile:
        profile_types_list.append("Diaspora")
    if contribuable_profile:
        profile_types_list.append("Contribuable (Marché / Place publique)")

    can_request_ads = False
    campagne_publicitaire = None
    can_create_ads = False
    campagne_peut_renouveler = False

    # Vérifier les profils liés
    if acteur_profile:
        context['profile'] = acteur_profile
        context['profile_type'] = 'Acteur Économique'
        context['status'] = acteur_profile.est_valide_par_mairie
        can_request_ads = bool(acteur_profile.est_valide_par_mairie)
    elif institution_profile:
        context['profile'] = institution_profile
        context['profile_type'] = 'Institution Financière'
        context['status'] = institution_profile.est_valide_par_mairie
        can_request_ads = bool(institution_profile.est_valide_par_mairie)
    elif emploi_profile:
        context['profile'] = emploi_profile
        context['profile_type'] = emploi_profile.get_type_profil_display()
        context['status'] = emploi_profile.est_valide_par_mairie
    else:
        context['profile'] = None
        context['profile_type'] = 'Utilisateur standard'

    # Récupérer les cotisations pour les contribuables
    cotisations_contribuable = None
    boutiques_magasins = None
    total_arrieres = None
    total_du_aujourdhui = None
    total_paye = None
    total_reste_a_payer = None

    if contribuable_profile:
        from mairie.models import BoutiqueMagasin, CotisationAnnuelle, PaiementCotisation

        boutiques_magasins = BoutiqueMagasin.objects.filter(
            contribuable=contribuable_profile,
            est_actif=True
        ).select_related('emplacement')

        # Récupérer toutes les cotisations annuelles du contribuable
        cotisations_contribuable = CotisationAnnuelle.objects.filter(
            boutique__contribuable=contribuable_profile
        ).select_related('boutique', 'boutique__emplacement').prefetch_related('paiements')

        if cotisations_contribuable.exists():
            maintenant = timezone.now()
            annee_courante = maintenant.year
            mois_courant = maintenant.month

            # 1) Montant total des arriérés (années < année courante)
            total_arrieres_annees_precedentes = sum(
                (c.reste_a_payer() for c in cotisations_contribuable if c.annee < annee_courante),
                start=Decimal("0"),
            )

            # 2) Arriérés de l'année en cours (mois précédents non payés)
            arrieres_annee_courante = Decimal("0")
            for c in cotisations_contribuable:
                if c.annee == annee_courante:
                    monthly_due = c.boutique.prix_location_mensuel or Decimal("0")
                    if monthly_due > 0:
                        # Montant dû jusqu'au mois courant (mois précédents)
                        montant_du_jusqu_aujourdhui = monthly_due * mois_courant
                        # Montant payé pour l'année en cours
                        montant_paye_annee_courante = c.montant_paye()
                        # Arriérés = dû - payé (si positif)
                        arrieres = montant_du_jusqu_aujourdhui - montant_paye_annee_courante
                        if arrieres > 0:
                            arrieres_annee_courante += arrieres

            # 3) Montant total des arriérés (années précédentes + mois précédents de l'année en cours)
            total_arrieres = total_arrieres_annees_precedentes + arrieres_annee_courante

            # 4) Montant total payé (toutes années, toutes boutiques) - gardé pour le calcul du reste à payer
            total_paye = PaiementCotisation.objects.filter(
                cotisation_annuelle__in=cotisations_contribuable
            ).aggregate(total=Sum("montant_paye"))["total"] or Decimal("0")

            # 5) Montant total dû en ce jour = arriérés + dû de l'année courante (jusqu'au mois courant)
            total_du_cette_annee = Decimal("0")
            for c in cotisations_contribuable:
                if c.annee == annee_courante:
                    monthly_due = c.boutique.prix_location_mensuel or Decimal("0")
                    if monthly_due > 0:
                        total_du_cette_annee += monthly_due * mois_courant
            total_du_aujourdhui = total_arrieres_annees_precedentes + total_du_cette_annee

            # 6) Reste à payer = dû en ce jour - payé (minimum 0)
            total_reste_a_payer = total_du_aujourdhui - total_paye
            if total_reste_a_payer < 0:
                total_reste_a_payer = Decimal("0")
        else:
            # Initialiser les valeurs à 0 si pas de cotisations
            total_arrieres = Decimal("0")
            total_du_aujourdhui = Decimal("0")
            total_paye = Decimal("0")
            total_reste_a_payer = Decimal("0")

    # Nom d'affichage pour "Bienvenue, NOM ET PRENOM"
    context["user_display_name"] = get_user_display_name_for_welcome(user)

    # Exposer tous les profils / organisations au template
    context["acteur_profile"] = acteur_profile
    context["institution_profile"] = institution_profile
    context["emploi_profile"] = emploi_profile
    context["contribuable_profile"] = contribuable_profile
    context["osc_list"] = osc_list
    context["diaspora_profile"] = diaspora_profile
    context["profile_types_list"] = profile_types_list
    context["has_any_profile"] = bool(profile_types_list)
    context["boutiques_magasins"] = boutiques_magasins
    context["cotisations_contribuable"] = cotisations_contribuable
    context["total_arrieres"] = total_arrieres
    context["total_du_aujourdhui"] = total_du_aujourdhui
    context["total_paye_contribuable"] = total_paye
    context["total_reste_a_payer_contribuable"] = total_reste_a_payer

    # Récupérer les cotisations pour les acteurs économiques et institutions financières
    cotisations_acteur = None
    cotisations_institution = None
    paiements_acteur = None
    paiements_institution = None
    total_montant_annuel_du_acteur = None
    total_montant_paye_acteur = None
    total_reste_a_payer_acteur = None
    total_montant_annuel_du_institution = None
    total_montant_paye_institution = None
    total_reste_a_payer_institution = None

    if acteur_profile:
        annee_courante = timezone.now().year
        # Récupérer toutes les cotisations annuelles de l'acteur
        cotisations_acteur = CotisationAnnuelleActeur.objects.filter(
            acteur=acteur_profile
        ).order_by('-annee')
        
        # Récupérer tous les paiements
        paiements_acteur = PaiementCotisationActeur.objects.filter(
            cotisation_annuelle__acteur=acteur_profile
        ).select_related('cotisation_annuelle', 'encaisse_par_agent').order_by('-date_paiement')
        
        # Calculer les totaux pour l'année courante
        cotisation_courante = cotisations_acteur.filter(annee=annee_courante).first()
        if cotisation_courante:
            total_montant_annuel_du_acteur = cotisation_courante.montant_annuel_du
            total_montant_paye_acteur = cotisation_courante.montant_paye()
            total_reste_a_payer_acteur = cotisation_courante.reste_a_payer()
        else:
            # Si pas de cotisation pour l'année courante, chercher la plus récente
            cotisation_recente = cotisations_acteur.first()
            if cotisation_recente:
                total_montant_annuel_du_acteur = cotisation_recente.montant_annuel_du
                total_montant_paye_acteur = cotisation_recente.montant_paye()
                total_reste_a_payer_acteur = cotisation_recente.reste_a_payer()

    if institution_profile:
        annee_courante = timezone.now().year
        # Récupérer toutes les cotisations annuelles de l'institution
        cotisations_institution = CotisationAnnuelleInstitution.objects.filter(
            institution=institution_profile
        ).order_by('-annee')
        
        # Récupérer tous les paiements
        paiements_institution = PaiementCotisationInstitution.objects.filter(
            cotisation_annuelle__institution=institution_profile
        ).select_related('cotisation_annuelle', 'encaisse_par_agent').order_by('-date_paiement')
        
        # Calculer les totaux pour l'année courante
        cotisation_courante = cotisations_institution.filter(annee=annee_courante).first()
        if cotisation_courante:
            total_montant_annuel_du_institution = cotisation_courante.montant_annuel_du
            total_montant_paye_institution = cotisation_courante.montant_paye()
            total_reste_a_payer_institution = cotisation_courante.reste_a_payer()
        else:
            # Si pas de cotisation pour l'année courante, chercher la plus récente
            cotisation_recente = cotisations_institution.first()
            if cotisation_recente:
                total_montant_annuel_du_institution = cotisation_recente.montant_annuel_du
                total_montant_paye_institution = cotisation_recente.montant_paye()
                total_reste_a_payer_institution = cotisation_recente.reste_a_payer()

    context["cotisations_acteur"] = cotisations_acteur
    context["cotisations_institution"] = cotisations_institution
    context["paiements_acteur"] = paiements_acteur
    context["paiements_institution"] = paiements_institution
    context["total_montant_annuel_du_acteur"] = total_montant_annuel_du_acteur
    context["total_montant_paye_acteur"] = total_montant_paye_acteur
    context["total_reste_a_payer_acteur"] = total_reste_a_payer_acteur
    context["total_montant_annuel_du_institution"] = total_montant_annuel_du_institution
    context["total_montant_paye_institution"] = total_montant_paye_institution
    context["total_reste_a_payer_institution"] = total_reste_a_payer_institution

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


@login_required
def espace_agent(request):
    """Espace agent collecteur - Dashboard avec les contribuables supervisés."""
    # Vérifier que l'utilisateur est un agent collecteur actif
    try:
        agent = request.user.agent_collecteur
        if agent.statut != 'actif':
            messages.error(request, "Votre compte agent n'est pas actif. Contactez l'administration.")
            return redirect('comptes:profil')
    except AgentCollecteur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cet espace.")
        return redirect('comptes:profil')
    
    # Récupérer les emplacements assignés à l'agent
    emplacements = agent.emplacements_assignes.all()
    
    # Récupérer les contribuables qui ont des boutiques/magasins dans ces emplacements
    contribuables_ids = BoutiqueMagasin.objects.filter(
        emplacement__in=emplacements,
        est_actif=True
    ).values_list('contribuable_id', flat=True).distinct()
    
    contribuables = Contribuable.objects.filter(id__in=contribuables_ids).prefetch_related(
        'boutiques_magasins__emplacement',
        'boutiques_magasins__cotisations_annuelles__paiements'
    )
    
    # Récupérer les acteurs économiques assignés à cet agent
    acteurs_economiques = ActeurEconomique.objects.filter(
        agents_collecteurs=agent,
        est_valide_par_mairie=True
    ).prefetch_related('cotisations_annuelles__paiements')
    
    # Récupérer les institutions financières assignées à cet agent
    institutions_financieres = InstitutionFinanciere.objects.filter(
        agents_collecteurs=agent,
        est_valide_par_mairie=True
    ).prefetch_related('cotisations_annuelles__paiements')
    
    # Statistiques
    annee_courante = timezone.now().year
    
    # Montant total collecté aujourd'hui
    aujourdhui = timezone.now().date()
    montant_aujourdhui = (
        PaiementCotisation.objects.filter(
            encaisse_par_agent=agent,
            date_paiement__date=aujourdhui
        ).aggregate(total=Sum('montant_paye'))['total'] or 0
    ) + (
        TicketMarche.objects.filter(
            encaisse_par_agent=agent,
            date=aujourdhui
        ).aggregate(total=Sum('montant'))['total'] or 0
    ) + (
        PaiementCotisationActeur.objects.filter(
            encaisse_par_agent=agent,
            date_paiement__date=aujourdhui
        ).aggregate(total=Sum('montant_paye'))['total'] or 0
    ) + (
        PaiementCotisationInstitution.objects.filter(
            encaisse_par_agent=agent,
            date_paiement__date=aujourdhui
        ).aggregate(total=Sum('montant_paye'))['total'] or 0
    )
    
    # Montant total collecté ce mois
    mois_courant = timezone.now().month
    montant_mois = agent.montant_total_collecte(
        date_debut=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        date_fin=timezone.now()
    )
    
    # Nombre de contribuables supervisés
    nombre_contribuables = contribuables.count()
    
    # Recherche/filtrage
    search_query = request.GET.get('q', '')
    if search_query:
        contribuables = contribuables.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(telephone__icontains=search_query)
        )
    
    context = {
        'agent': agent,
        'contribuables': contribuables,
        'acteurs_economiques': acteurs_economiques,
        'institutions_financieres': institutions_financieres,
        'emplacements': emplacements,
        'nombre_contribuables': nombre_contribuables,
        'montant_aujourdhui': montant_aujourdhui,
        'montant_mois': montant_mois,
        'annee_courante': annee_courante,
        'search_query': search_query,
    }
    
    return render(request, 'comptes/espace_agent.html', context)


@login_required
def payer_contribuable(request, contribuable_id):
    """Permet à un agent de payer pour un contribuable (cotisation ou ticket marché)."""
    # Vérifier que l'utilisateur est un agent collecteur actif
    try:
        agent = request.user.agent_collecteur
        if agent.statut != 'actif':
            messages.error(request, "Votre compte agent n'est pas actif.")
            return redirect('comptes:espace_agent')
    except AgentCollecteur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas autorisé à effectuer cette action.")
        return redirect('comptes:profil')
    
    contribuable = get_object_or_404(Contribuable, id=contribuable_id)
    
    # Vérifier que le contribuable est dans les emplacements assignés à l'agent
    emplacements_agent = agent.emplacements_assignes.all()
    boutiques_contribuable = BoutiqueMagasin.objects.filter(
        contribuable=contribuable,
        emplacement__in=emplacements_agent,
        est_actif=True
    )
    
    if not boutiques_contribuable.exists():
        messages.error(request, "Ce contribuable n'est pas dans votre zone de supervision.")
        return redirect('comptes:espace_agent')
    
    # Récupérer/garantir les cotisations annuelles pour les boutiques du contribuable
    # On prend toutes les années afin de pouvoir encaisser d'abord les arriérés.
    # Si aucune cotisation n'existe encore pour l'année courante pour une boutique donnée,
    # on crée automatiquement la ligne de cotisation annuelle correspondante.
    annee_courante = timezone.now().year

    for boutique in boutiques_contribuable:
        if not CotisationAnnuelle.objects.filter(boutique=boutique, annee=annee_courante).exists():
            CotisationAnnuelle.objects.create(
                boutique=boutique,
                annee=annee_courante,
                montant_annuel_du=boutique.get_prix_annuel(),
            )

    cotisations_annuelles = (
        CotisationAnnuelle.objects.filter(boutique__in=boutiques_contribuable)
        .select_related('boutique', 'boutique__emplacement')
        .prefetch_related('paiements')
        .order_by('-annee', 'boutique__matricule')
    )

    # Préparer un résumé par mois pour affichage (payé / partiel / non payé)
    mois_noms = ["Jan.", "Fév.", "Mars", "Avr.", "Mai", "Juin", "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc."]
    cotisations_resume = []
    for cotisation in cotisations_annuelles:
        monthly_due = float(cotisation.boutique.prix_location_mensuel or 0)
        paiements_par_mois = (
            cotisation.paiements.values("mois")
            .annotate(total=Sum("montant_paye"))
        )
        map_paiements = {p["mois"]: float(p["total"] or 0) for p in paiements_par_mois}
        mois_list = []
        for m in range(1, 13):
            total_m = map_paiements.get(m, 0.0)
            if total_m <= 0:
                status = "non_paye"
            elif monthly_due and total_m >= monthly_due:
                status = "paye"
            else:
                status = "partiel"
            mois_list.append(
                {
                    "numero": m,
                    "nom": mois_noms[m - 1],
                    "total": total_m,
                    "status": status,
                }
            )
        cotisations_resume.append(
            {
                "cotisation": cotisation,
                "monthly_due": monthly_due,
                "mois": mois_list,
            }
        )
    
    # Type de paiement (cotisation ou ticket)
    # En POST, le formulaire envoie un champ caché `type`.
    type_paiement = request.GET.get('type', 'cotisation')  # 'cotisation' ou 'ticket'
    
    if request.method == 'POST':
        type_paiement = request.POST.get('type') or type_paiement

        if type_paiement == 'cotisation':
            # Paiement de cotisation mensuelle (montant réparti automatiquement sur les mois non payés)
            cotisation_id = request.POST.get('cotisation_annuelle')
            montant = request.POST.get('montant')
            notes = request.POST.get('notes', '')
            
            try:
                if not cotisation_id:
                    messages.error(request, "Veuillez choisir une boutique/magasin.")
                    return redirect('comptes:payer_contribuable', contribuable_id=contribuable.id)

                if montant is None or str(montant).strip() == "":
                    messages.error(request, "Veuillez renseigner un montant.")
                    return redirect('comptes:payer_contribuable', contribuable_id=contribuable.id)

                try:
                    montant_value = Decimal(str(montant))
                except (InvalidOperation, TypeError, ValueError):
                    messages.error(request, "Montant invalide. Veuillez saisir un nombre.")
                    return redirect('comptes:payer_contribuable', contribuable_id=contribuable.id)

                if montant_value <= 0:
                    messages.error(request, "Le montant doit être supérieur à zéro.")
                    return redirect('comptes:payer_contribuable', contribuable_id=contribuable.id)

                cotisation_annuelle = CotisationAnnuelle.objects.get(id=cotisation_id)
                # Sécurité: la cotisation doit appartenir à une boutique du contribuable dans la zone de l'agent
                if cotisation_annuelle.boutique.contribuable_id != contribuable.id:
                    messages.error(request, "Cotisation invalide pour ce contribuable.")
                    return redirect('comptes:espace_agent')
                if cotisation_annuelle.boutique.emplacement_id not in list(emplacements_agent.values_list("id", flat=True)):
                    messages.error(request, "Cette cotisation n'est pas dans votre zone de supervision.")
                    return redirect('comptes:espace_agent')

                # Vérifier les arriérés des années précédentes pour cette boutique
                cotisations_anciennes = CotisationAnnuelle.objects.filter(
                    boutique=cotisation_annuelle.boutique,
                    annee__lt=cotisation_annuelle.annee,
                ).order_by('annee')

                for c in cotisations_anciennes:
                    if c.reste_a_payer() > 0:
                        messages.error(
                            request,
                            f"Cette boutique a encore des arriérés pour l'année {c.annee}. "
                            f"Veuillez d'abord encaisser ces arriérés avant de commencer les paiements pour {cotisation_annuelle.annee}."
                        )
                        return redirect('comptes:payer_contribuable', contribuable_id=contribuable.id)

                # Montant mensuel dû pour cette boutique (en Decimal)
                monthly_due = cotisation_annuelle.boutique.prix_location_mensuel or Decimal("0")
                if monthly_due <= 0:
                    messages.error(request, "Montant mensuel de la cotisation non défini pour cette boutique.")
                    return redirect('comptes:payer_contribuable', contribuable_id=contribuable.id)

                # Répartition séquentielle du montant :
                # - on complète d'abord les mois partiellement payés (dans l'ordre),
                # - puis on paie les mois suivants,
                # afin d'éviter des mois « à moitié payés » au milieu de l'année.
                montant_restant = montant_value
                paiements_crees = []

                # Pour chaque mois de 1 à 12, on regarde combien est déjà payé
                # et on complète si nécessaire, avant de passer au mois suivant.
                for mois in range(1, 13):
                    if montant_restant <= 0:
                        break

                    paiement_existant = PaiementCotisation.objects.filter(
                        cotisation_annuelle=cotisation_annuelle,
                        mois=mois,
                    ).first()

                    deja_paye = paiement_existant.montant_paye if paiement_existant else Decimal("0")

                    # Si ce mois est déjà entièrement payé, on passe au suivant
                    if deja_paye >= monthly_due:
                        continue

                    reste_pour_mois = monthly_due - deja_paye
                    a_payer_ici = min(montant_restant, reste_pour_mois)

                    if a_payer_ici <= 0:
                        continue

                    if paiement_existant:
                        # On complète le paiement existant pour ce mois
                        paiement_existant.montant_paye = paiement_existant.montant_paye + a_payer_ici
                        paiement_existant.encaisse_par_agent = agent
                        # On met à jour la date de paiement et les notes
                        paiement_existant.date_paiement = timezone.now()
                        if notes:
                            paiement_existant.notes = (paiement_existant.notes + "\n" if paiement_existant.notes else "") + notes
                        paiement_existant.save()
                    else:
                        # Aucun paiement pour ce mois : on crée l'enregistrement
                        PaiementCotisation.objects.create(
                            cotisation_annuelle=cotisation_annuelle,
                            mois=mois,
                            montant_paye=a_payer_ici,
                            encaisse_par_agent=agent,
                            notes=notes,
                        )

                    paiements_crees.append(mois)
                    montant_restant -= a_payer_ici

                if not paiements_crees:
                    messages.error(
                        request,
                        "Le montant saisi est insuffisant pour enregistrer un paiement sur les mois restants."
                    )
                    return redirect('comptes:payer_contribuable', contribuable_id=contribuable.id)

                # Message récapitulatif
                mois_str = ", ".join(str(m) for m in sorted(paiements_crees))
                messages.success(
                    request,
                    f"Paiement de {montant_value:.0f} FCFA enregistré et réparti sur les mois suivants : {mois_str}."
                )
                return redirect('comptes:payer_contribuable', contribuable_id=contribuable.id)
            except Exception as e:
                messages.error(request, f"Erreur lors de l'enregistrement du paiement : {str(e)}")
        
        elif type_paiement == 'ticket':
            # Paiement de ticket marché
            emplacement_id = request.POST.get('emplacement')
            date_ticket = request.POST.get('date')
            nom_vendeur = request.POST.get('nom_vendeur')
            telephone_vendeur = request.POST.get('telephone_vendeur', '')
            montant = request.POST.get('montant')
            notes = request.POST.get('notes', '')
            
            try:
                emplacement = EmplacementMarche.objects.get(id=emplacement_id)
                
                # Vérifier que l'emplacement est assigné à l'agent
                if emplacement not in agent.emplacements_assignes.all():
                    messages.error(request, "Cet emplacement n'est pas dans votre zone de supervision.")
                else:
                    ticket = TicketMarche.objects.create(
                        date=datetime.strptime(date_ticket, '%Y-%m-%d').date(),
                        emplacement=emplacement,
                        contribuable=contribuable,
                        nom_vendeur=nom_vendeur,
                        telephone_vendeur=telephone_vendeur,
                        montant=float(montant),
                        encaisse_par_agent=agent,
                        notes=notes
                    )
                    messages.success(request, f"Ticket marché enregistré avec succès : {montant} FCFA.")
                    return redirect('comptes:payer_contribuable', contribuable_id=contribuable.id)
            except Exception as e:
                messages.error(request, f"Erreur lors de l'enregistrement du ticket : {str(e)}")
    
    # Récupérer les emplacements pour le formulaire de ticket
    emplacements = agent.emplacements_assignes.all()
    
    context = {
        'agent': agent,
        'contribuable': contribuable,
        'boutiques_contribuable': boutiques_contribuable,
        'cotisations_annuelles': cotisations_annuelles,
        'cotisations_resume': cotisations_resume,
        'emplacements': emplacements,
        'type_paiement': type_paiement,
        'annee_courante': annee_courante,
    }
    
    return render(request, 'comptes/payer_contribuable.html', context)


@login_required
def payer_acteur(request, acteur_id):
    """Permet à un agent de payer la cotisation annuelle d'un acteur économique."""
    # Vérifier que l'utilisateur est un agent collecteur actif
    try:
        agent = request.user.agent_collecteur
        if agent.statut != 'actif':
            messages.error(request, "Votre compte agent n'est pas actif.")
            return redirect('comptes:espace_agent')
    except AgentCollecteur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas autorisé à effectuer cette action.")
        return redirect('comptes:profil')
    
    acteur = get_object_or_404(ActeurEconomique, id=acteur_id)
    
    # Vérifier que l'acteur est assigné à cet agent
    if agent not in acteur.agents_collecteurs.all():
        messages.error(request, "Cet acteur économique n'est pas dans votre zone de supervision.")
        return redirect('comptes:espace_agent')
    
    # Récupérer/garantir les cotisations annuelles pour l'acteur
    annee_courante = timezone.now().year
    
    if request.method == 'POST':
        cotisation_id = request.POST.get('cotisation_annuelle')
        montant = request.POST.get('montant')
        notes = request.POST.get('notes', '')
        
        try:
            if not cotisation_id:
                messages.error(request, "Veuillez choisir une cotisation.")
                return redirect('comptes:payer_acteur', acteur_id=acteur.id)
            
            if montant is None or str(montant).strip() == "":
                messages.error(request, "Veuillez renseigner un montant.")
                return redirect('comptes:payer_acteur', acteur_id=acteur.id)
            
            try:
                montant_value = Decimal(str(montant))
            except (InvalidOperation, TypeError, ValueError):
                messages.error(request, "Montant invalide. Veuillez saisir un nombre.")
                return redirect('comptes:payer_acteur', acteur_id=acteur.id)
            
            if montant_value <= 0:
                messages.error(request, "Le montant doit être supérieur à zéro.")
                return redirect('comptes:payer_acteur', acteur_id=acteur.id)
            
            cotisation_annuelle = CotisationAnnuelleActeur.objects.get(id=cotisation_id)
            
            # Vérifier que la cotisation appartient à l'acteur assigné à l'agent
            if cotisation_annuelle.acteur_id != acteur.id:
                messages.error(request, "Cotisation invalide pour cet acteur.")
                return redirect('comptes:espace_agent')
            
            if agent not in cotisation_annuelle.acteur.agents_collecteurs.all():
                messages.error(request, "Cet acteur n'est pas dans votre zone de supervision.")
                return redirect('comptes:espace_agent')
            
            # Vérifier que le montant annuel dû est défini
            if cotisation_annuelle.montant_annuel_du <= 0:
                messages.error(
                    request,
                    f"Le montant annuel dû pour l'année {cotisation_annuelle.annee} n'a pas encore été défini. "
                    "Veuillez contacter l'administrateur pour définir le montant de la cotisation."
                )
                return redirect('comptes:payer_acteur', acteur_id=acteur.id)
            
            # Vérifier les arriérés des années précédentes
            cotisations_anciennes = CotisationAnnuelleActeur.objects.filter(
                acteur=cotisation_annuelle.acteur,
                annee__lt=cotisation_annuelle.annee,
            ).order_by('annee')
            
            for c in cotisations_anciennes:
                if c.reste_a_payer() > 0:
                    messages.error(
                        request,
                        f"Cet acteur a encore des arriérés pour l'année {c.annee}. "
                        f"Veuillez d'abord encaisser ces arriérés avant de commencer les paiements pour {cotisation_annuelle.annee}."
                    )
                    return redirect('comptes:payer_acteur', acteur_id=acteur.id)
            
            # Vérifier que le montant ne dépasse pas le reste à payer
            reste_a_payer = cotisation_annuelle.reste_a_payer()
            if montant_value > reste_a_payer:
                messages.error(
                    request,
                    f"Le montant ({montant_value:,.0f} FCFA) dépasse le reste à payer ({reste_a_payer:,.0f} FCFA)."
                )
                return redirect('comptes:payer_acteur', acteur_id=acteur.id)
            
            # Créer le paiement annuel
            PaiementCotisationActeur.objects.create(
                cotisation_annuelle=cotisation_annuelle,
                montant_paye=montant_value,
                encaisse_par_agent=agent,
                notes=notes,
            )
            
            messages.success(
                request,
                f"Paiement de {montant_value:,.0f} FCFA enregistré pour {acteur.raison_sociale} ({cotisation_annuelle.annee})."
            )
            return redirect('comptes:payer_acteur', acteur_id=acteur.id)
            
        except CotisationAnnuelleActeur.DoesNotExist:
            messages.error(request, "Cotisation introuvable.")
            return redirect('comptes:espace_agent')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement du paiement: {str(e)}")
            return redirect('comptes:payer_acteur', acteur_id=acteur.id)
    
    # Créer la cotisation de l'année courante si elle n'existe pas
    if not CotisationAnnuelleActeur.objects.filter(acteur=acteur, annee=annee_courante).exists():
        # Le montant annuel doit être défini par l'admin, pour l'instant on utilise 0
        CotisationAnnuelleActeur.objects.create(
            acteur=acteur,
            annee=annee_courante,
            montant_annuel_du=Decimal("0"),  # À définir par l'admin
        )
    
    cotisations_annuelles = CotisationAnnuelleActeur.objects.filter(
        acteur=acteur
    ).order_by('-annee')
    
    context = {
        'agent': agent,
        'acteur': acteur,
        'cotisations_annuelles': cotisations_annuelles,
        'annee_courante': annee_courante,
    }
    
    return render(request, 'comptes/payer_acteur.html', context)


@login_required
def payer_institution(request, institution_id):
    """Permet à un agent de payer la cotisation annuelle d'une institution financière."""
    # Vérifier que l'utilisateur est un agent collecteur actif
    try:
        agent = request.user.agent_collecteur
        if agent.statut != 'actif':
            messages.error(request, "Votre compte agent n'est pas actif.")
            return redirect('comptes:espace_agent')
    except AgentCollecteur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas autorisé à effectuer cette action.")
        return redirect('comptes:profil')
    
    institution = get_object_or_404(InstitutionFinanciere, id=institution_id)
    
    # Vérifier que l'institution est assignée à cet agent
    if agent not in institution.agents_collecteurs.all():
        messages.error(request, "Cette institution financière n'est pas dans votre zone de supervision.")
        return redirect('comptes:espace_agent')
    
    # Récupérer/garantir les cotisations annuelles pour l'institution
    annee_courante = timezone.now().year
    
    if request.method == 'POST':
        cotisation_id = request.POST.get('cotisation_annuelle')
        montant = request.POST.get('montant')
        notes = request.POST.get('notes', '')
        
        try:
            if not cotisation_id:
                messages.error(request, "Veuillez choisir une cotisation.")
                return redirect('comptes:payer_institution', institution_id=institution.id)
            
            if montant is None or str(montant).strip() == "":
                messages.error(request, "Veuillez renseigner un montant.")
                return redirect('comptes:payer_institution', institution_id=institution.id)
            
            try:
                montant_value = Decimal(str(montant))
            except (InvalidOperation, TypeError, ValueError):
                messages.error(request, "Montant invalide. Veuillez saisir un nombre.")
                return redirect('comptes:payer_institution', institution_id=institution.id)
            
            if montant_value <= 0:
                messages.error(request, "Le montant doit être supérieur à zéro.")
                return redirect('comptes:payer_institution', institution_id=institution.id)
            
            cotisation_annuelle = CotisationAnnuelleInstitution.objects.get(id=cotisation_id)
            
            # Vérifier que la cotisation appartient à l'institution assignée à l'agent
            if cotisation_annuelle.institution_id != institution.id:
                messages.error(request, "Cotisation invalide pour cette institution.")
                return redirect('comptes:espace_agent')
            
            if agent not in cotisation_annuelle.institution.agents_collecteurs.all():
                messages.error(request, "Cette institution n'est pas dans votre zone de supervision.")
                return redirect('comptes:espace_agent')
            
            # Vérifier que le montant annuel dû est défini
            if cotisation_annuelle.montant_annuel_du <= 0:
                messages.error(
                    request,
                    f"Le montant annuel dû pour l'année {cotisation_annuelle.annee} n'a pas encore été défini. "
                    "Veuillez contacter l'administrateur pour définir le montant de la cotisation."
                )
                return redirect('comptes:payer_institution', institution_id=institution.id)
            
            # Vérifier les arriérés des années précédentes
            cotisations_anciennes = CotisationAnnuelleInstitution.objects.filter(
                institution=cotisation_annuelle.institution,
                annee__lt=cotisation_annuelle.annee,
            ).order_by('annee')
            
            for c in cotisations_anciennes:
                if c.reste_a_payer() > 0:
                    messages.error(
                        request,
                        f"Cette institution a encore des arriérés pour l'année {c.annee}. "
                        f"Veuillez d'abord encaisser ces arriérés avant de commencer les paiements pour {cotisation_annuelle.annee}."
                    )
                    return redirect('comptes:payer_institution', institution_id=institution.id)
            
            # Vérifier que le montant ne dépasse pas le reste à payer
            reste_a_payer = cotisation_annuelle.reste_a_payer()
            if montant_value > reste_a_payer:
                messages.error(
                    request,
                    f"Le montant ({montant_value:,.0f} FCFA) dépasse le reste à payer ({reste_a_payer:,.0f} FCFA)."
                )
                return redirect('comptes:payer_institution', institution_id=institution.id)
            
            # Créer le paiement annuel
            PaiementCotisationInstitution.objects.create(
                cotisation_annuelle=cotisation_annuelle,
                montant_paye=montant_value,
                encaisse_par_agent=agent,
                notes=notes,
            )
            
            messages.success(
                request,
                f"Paiement de {montant_value:,.0f} FCFA enregistré pour {institution.nom_institution} ({cotisation_annuelle.annee})."
            )
            return redirect('comptes:payer_institution', institution_id=institution.id)
            
        except CotisationAnnuelleInstitution.DoesNotExist:
            messages.error(request, "Cotisation introuvable.")
            return redirect('comptes:espace_agent')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement du paiement: {str(e)}")
            return redirect('comptes:payer_institution', institution_id=institution.id)
    
    # Créer la cotisation de l'année courante si elle n'existe pas
    if not CotisationAnnuelleInstitution.objects.filter(institution=institution, annee=annee_courante).exists():
        # Le montant annuel doit être défini par l'admin, pour l'instant on utilise 0
        CotisationAnnuelleInstitution.objects.create(
            institution=institution,
            annee=annee_courante,
            montant_annuel_du=Decimal("0"),  # À définir par l'admin
        )
    
    cotisations_annuelles = CotisationAnnuelleInstitution.objects.filter(
        institution=institution
    ).order_by('-annee')
    
    context = {
        'agent': agent,
        'institution': institution,
        'cotisations_annuelles': cotisations_annuelles,
        'annee_courante': annee_courante,
    }
    
    return render(request, 'comptes/payer_institution.html', context)
