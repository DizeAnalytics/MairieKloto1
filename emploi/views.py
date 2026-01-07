from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from .forms import (
    ProfilJeuneForm, 
    ProfilRetraiteForm,
    ProfilJeuneEditForm,
    ProfilRetraiteEditForm
)
from .models import ProfilEmploi


@require_http_methods(["GET", "POST"])
def inscription_jeune(request):
    """Inscription des jeunes en quête d'emploi."""

    if request.method == "POST":
        form = ProfilJeuneForm(request.POST, user=request.user)
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
            
            profil = form.save(commit=False)
            profil.type_profil = "jeune"
            profil.user = user
            profil.save()
            
            messages.success(request, "Inscription réussie ! Bienvenue dans votre espace.")
            return redirect('comptes:profil')
    else:
        form = ProfilJeuneForm(user=request.user)

    context = {
        "form": form,
        "type_profil_label": "Jeunes demandeurs d'emploi",
    }
    return render(request, "emploi/inscription-jeunes.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def modifier_jeune(request):
    """Modification du profil des jeunes en quête d'emploi."""
    
    # Vérifier si l'utilisateur a un profil emploi de type 'jeune'
    if not hasattr(request.user, 'profil_emploi') or request.user.profil_emploi.type_profil != 'jeune':
        messages.error(request, "Vous n'avez pas de profil Jeune Demandeur d'Emploi.")
        return redirect('comptes:profil')
        
    profil = request.user.profil_emploi
    
    if request.method == "POST":
        form = ProfilJeuneEditForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été mises à jour avec succès.")
            return redirect('comptes:profil')
    else:
        form = ProfilJeuneEditForm(instance=profil)
        
    context = {
        "form": form,
        "type_profil_label": "Jeunes demandeurs d'emploi",
        "is_edit": True,
    }
    return render(request, "emploi/modifier_jeune.html", context)


@require_http_methods(["GET", "POST"])
def inscription_retraite(request):
    """Inscription des retraités valides cherchant une activité."""

    if request.method == "POST":
        form = ProfilRetraiteForm(request.POST, user=request.user)
        if form.is_valid():
            if request.user.is_authenticated:
                user = request.user
            else:
                # Vérifier si l'email existe déjà comme username
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                
                if User.objects.filter(username=email).exists():
                    messages.error(request, "Un compte avec cet email existe déjà.")
                    context = {
                        "form": form,
                        "type_profil_label": "Retraités actifs",
                    }
                    return render(request, "emploi/inscription-retraites.html", context)
                else:
                    # Créer l'utilisateur
                    user = User.objects.create_user(username=email, email=email, password=password)
                    # Connecter l'utilisateur
                    login(request, user, backend='mairie_kloto_platform.backends.EmailOrUsernameBackend')
            
            profil = form.save(commit=False)
            profil.type_profil = "retraite"
            profil.user = user
            profil.save()
            
            messages.success(request, "Inscription réussie ! Bienvenue dans votre espace.")
            return redirect('comptes:profil')
    else:
        form = ProfilRetraiteForm(user=request.user)

    context = {
        "form": form,
        "type_profil_label": "Retraités actifs",
    }
    return render(request, "emploi/inscription-retraites.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def modifier_retraite(request):
    """Modification du profil des retraités actifs."""
    
    # Vérifier si l'utilisateur a un profil emploi de type 'retraite'
    if not hasattr(request.user, 'profil_emploi') or request.user.profil_emploi.type_profil != 'retraite':
        messages.error(request, "Vous n'avez pas de profil Retraité Actif.")
        return redirect('comptes:profil')
        
    profil = request.user.profil_emploi
    
    if request.method == "POST":
        form = ProfilRetraiteEditForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été mises à jour avec succès.")
            return redirect('comptes:profil')
    else:
        form = ProfilRetraiteEditForm(instance=profil)
        
    context = {
        "form": form,
        "type_profil_label": "Retraités actifs",
        "is_edit": True,
    }
    return render(request, "emploi/modifier_retraite.html", context)


@login_required
def generer_pdf_jeune(request):
    """Génère un PDF modèle pour l'inscription des jeunes demandeurs d'emploi."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="modele_jeunes_demandeurs_emploi.pdf"'

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
    story.append(Paragraph("INSCRIPTION DES JEUNES DEMANDEURS D'EMPLOI", title_style))
    story.append(Paragraph("Mairie de Kloto 1 - Plateforme Emploi & Compétences", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Section 1: Informations personnelles
    story.append(Paragraph("1. INFORMATIONS PERSONNELLES", section_style))

    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
        wordWrap="CJK",
    )

    sexe_opts = "<br/>".join(["Masculin", "Féminin", "Autre"])

    data = [
        [Paragraph("<b>Nom</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Prénoms</b>", cell_style), Paragraph("_________________________", cell_style)],
        [
            Paragraph("<b>Sexe</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + sexe_opts, cell_style),
        ],
        [Paragraph("<b>Date de naissance</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Nationalité</b>", cell_style), Paragraph("_________________________", cell_style)],
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
        [Paragraph("<b>Téléphone principal</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Téléphone secondaire</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Email</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Quartier</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Canton</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Adresse complète</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Résident de Kloto 1 ?</b>", cell_style), Paragraph("☐ Oui   ☐ Non", cell_style)],
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

    # Section 3: Profil professionnel
    story.append(Paragraph("3. PROFIL PROFESSIONNEL", section_style))
    story.append(Paragraph("Veuillez joindre votre CV si possible.", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))
    
    data = [
        [Paragraph("<b>Niveau d'étude</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Diplôme principal</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Domaine de compétence</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Disponibilité</b>", cell_style), Paragraph("_________________________", cell_style)],
    ]
    
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
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
def generer_pdf_retraite(request):
    """Génère un PDF modèle pour l'inscription des retraités."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="modele_retraites_actifs.pdf"'

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

    # Titre
    story.append(Paragraph("INSCRIPTION DES RETRAITÉS ACTIFS", title_style))
    story.append(Paragraph("Mairie de Kloto 1 - Plateforme Emploi & Compétences", styles["Normal"]))
    
    # ... Contenu similaire à adapter ...
    
    doc.build(story)
    return response
