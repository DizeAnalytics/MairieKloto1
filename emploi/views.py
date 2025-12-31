from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from .forms import ProfilJeuneForm, ProfilRetraiteForm
from .models import ProfilEmploi


@login_required
@require_http_methods(["GET", "POST"])
def inscription_jeune(request):
    """Inscription des jeunes en quête d'emploi."""

    success = False

    if request.method == "POST":
        form = ProfilJeuneForm(request.POST)
        if form.is_valid():
            profil = form.save(commit=False)
            profil.type_profil = "jeune"
            profil.save()
            success = True
            form = ProfilJeuneForm()
    else:
        form = ProfilJeuneForm()

    profils = ProfilEmploi.objects.filter(type_profil="jeune")

    context = {
        "form": form,
        "success": success,
        "profils": profils,
        "type_profil_label": "Jeunes demandeurs d'emploi",
    }
    return render(request, "emploi/inscription-jeunes.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def inscription_retraite(request):
    """Inscription des retraités valides cherchant une activité."""

    success = False

    if request.method == "POST":
        form = ProfilRetraiteForm(request.POST)
        if form.is_valid():
            profil = form.save(commit=False)
            profil.type_profil = "retraite"
            profil.save()
            success = True
            form = ProfilRetraiteForm()
    else:
        form = ProfilRetraiteForm()

    profils = ProfilEmploi.objects.filter(type_profil="retraite")

    context = {
        "form": form,
        "success": success,
        "profils": profils,
        "type_profil_label": "Retraités actifs",
    }
    return render(request, "emploi/inscription-retraites.html", context)


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
    
    niveau_opts = "<br/>".join(
        [
            "Aucun diplôme formel",
            "CEP",
            "BEPC",
            "BAC",
            "BTS / DUT",
            "Licence",
            "Master",
            "Doctorat",
            "Autre",
        ]
    )
    situation_opts = "<br/>".join(["Sans emploi", "En emploi", "Étudiant", "Autre"])
    dispo_opts = "<br/>".join(["Immédiate", "Sous 1 mois", "Sous 3 mois", "Autre"])
    contrat_opts = "<br/>".join(["CDI", "CDD", "Stage", "Mission / Temps partiel", "Bénévolat"])

    data = [
        [
            Paragraph("<b>Niveau d'études</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + niveau_opts, cell_style),
        ],
        [Paragraph("<b>Diplôme principal</b>", cell_style), Paragraph("_________________________", cell_style)],
        [
            Paragraph("<b>Situation actuelle</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + situation_opts, cell_style),
        ],
        [Paragraph("<b>Employeur actuel (si applicable)</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Domaines de compétences</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Expériences professionnelles</b>", cell_style), Paragraph("_________________________", cell_style)],
        [
            Paragraph("<b>Disponibilité</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + dispo_opts, cell_style),
        ],
        [
            Paragraph("<b>Type de contrat souhaité</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + contrat_opts, cell_style),
        ],
        [Paragraph("<b>Salaire souhaité (facultatif)</b>", cell_style), Paragraph("_________________________", cell_style)],
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
    story.append(Spacer(1, 0.5 * cm))

    # Autorisations
    story.append(Paragraph("AUTORISATIONS", section_style))
    field_style = ParagraphStyle(
        "FieldStyle",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=8,
        leftIndent=20,
    )
    story.append(Paragraph("☐ J'accepte que mes données soient traitées par la Mairie de Kloto 1", field_style))
    story.append(Paragraph("☐ J'accepte d'être contacté par des employeurs via la plateforme", field_style))

    doc.build(story)
    return response


@login_required
def generer_pdf_retraite(request):
    """Génère un PDF modèle pour l'inscription des retraités actifs."""
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
    story.append(Paragraph("INSCRIPTION DES RETRAITÉS ACTIFS", title_style))
    story.append(Paragraph("Mairie de Kloto 1 - Valorisation des compétences des retraités", styles["Normal"]))
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

    # Section 3: Parcours professionnel
    story.append(Paragraph("3. PARCOURS PROFESSIONNEL", section_style))
    
    niveau_opts = "<br/>".join(
        [
            "Aucun diplôme formel",
            "CEP",
            "BEPC",
            "BAC",
            "BTS / DUT",
            "Licence",
            "Master",
            "Doctorat",
            "Autre",
        ]
    )

    data = [
        [
            Paragraph("<b>Niveau d'études</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + niveau_opts, cell_style),
        ],
        [Paragraph("<b>Diplôme principal</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Situation actuelle</b>", cell_style), Paragraph("Retraité", cell_style)],
        [Paragraph("<b>Dernier employeur</b>", cell_style), Paragraph("_________________________", cell_style)],
        [
            Paragraph("<b>Caisse de retraite / régime de pension</b>", cell_style),
            Paragraph("_________________________", cell_style),
        ],
        [
            Paragraph("<b>Métiers / domaines d'expertise</b>", cell_style),
            Paragraph("_________________________", cell_style),
        ],
        [
            Paragraph("<b>Résumé des expériences majeures</b>", cell_style),
            Paragraph("_________________________", cell_style),
        ],
        [Paragraph("<b>Dernier poste occupé</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Années d'expérience</b>", cell_style), Paragraph("_________________________", cell_style)],
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

    # Section 4: Disponibilités
    story.append(Paragraph("4. DISPONIBILITÉS", section_style))
    
    dispo_opts = "<br/>".join(["Immédiate", "Sous 1 mois", "Sous 3 mois", "Autre"])
    contrat_opts = "<br/>".join(["CDI", "CDD", "Stage", "Mission / Temps partiel", "Bénévolat"])

    data = [
        [
            Paragraph("<b>Disponibilité</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + dispo_opts, cell_style),
        ],
        [
            Paragraph("<b>Type d'engagement souhaité</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + contrat_opts, cell_style),
        ],
        [
            Paragraph("<b>Indemnité / rémunération souhaitée (facultatif)</b>", cell_style),
            Paragraph("_________________________", cell_style),
        ],
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
    story.append(Spacer(1, 0.5 * cm))

    # Autorisations
    story.append(Paragraph("AUTORISATIONS", section_style))
    field_style = ParagraphStyle(
        "FieldStyle",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=8,
        leftIndent=20,
    )
    story.append(Paragraph("☐ J'accepte que mes données soient traitées par la Mairie de Kloto 1", field_style))
    story.append(Paragraph("☐ J'accepte d'être contacté par des structures via la plateforme", field_style))

    doc.build(story)
    return response

