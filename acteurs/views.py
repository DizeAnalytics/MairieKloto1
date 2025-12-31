from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from .forms import ActeurEconomiqueForm, InstitutionFinanciereForm, SiteTouristiqueForm
from .models import ActeurEconomique, InstitutionFinanciere, SiteTouristique


@login_required
@require_http_methods(["GET", "POST"])
def enregistrer_acteur(request):
    """Affiche le formulaire d’enregistrement et la liste des acteurs déjà enregistrés."""

    success = False

    if request.method == "POST":
        form = ActeurEconomiqueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            success = True
            form = ActeurEconomiqueForm()  # Réinitialiser le formulaire après enregistrement
    else:
        form = ActeurEconomiqueForm()

    acteurs = ActeurEconomique.objects.all()

    context = {
        "form": form,
        "success": success,
        "acteurs": acteurs,
    }
    return render(request, "acteurs/enregistrement-acteurs.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def inscrire_institution_financiere(request):
    """Formulaire d’inscription des institutions financières."""

    success = False

    if request.method == "POST":
        form = InstitutionFinanciereForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            success = True
            form = InstitutionFinanciereForm()
    else:
        form = InstitutionFinanciereForm()

    institutions = InstitutionFinanciere.objects.all()

    context = {
        "form": form,
        "success": success,
        "institutions": institutions,
    }
    return render(request, "acteurs/inscription-institutions.html", context)

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
            "Santé",
            "Éducation et Formation",
            "Hôtellerie et Restauration",
            "Finance et Assurance",
            "Bar",
            "Restaurant",
            "Auberge",
            "Service Traiteur",
            "Pharmacie",
            "Dépôt de Pharmacie",
            "Écoles Publiques",
            "Écoles Privées",
            "Supermarché",
            "Boutique",
            "Alimentation générale",
            "Prêt-à-porter",
            "Quincaillerie",
            "Tourisme",
            "Autre",
        ]
    )
    statut_opts = "<br/>".join(
        [
            "SARL - Société à Responsabilité Limitée",
            "SA - Société Anonyme",
            "EI - Entreprise Individuelle",
            "SNC - Société en Nom Collectif",
            "Association",
            "ONG",
            "Coopérative",
            "Autre",
        ]
    )

    data = [
        [Paragraph("<b>Raison sociale</b>", cell_style), Paragraph("_________________________", cell_style)],
        [
            Paragraph("<b>Type d'acteur</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + type_acteur_opts, cell_style),
        ],
        [
            Paragraph("<b>Secteur d'activité</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + secteur_opts, cell_style),
        ],
        [
            Paragraph("<b>Statut juridique</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + statut_opts, cell_style),
        ],
        [Paragraph("<b>Description de l'activité</b>", cell_style), Paragraph("_________________________", cell_style)],
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

    # Section 2: Informations légales
    story.append(Paragraph("2. INFORMATIONS LÉGALES ET FISCALES", section_style))
    
    data = [
        ["N° RCCM", "___________________________"],
        ["N° CFE", "___________________________"],
        ["N° Carte d'Opérateur économique", "___________________________"],
        ["NIF", "___________________________"],
        ["Date de création", "___________________________"],
        ["Capital social (FCFA)", "___________________________"],
    ]
    
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    # Section 3: Responsable et Contact
    story.append(Paragraph("3. RESPONSABLE ET COORDONNÉES", section_style))
    
    data = [
        ["Nom du responsable", "___________________________"],
        ["Fonction", "___________________________"],
        ["Téléphone 1", "___________________________"],
        ["Téléphone 2", "___________________________"],
        ["Email professionnel", "___________________________"],
        ["Site web", "___________________________"],
    ]
    
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    # Section 4: Localisation
    story.append(Paragraph("4. LOCALISATION", section_style))
    
    data = [
        ["Quartier", "___________________________"],
        ["Canton", "___________________________"],
        ["Adresse complète", "___________________________"],
    ]
    
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    # Section 5: Informations complémentaires
    story.append(Paragraph("5. INFORMATIONS COMPLÉMENTAIRES", section_style))
    
    nb_employes_opts = "<br/>".join(["1 à 5", "6 à 10", "11 à 50", "51 à 100", "Plus de 100"])
    ca_opts = "<br/>".join(
        [
            "Moins de 5 millions",
            "5 à 20 millions",
            "20 à 50 millions",
            "50 à 100 millions",
            "Plus de 100 millions",
        ]
    )

    data = [
        [
            Paragraph("<b>Nombre d'employés</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + nb_employes_opts, cell_style),
        ],
        [
            Paragraph("<b>Chiffre d'affaires annuel (FCFA)</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + ca_opts, cell_style),
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
    story.append(Spacer(1, 0.3 * cm))

    # Section 6: Documents
    story.append(Paragraph("6. DOCUMENTS JUSTIFICATIFS", section_style))
    
    data = [
        ["Document de registre (RCCM)", "☐ Joindre le document"],
        ["Carte CFE", "☐ Joindre le document"],
        ["Autres documents", "☐ Joindre le document"],
    ]
    
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    # Conditions
    story.append(Paragraph("CONDITIONS", section_style))
    story.append(Paragraph("☐ Je certifie que les informations fournies sont exactes et complètes", field_style))
    story.append(Paragraph("☐ J'accepte que mes données soient traitées par la Mairie de Kloto 1", field_style))
    story.append(Paragraph("☐ J'accepte que mes coordonnées soient visibles publiquement sur la plateforme", field_style))

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

    # Section 1: Type et Identification
    story.append(Paragraph("1. TYPE ET IDENTIFICATION", section_style))

    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,
        wordWrap="CJK",
    )

    type_institution_opts = "<br/>".join(
        [
            "Banque commerciale",
            "Institution de microfinance (IMF)",
            "Bailleur de fonds",
            "ONG de financement",
            "Association",
            "Fondation",
            "Coopérative d'épargne et de crédit",
            "Compagnie d'assurance",
            "Société d'investissement",
            "Autre",
        ]
    )

    data = [
        [
            Paragraph("<b>Type d'institution</b>", cell_style),
            Paragraph("_________________________<br/><br/>Options :<br/>" + type_institution_opts, cell_style),
        ],
        [Paragraph("<b>Nom de l'institution</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Sigle / Acronyme</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>Année de création</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>N° d'agrément</b>", cell_style), Paragraph("_________________________", cell_style)],
        [Paragraph("<b>N° IFU</b>", cell_style), Paragraph("_________________________", cell_style)],
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

    # Section 2: Services Financiers
    story.append(Paragraph("2. SERVICES FINANCIERS PROPOSÉS", section_style))
    
    # Style pour les cellules de table
    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=10,
    )
    
    services_text = "☐ Comptes bancaires<br/>☐ Épargne<br/>☐ Crédits / Prêts<br/>☐ Micro-crédits<br/>☐ Transfert d'argent<br/>☐ Mobile Banking<br/>☐ Financement PME<br/>☐ Crédit agricole<br/>☐ Assurance<br/>☐ Change de devises<br/>☐ Conseil financier<br/>☐ Investissement"
    
    data = [
        [Paragraph("<b>Description générale des services</b>", cell_style), Paragraph("___________________________", cell_style)],
        [Paragraph("<b>Services disponibles</b>", cell_style), Paragraph(services_text, cell_style)],
        [Paragraph("<b>Taux d'intérêt moyen (crédit)</b>", cell_style), Paragraph("___________________________", cell_style)],
        [Paragraph("<b>Taux d'intérêt moyen (épargne)</b>", cell_style), Paragraph("___________________________", cell_style)],
    ]
    
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    # Section 3: Coordonnées
    story.append(Paragraph("3. COORDONNÉES ET CONTACT", section_style))
    
    data = [
        ["Nom du responsable", "___________________________"],
        ["Fonction", "___________________________"],
        ["Téléphone principal", "___________________________"],
        ["Téléphone secondaire", "___________________________"],
        ["WhatsApp", "___________________________"],
        ["Email principal", "___________________________"],
        ["Site web", "___________________________"],
        ["Page Facebook", "___________________________"],
    ]
    
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    # Section 4: Localisation
    story.append(Paragraph("4. LOCALISATION ET PRÉSENCE", section_style))
    
    data = [
        ["Quartier", "___________________________"],
        ["Canton", "___________________________"],
        ["Adresse complète", "___________________________"],
        ["Nombre d'agences dans Kloto 1", "___________________________"],
        ["Horaires d'ouverture", "___________________________"],
    ]
    
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    # Section 5: Documents
    story.append(Paragraph("5. DOCUMENTS JUSTIFICATIFS", section_style))
    
    data = [
        ["Agrément officiel", "☐ Joindre le document"],
        ["Logo de l'institution", "☐ Joindre le document"],
        ["Brochure / Présentation des services", "☐ Joindre le document"],
    ]
    
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    # Section 6: Informations complémentaires
    story.append(Paragraph("6. INFORMATIONS COMPLÉMENTAIRES", section_style))
    
    data = [
        ["Conditions d'éligibilité aux services", "___________________________"],
        ["Public cible prioritaire", "___________________________"],
    ]
    
    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    # Conditions
    story.append(Paragraph("CONDITIONS D'INSCRIPTION", section_style))
    field_style = ParagraphStyle(
        "FieldStyle",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=8,
        leftIndent=20,
    )
    story.append(Paragraph("☐ Je certifie que les informations fournies sont exactes et à jour", field_style))
    story.append(Paragraph("☐ J'accepte que les coordonnées de mon institution soient visibles publiquement", field_style))
    story.append(Paragraph("☐ J'accepte d'être contacté par les entreprises et citoyens via cette plateforme", field_style))
    story.append(Paragraph("☐ Je m'engage à actualiser mes informations régulièrement", field_style))

    doc.build(story)
    return response

