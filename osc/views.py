from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods

from .forms import OrganisationSocieteCivileForm
from .models import OrganisationSocieteCivile


@require_http_methods(["GET", "POST"])
def inscription_osc(request):
    """Enregistrement des Organisations de la Société Civile (OSC)."""

    if request.method == "POST":
        form = OrganisationSocieteCivileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Gestion de l'utilisateur
            if request.user.is_authenticated:
                user = request.user
            else:
                username = form.cleaned_data.get("username")
                email = form.cleaned_data.get("email")
                password = form.cleaned_data.get("password")

                if not username or not password:
                    messages.error(
                        request,
                        "Veuillez renseigner un nom d'utilisateur et un mot de passe pour créer votre compte.",
                    )
                    return render(
                        request,
                        "osc/inscription.html",
                        {"form": form, "titre": "Enregistrement des OSC"},
                    )

                if User.objects.filter(username=username).exists():
                    messages.error(request, "Un compte avec ce nom d'utilisateur existe déjà.")
                    return render(
                        request,
                        "osc/inscription.html",
                        {"form": form, "titre": "Enregistrement des OSC"},
                    )

                user = User.objects.create_user(username=username, email=email, password=password)
                login(request, user, backend="mairie_kloto_platform.backends.EmailOrUsernameBackend")

            osc = form.save(commit=False)
            osc.user = user

            # Récupération des domaines d'intervention depuis les champs dynamiques
            secteurs = request.POST.getlist("sector[]")
            secteurs_valides = [s.strip() for s in secteurs if s.strip()]
            osc.domaines_intervention = "\n".join(secteurs_valides)

            # Récupération des membres / responsables
            noms_membres = request.POST.getlist("member_nom[]")
            fonctions_membres = request.POST.getlist("member_fonction[]")
            lignes_membres = []
            for nom, fonction in zip(noms_membres, fonctions_membres):
                if nom.strip() or fonction.strip():
                    lignes_membres.append(f"{nom.strip()} - {fonction.strip()}")
            osc.membres_responsables = "\n".join(lignes_membres)

            osc.save()

            messages.success(
                request,
                "Votre organisation de la société civile a été enregistrée avec succès. "
                "Elle sera examinée par les services de la mairie.",
            )
            return redirect("comptes:profil")
    else:
        form = OrganisationSocieteCivileForm(user=request.user)

    context = {
        "form": form,
        "titre": "Enregistrement des OSC",
        "secteurs": [],
        "membres": [],
    }
    return render(request, "osc/inscription.html", context)


@login_required
def liste_osc(request):
    """Liste simple des OSC associées à l'utilisateur connecté."""
    organisations = OrganisationSocieteCivile.objects.filter(user=request.user).order_by("-date_enregistrement")
    return render(
        request,
        "osc/liste.html",
        {
            "organisations": organisations,
            "titre": "Mes Organisations de la Société Civile",
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def modifier_osc(request, pk):
    """
    Permet de modifier une OSC existante appartenant à l'utilisateur connecté.
    """
    osc = get_object_or_404(OrganisationSocieteCivile, pk=pk, user=request.user)

    if request.method == "POST":
        form = OrganisationSocieteCivileForm(request.POST, request.FILES, instance=osc, user=request.user)
        if form.is_valid():
            osc = form.save(commit=False)

            # Mettre à jour les domaines d'intervention depuis les champs dynamiques
            secteurs = request.POST.getlist("sector[]")
            secteurs_valides = [s.strip() for s in secteurs if s.strip()]
            osc.domaines_intervention = "\n".join(secteurs_valides)

            # Mettre à jour les membres / responsables
            noms_membres = request.POST.getlist("member_nom[]")
            fonctions_membres = request.POST.getlist("member_fonction[]")
            lignes_membres = []
            for nom, fonction in zip(noms_membres, fonctions_membres):
                if nom.strip() or fonction.strip():
                    lignes_membres.append(f"{nom.strip()} - {fonction.strip()}")
            osc.membres_responsables = "\n".join(lignes_membres)

            osc.save()
            messages.success(request, "Votre organisation a été mise à jour avec succès.")
            return redirect("comptes:profil")
    else:
        form = OrganisationSocieteCivileForm(instance=osc, user=request.user)

    # Pré-remplir les champs dynamiques pour le template
    secteurs = osc.domaines_intervention.splitlines() if osc.domaines_intervention else []
    membres = osc.membres_responsables.splitlines() if osc.membres_responsables else []

    context = {
        "form": form,
        "titre": "Modification de l'OSC",
        "osc": osc,
        "secteurs": secteurs,
        "membres": membres,
    }
    return render(request, "osc/inscription.html", context)

