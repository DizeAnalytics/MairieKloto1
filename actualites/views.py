from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from .models import Actualite, CommentaireActualite
from .forms import CommentaireActualiteForm


def liste_actualites(request):
    """Affiche la liste des 3 dernières actualités publiées."""

    actualites = Actualite.objects.filter(est_publie=True).order_by("-date_publication")[:3]

    context = {
        "actualites": actualites,
    }

    return render(request, "actualites/liste.html", context)


def detail_actualite(request, pk):
    """Affiche le détail d'une actualité et gère les commentaires."""

    actualite = get_object_or_404(Actualite, pk=pk, est_publie=True)

    # Récupérer les actualités récentes pour la sidebar
    actualites_recentes = (
        Actualite.objects.filter(est_publie=True)
        .exclude(pk=pk)
        .order_by("-date_publication")[:5]
    )

    # Commentaires déjà publiés
    commentaires = CommentaireActualite.objects.filter(
        actualite=actualite,
        est_valide=True,
    ).select_related("utilisateur")

    # Les commentaires sont réservés aux utilisateurs connectés
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Vous devez être connecté pour laisser un commentaire.")
            login_url = reverse("comptes:connexion")
            return redirect(f"{login_url}?next={request.path}")

        form = CommentaireActualiteForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.actualite = actualite
            commentaire.utilisateur = request.user
            # Nom et e-mail issus du compte de l'utilisateur connecté
            commentaire.nom = request.user.get_full_name() or request.user.username
            commentaire.email = getattr(request.user, "email", "") or ""
            commentaire.save()
            messages.success(request, "Votre commentaire a été enregistré avec succès.")
            return redirect(reverse("actualites:detail", args=[actualite.pk]))
        else:
            messages.error(
                request,
                "Veuillez corriger les erreurs dans le formulaire de commentaire.",
            )
    else:
        if request.user.is_authenticated:
            initial = {
                "nom": request.user.get_full_name() or request.user.username,
                "email": getattr(request.user, "email", "") or "",
            }
            form = CommentaireActualiteForm(initial=initial)
        else:
            form = CommentaireActualiteForm()

    context = {
        "actualite": actualite,
        "actualites_recentes": actualites_recentes,
        "commentaires": commentaires,
        "form_commentaire": form,
    }

    return render(request, "actualites/detail.html", context)

