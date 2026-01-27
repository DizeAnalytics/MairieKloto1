from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from .models import (
    MotMaire,
    Collaborateur,
    InformationMairie,
    EtatCivilPage,
    AppelOffre,
    Candidature,
    ImageCarousel,
    Publicite,
    Projet,
    Suggestion,
    DonMairie,
    ConfigurationMairie,
)
from .forms import CandidatureForm, SuggestionForm
from acteurs.models import ActeurEconomique, InstitutionFinanciere
from emploi.models import ProfilEmploi


def accueil(request):
    """Page d'accueil avec le mot du maire, collaborateurs et informations."""
    import random
    
    mot_maire = MotMaire.objects.filter(est_actif=True).first()
    collaborateurs = Collaborateur.objects.filter(est_visible=True).order_by('ordre_affichage', 'fonction', 'nom')
    informations = InformationMairie.objects.filter(est_visible=True).order_by('ordre_affichage', 'type_info')
    
    # Récupérer les images actives du carousel (max 5) et les mélanger aléatoirement
    images_carousel = list(ImageCarousel.objects.filter(est_actif=True).order_by('ordre_affichage', '-date_creation')[:5])
    random.shuffle(images_carousel)

    context = {
        'mot_maire': mot_maire,
        'collaborateurs': collaborateurs,
        'informations': informations,
        'images_carousel': images_carousel,
    }
    
    return render(request, 'mairie/accueil.html', context)


def etat_civil(request):
    """Page listant toutes les démarches d'état civil (actes de naissance, mariage, décès, etc.)."""

    rubriques = EtatCivilPage.objects.filter(est_visible=True).order_by("ordre_affichage", "titre")

    context = {
        "rubriques": rubriques,
    }
    return render(request, "mairie/etat_civil.html", context)


def contactez_nous(request):
    """Page de contact avec formulaire de suggestion et section pour faire un don."""

    # Les informations principales (adresse, téléphone, email, horaires)
    # viennent de ConfigurationMairie via le context processor `mairie_config`.
    # Ici on se contente d'afficher une belle page de synthèse.
    informations_contact = InformationMairie.objects.filter(
        type_info__in=["contact", "adresse", "horaire"]
    ).order_by("ordre_affichage", "type_info")
    
    # Récupérer la configuration de la mairie pour les numéros de compte
    mairie_config = ConfigurationMairie.objects.filter(est_active=True).first()

    # Gestion du formulaire de suggestion
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save()
            messages.success(
                request,
                "Votre suggestion a été envoyée avec succès ! Nous vous remercions pour votre contribution."
            )
            # Rediriger pour éviter la double soumission
            return redirect('mairie:contactez_nous')
        else:
            messages.error(
                request,
                "Une erreur s'est produite lors de l'envoi de votre suggestion. Veuillez vérifier les informations saisies."
            )
    else:
        form = SuggestionForm()

    context = {
        "informations_contact": informations_contact,
        "form_suggestion": form,
        "mairie_config": mairie_config,
    }
    return render(request, "mairie/contactez_nous.html", context)


def liste_appels_offres(request):
    """Page listant tous les appels d'offres publiés et ouverts."""
    
    maintenant = timezone.now()
    
    # Récupérer uniquement les appels d'offres publiés sur le site
    # et dont la date de fin n'est pas encore dépassée
    appels_offres = AppelOffre.objects.filter(
        est_publie_sur_site=True,
        statut='publie',
        date_fin__gte=maintenant  # Seulement ceux qui ne sont pas encore expirés
    ).order_by('-date_debut', '-date_creation')
    
    # Les appels clôturés ne sont plus affichés automatiquement
    # Mais on peut garder une logique pour afficher ceux qui sont manuellement clôturés
    # et dont la date n'est pas encore dépassée (pour information)
    appels_clotures = AppelOffre.objects.filter(
        est_publie_sur_site=True,
        statut='cloture',
        date_fin__gte=maintenant  # Encore visibles même si statut = clôturé
    ).order_by('-date_debut', '-date_creation')
    
    context = {
        'appels_ouverts': appels_offres,
        'appels_clotures': appels_clotures,
    }
    
    return render(request, 'mairie/appels_offres.html', context)


@login_required
def detail_appel_offre(request, pk: int):
    """Page de détail d'un appel d'offres, avec toutes les informations avant candidature."""

    appel = get_object_or_404(
        AppelOffre,
        pk=pk,
        est_publie_sur_site=True,
    )

    maintenant = timezone.now()
    # Un appel est ouvert si :
    # 1. Il est publié sur le site (est_publie_sur_site=True)
    # 2. Le statut est "publie" (ou "cloture" mais pas encore expiré)
    # 3. La date actuelle est entre date_debut et date_fin
    # Note: Si est_publie_sur_site=True, on considère l'appel comme ouvert si les dates sont valides,
    # même si le statut n'est pas exactement "publie" (mais pas "archive" ou "brouillon")
    est_ouvert = (
        appel.est_publie_sur_site
        and appel.statut in ["publie", "cloture"]  # Permettre aussi "cloture" si pas encore expiré
        and appel.date_debut <= maintenant <= appel.date_fin
    )
    
    # Déterminer la raison pour laquelle l'appel est fermé (pour debug/admin)
    raison_fermeture = None
    if not est_ouvert:
        if not appel.est_publie_sur_site:
            raison_fermeture = "L'appel d'offres n'est pas publié sur le site."
        elif appel.statut not in ["publie", "cloture"]:
            raison_fermeture = f"Le statut est '{appel.get_statut_display()}' (doit être 'Publié' ou 'Clôturé')."
        elif maintenant < appel.date_debut:
            raison_fermeture = f"L'appel d'offres n'a pas encore commencé. Il débutera le {appel.date_debut.strftime('%d/%m/%Y à %H:%M')}."
        elif maintenant > appel.date_fin:
            raison_fermeture = f"L'appel d'offres est terminé depuis le {appel.date_fin.strftime('%d/%m/%Y à %H:%M')}."
    
    # Vérifier si l'utilisateur a un profil (acteur économique, institution financière, jeune ou retraité)
    # Vérification directe dans la base de données pour éviter les exceptions RelatedObjectDoesNotExist
    has_profile = (
        ActeurEconomique.objects.filter(user=request.user).exists() or
        InstitutionFinanciere.objects.filter(user=request.user).exists() or
        ProfilEmploi.objects.filter(user=request.user).exists()
    )

    context = {
        "appel": appel,
        "est_ouvert": est_ouvert,
        "has_profile": has_profile,
        "raison_fermeture": raison_fermeture,
        "maintenant": maintenant,
    }
    return render(request, "mairie/appel_offre_detail.html", context)


@login_required
def generer_pdf_appel_offre(request, pk: int):
    """Génère un PDF pour un appel d'offres spécifique."""
    appel = get_object_or_404(
        AppelOffre,
        pk=pk,
        est_publie_sur_site=True,
    )

    response = HttpResponse(content_type="application/pdf")
    filename = f"appel_offres_{appel.reference or appel.pk}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Style pour le titre
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#006233"),
        spaceAfter=30,
        alignment=1,  # Centré
    )

    # Style pour les sections
    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#006233"),
        spaceAfter=12,
        spaceBefore=20,
    )

    # Style pour les cellules de table
    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
        wordWrap="CJK",
    )

    # Titre
    story.append(Paragraph("APPEL D'OFFRES", title_style))
    story.append(Paragraph("Mairie de Kloto 1 - Kpalimé, Région des Plateaux, Togo", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Informations générales
    story.append(Paragraph("1. INFORMATIONS GÉNÉRALES", section_style))

    data = [
        [Paragraph("<b>Titre</b>", cell_style), Paragraph(appel.titre, cell_style)],
        [Paragraph("<b>Référence</b>", cell_style), Paragraph(appel.reference or "Non renseignée", cell_style)],
        [Paragraph("<b>Public cible</b>", cell_style), Paragraph(appel.get_public_cible_display(), cell_style)],
        [Paragraph("<b>Date d'ouverture</b>", cell_style), Paragraph(appel.date_debut.strftime("%d/%m/%Y à %H:%M"), cell_style)],
        [Paragraph("<b>Date de clôture</b>", cell_style), Paragraph(appel.date_fin.strftime("%d/%m/%Y à %H:%M"), cell_style)],
    ]

    if appel.budget_estime:
        data.append([Paragraph("<b>Budget estimé</b>", cell_style), Paragraph(f"{appel.budget_estime:,.0f} FCFA", cell_style)])

    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    # Description
    story.append(Paragraph("2. DESCRIPTION DE L'APPEL D'OFFRES", section_style))
    story.append(Paragraph(appel.description, styles["Normal"]))
    story.append(Spacer(1, 0.3 * cm))

    # Critères de sélection
    if appel.criteres_selection:
        story.append(Paragraph("3. CRITÈRES DE SÉLECTION", section_style))
        story.append(Paragraph(appel.criteres_selection.replace("\n", "<br/>"), styles["Normal"]))
        story.append(Spacer(1, 0.3 * cm))

    # Dossier de candidature
    if appel.dossier_candidature:
        story.append(Paragraph("4. DOSSIER DE CANDIDATURE À FOURNIR", section_style))
        story.append(Paragraph(appel.dossier_candidature.replace("\n", "<br/>"), styles["Normal"]))
        story.append(Spacer(1, 0.3 * cm))

    # Statut
    story.append(Paragraph("5. STATUT", section_style))
    maintenant = timezone.now()
    if appel.date_fin >= maintenant and appel.statut == 'publie':
        statut_text = "Ouvert - Candidatures acceptées jusqu'au " + appel.date_fin.strftime("%d/%m/%Y à %H:%M")
    else:
        statut_text = "Clôturé"
    
    story.append(Paragraph(statut_text, styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Note finale
    story.append(Paragraph("Pour plus d'informations, consultez la plateforme web de la Mairie de Kloto 1.", styles["Normal"]))

    doc.build(story)
    return response


@login_required
def soumettre_candidature(request, pk: int):
    """Permet à un utilisateur de soumettre une candidature pour un appel d'offres."""
    appel = get_object_or_404(AppelOffre, pk=pk, est_publie_sur_site=True)
    
    # Récupérer les profils éventuels de l'utilisateur
    acteur = ActeurEconomique.objects.filter(user=request.user).first()
    institution = InstitutionFinanciere.objects.filter(user=request.user).first()
    profil_emploi = ProfilEmploi.objects.filter(user=request.user).first()

    # Vérifier si l'utilisateur a AU MOINS un profil (acteur économique, institution financière, jeune ou retraité)
    has_profile = any([acteur, institution, profil_emploi])
    
    if not has_profile:
        messages.error(
            request, 
            "Vous devez d'abord remplir un formulaire d'inscription (Acteur économique, Institution financière, Jeune ou Retraité) avant de pouvoir postuler à un appel d'offres."
        )
        return redirect('mairie:appel_offre_detail', pk=pk)

    # Vérifier que le type de profil correspond au public cible de l'appel d'offres
    public = appel.public_cible
    autorise = False

    if public == "tous":
        autorise = True
    elif public == "entreprises":
        # Réservé aux acteurs économiques (entreprises / acteurs économiques)
        autorise = acteur is not None
    elif public == "institutions":
        # Réservé aux institutions financières
        autorise = institution is not None
    elif public == "entreprises_institutions":
        # Réservé aux acteurs économiques ET/OU institutions financières
        autorise = (acteur is not None) or (institution is not None)
    elif public == "jeunes":
        # Réservé aux profils emploi de type "jeune"
        autorise = profil_emploi is not None and profil_emploi.type_profil == "jeune"
    elif public == "retraites":
        # Réservé aux profils emploi de type "retraite"
        autorise = profil_emploi is not None and profil_emploi.type_profil == "retraite"

    if not autorise:
        messages.error(
            request,
            f"Cet appel d'offres est réservé au public suivant : {appel.get_public_cible_display()}. "
            "Votre type de profil ne correspond pas."
        )
        return redirect('mairie:appel_offre_detail', pk=pk)
    
    # Vérifier si l'appel est ouvert
    maintenant = timezone.now()
    if not (appel.statut == "publie" and appel.date_debut <= maintenant <= appel.date_fin):
        messages.error(request, "Cet appel d'offres n'est plus ouvert aux candidatures.")
        return redirect('mairie:appel_offre_detail', pk=pk)

    # Empêcher plusieurs candidatures du même utilisateur pour le même appel d'offres
    if Candidature.objects.filter(appel_offre=appel, candidat=request.user).exists():
        messages.warning(request, "Vous avez déjà soumis une candidature pour cet appel d'offres.")
        return redirect('mairie:appel_offre_detail', pk=pk)

    if request.method == 'POST':
        form = CandidatureForm(request.POST, request.FILES)
        if form.is_valid():
            candidature = form.save(commit=False)
            candidature.appel_offre = appel
            candidature.candidat = request.user
            candidature.save()
            messages.success(request, "Votre candidature a été soumise avec succès ! Vous recevrez une notification lors de son traitement.")
            return redirect('mairie:appel_offre_detail', pk=pk)
    else:
        form = CandidatureForm()

    context = {
        'appel': appel,
        'form': form,
    }
    return render(request, 'mairie/candidature_form.html', context)


def liste_projets(request):
    """Page listant tous les projets publiés de la mairie."""
    
    projets = Projet.objects.filter(est_visible=True).order_by('ordre_affichage', '-date_debut', '-date_creation')
    
    # Séparer les projets en cours et réalisés
    projets_en_cours = projets.filter(statut='en_cours')
    projets_realises = projets.filter(statut='realise')
    
    context = {
        'projets_en_cours': projets_en_cours,
        'projets_realises': projets_realises,
    }
    
    return render(request, 'mairie/projets.html', context)


def detail_projet(request, slug):
    """Page de détail d'un projet."""
    
    projet = get_object_or_404(
        Projet.objects.prefetch_related("photos"),
        slug=slug,
        est_visible=True
    )
    
    # Récupérer d'autres projets pour la section "À découvrir aussi"
    autres_projets = Projet.objects.filter(
        est_visible=True
    ).exclude(pk=projet.pk).order_by('ordre_affichage', '-date_debut')[:6]
    
    context = {
        'projet': projet,
        'autres_projets': autres_projets,
    }
    
    return render(request, 'mairie/projet_detail.html', context)

