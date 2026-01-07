from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from .forms import (
    ActeurEconomiqueForm, 
    InstitutionFinanciereForm, 
    SiteTouristiqueForm,
    ActeurEconomiqueEditForm,
    InstitutionFinanciereEditForm
)
from .models import ActeurEconomique, InstitutionFinanciere, SiteTouristique


@require_http_methods(["GET", "POST"])
def enregistrer_acteur(request):
    """Affiche le formulaire d’enregistrement des acteurs économiques."""

    if request.method == "POST":
        form = ActeurEconomiqueForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            if request.user.is_authenticated:
                user = request.user
            else:
                # Récupérer les données
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                
                # Créer l'utilisateur
                user = User.objects.create_user(username=username, email=email, password=password)
                # Connecter l'utilisateur
                login(request, user, backend='mairie_kloto_platform.backends.EmailOrUsernameBackend')
            
            # Créer l'acteur économique lié
            acteur = form.save(commit=False)
            acteur.user = user
            acteur.save()
            
            messages.success(request, "Inscription réussie ! Bienvenue dans votre espace.")
            return redirect('comptes:profil')
    else:
        form = ActeurEconomiqueForm(user=request.user)

    context = {
        "form": form,
    }
    return render(request, "acteurs/enregistrement-acteurs.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def modifier_acteur(request):
    """Permet à un acteur économique de modifier ses informations."""
    
    # Vérifier si l'utilisateur a un profil acteur
    if not hasattr(request.user, 'acteur_economique'):
        messages.error(request, "Vous n'avez pas de profil Acteur Économique.")
        return redirect('comptes:profil')
        
    acteur = request.user.acteur_economique
    
    if request.method == "POST":
        form = ActeurEconomiqueEditForm(request.POST, request.FILES, instance=acteur)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été mises à jour avec succès.")
            return redirect('comptes:profil')
    else:
        form = ActeurEconomiqueEditForm(instance=acteur)
        
    context = {
        "form": form,
        "is_edit": True,
    }
    return render(request, "acteurs/modifier_acteur.html", context)




@require_http_methods(["GET", "POST"])
def inscrire_institution_financiere(request):
    """Formulaire d’inscription des institutions financières."""

    if request.method == "POST":
        form = InstitutionFinanciereForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            if request.user.is_authenticated:
                user = request.user
            else:
                # Récupérer les données
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                
                # Créer l'utilisateur
                user = User.objects.create_user(username=username, email=email, password=password)
                
                # Connecter l'utilisateur
                login(request, user, backend='mairie_kloto_platform.backends.EmailOrUsernameBackend')
            
            # Créer l'institution liée
            institution = form.save(commit=False)
            institution.user = user
            institution.save()
            
            messages.success(request, "Inscription réussie ! Bienvenue dans votre espace.")
            return redirect('comptes:profil')
    else:
        form = InstitutionFinanciereForm(user=request.user)

    context = {
        "form": form,
    }
    return render(request, "acteurs/inscription-institutions.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def modifier_institution(request):
    """Permet à une institution financière de modifier ses informations."""
    
    # Vérifier si l'utilisateur a un profil institution
    if not hasattr(request.user, 'institution_financiere'):
        messages.error(request, "Vous n'avez pas de profil Institution Financière.")
        return redirect('comptes:profil')
        
    institution = request.user.institution_financiere
    
    if request.method == "POST":
        form = InstitutionFinanciereEditForm(request.POST, request.FILES, instance=institution)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été mises à jour avec succès.")
            return redirect('comptes:profil')
    else:
        form = InstitutionFinanciereEditForm(instance=institution)
        
    context = {
        "form": form,
        "is_edit": True,
    }
    return render(request, "acteurs/modifier_institution.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def enregistrer_site_touristique(request):
    success = False
    if request.method == "POST":
        form = SiteTouristiqueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            success = True
            form = SiteTouristiqueForm()
    else:
        form = SiteTouristiqueForm()
    sites = SiteTouristique.objects.all()
    context = {
        "form": form,
        "success": success,
        "sites": sites,
    }
    return render(request, "acteurs/enregistrement-sites.html", context)

def liste_sites_touristiques(request):
    sites = SiteTouristique.objects.filter(est_valide_par_mairie=True).order_by("nom_site")
    context = {
        "sites": sites,
    }
    return render(request, "acteurs/liste-sites.html", context)

def site_detail(request, pk: int):
    site = get_object_or_404(SiteTouristique, pk=pk, est_valide_par_mairie=True)
    autres_sites = SiteTouristique.objects.filter(est_valide_par_mairie=True).exclude(pk=pk).order_by("nom_site")[:6]
    context = {
        "site": site,
        "autres_sites": autres_sites,
    }
    return render(request, "acteurs/detail-site.html", context)

@login_required
def generer_pdf_acteur(request):
    """Génère un PDF modèle pour l'enregistrement des acteurs économiques."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="modele_acteurs_economiques.pdf"'

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

    # Style pour les champs
    field_style = ParagraphStyle(
        "FieldStyle",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=8,
        leftIndent=20,
    )

    # Titre
    story.append(Paragraph("ENREGISTREMENT DES ACTEURS ÉCONOMIQUES", title_style))
    story.append(Paragraph("Mairie de Kloto 1 - Kpalimé, Région des Plateaux, Togo", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Section 1: Informations de base
    story.append(Paragraph("1. INFORMATIONS DE BASE", section_style))

    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
        wordWrap="CJK",
    )

    type_acteur_opts = "<br/>".join(
        [
            "Entreprise",
            "Commerce",
            "Artisan",
            "PME",
            "PMI",
            "ONG",
            "Association",
            "Autre",
        ]
    )
    secteur_opts = "<br/>".join(
        [
            "Commerce général",
            "Artisanat",
            "Services",
            "Industrie",
            "Agriculture",
            "Bâtiment et Travaux Publics",
            "Transport",
            "Technologie et Informatique",
        ]
    )

    data = [
        [Paragraph("<b>Raison sociale / Nom</b>", cell_style), Paragraph("_________________________", cell_style)],
        [
            Paragraph("<b>Type d'acteur</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + type_acteur_opts, cell_style),
        ],
        [
            Paragraph("<b>Secteur d'activité</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + secteur_opts, cell_style),
        ],
        [Paragraph("<b>Date de création</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>N° RCCM</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>N° CFE</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>N° Carte Opérateur</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>NIF</b>", cell_style), Paragraph("_________________________", cell_style)],
    ]

    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    # Section 2: Coordonnées
    story.append(Paragraph("2. COORDONNÉES", section_style))
    
    data = [
        [Paragraph("<b>Nom du responsable</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Téléphone 1</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Téléphone 2</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Email</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Quartier</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Canton</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Adresse complète</b>", cell_style), Paragraph("_________________________", cell_style)],
    ]

    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    
    # Pied de page
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("Je certifie que les informations ci-dessus sont exactes.", styles["Normal"]))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("Date et Signature : _________________________", styles["Normal"]))

    doc.build(story)
    return response


@login_required
def generer_pdf_institution(request):
    """Génère un PDF modèle pour l'inscription des institutions financières."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="modele_institutions_financieres.pdf"'

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
        alignment=1,
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

    # Titre
    story.append(Paragraph("INSCRIPTION DES INSTITUTIONS FINANCIÈRES", title_style))
    story.append(Paragraph("Mairie de Kloto 1 - Kpalimé, Région des Plateaux, Togo", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Section 1: Informations de l'institution
    story.append(Paragraph("1. INFORMATIONS DE L'INSTITUTION", section_style))

    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
        wordWrap="CJK",
    )

    type_inst_opts = "<br/>".join(
        [
            "Banque",
            "Microfinance",
            "Assurance",
            "Coopérative",
            "Autre",
        ]
    )

    data = [
        [Paragraph("<b>Nom de l'institution</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Sigle</b>", cell_style), Paragraph("_________________________", cell_style)],
        [
            Paragraph("<b>Type d'institution</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + type_inst_opts, cell_style),
        ],
        [Paragraph("<b>Année de création</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>N° Agrément</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>IFU</b>", cell_style), Paragraph("_________________________", cell_style)],
    ]

    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    # Section 2: Services et Coordonnées
    story.append(Paragraph("2. SERVICES ET COORDONNÉES", section_style))
    
    data = [
        [Paragraph("<b>Nom du responsable</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Téléphone 1</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Email</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Quartier / Adresse</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Services principaux</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Conditions d'éligibilité</b>", cell_style), Paragraph("_________________________", cell_style)],
    ]

    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    
    doc.build(story)
    return response
