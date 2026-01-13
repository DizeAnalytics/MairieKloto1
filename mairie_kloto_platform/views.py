from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta, datetime, date
import os
import json
from django.core.serializers.json import DjangoJSONEncoder
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas as pdfcanvas
from mairie.models import ConfigurationMairie, VisiteSite

from acteurs.models import ActeurEconomique, InstitutionFinanciere
from emploi.models import ProfilEmploi
from mairie.models import Candidature, AppelOffre
from comptes.models import Notification
from django.utils.html import escape
from django.utils.text import slugify


class NumberedCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        pdfcanvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        width, height = self._pagesize
        self.drawCentredString(width / 2, 30, f"Page {self._pageNumber} / {page_count}")


def _format_pdf_value(value):
    if value in (None, "", [], ()):
        return "Non renseigné"
    if isinstance(value, bool):
        text = "Oui" if value else "Non"
    elif isinstance(value, datetime):
        text = value.strftime("%d/%m/%Y %H:%M")
    elif isinstance(value, date):
        text = value.strftime("%d/%m/%Y")
    elif isinstance(value, (list, tuple, set)):
        flattened = ", ".join(str(item) for item in value if item)
        text = flattened or "Non renseigné"
    else:
        text = str(value)
    # Escape HTML but preserve line breaks
    escaped = escape(text)
    return escaped.replace("\n", "<br/>")


def _make_pdf_filename(prefix, label):
    base = slugify(label) if label else ""
    if not base:
        base = slugify(prefix) or "detail"
    return f"{prefix}_{base}.pdf"


def _build_detail_pdf(filename, title, sections):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DetailTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#006233"),
        alignment=1,
        spaceAfter=18,
    )
    section_style = ParagraphStyle(
        "DetailSection",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#004d28"),
        spaceBefore=12,
        spaceAfter=8,
    )
    label_style = ParagraphStyle(
        "DetailLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#004d28"),
    )
    value_style = ParagraphStyle(
        "DetailValue",
        parent=styles["Normal"],
        leading=14,
    )
    story = [Paragraph(title, title_style)]

    for section_title, items in sections:
        if not items:
            continue
        story.append(Paragraph(section_title, section_style))
        table_data = []
        for label, value in items:
            table_data.append(
                [
                    Paragraph(str(escape(label)), label_style),
                    Paragraph(_format_pdf_value(value), value_style),
                ]
            )
        table = Table(table_data, colWidths=[6 * cm, 10.5 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#C8E6C9")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.25 * cm))

    if not sections:
        story.append(Paragraph("Aucune information disponible.", styles["Normal"]))

    doc.build(story, canvasmaker=NumberedCanvas)
    return response


def home(request):
    """Page d'accueil de la plateforme (page Enregistrement)."""

    context = {}
    return render(request, "mairie-kloto-platform.html", context)


def fake_admin(request):
    """Fausse route admin pour sécuriser l'accès à l'administration Django."""
    return render(request, "admin_fake.html", status=404)


def is_staff_user(user):
    """Vérifie si l'utilisateur est staff ou superuser."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(is_staff_user)
def tableau_bord(request):
    """Tableau de bord administrateur."""
    
    # Statistiques générales
    stats = {
        'acteurs_economiques': ActeurEconomique.objects.count(),
        'institutions_financieres': InstitutionFinanciere.objects.count(),
        'jeunes': ProfilEmploi.objects.filter(type_profil='jeune').count(),
        'retraites': ProfilEmploi.objects.filter(type_profil='retraite').count(),
        'candidatures': Candidature.objects.count(),
        'total_inscriptions': (
            ActeurEconomique.objects.count() +
            InstitutionFinanciere.objects.count() +
            ProfilEmploi.objects.count()
        ),
    }

    # Données pour le graphique (30 derniers jours)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Génération des dates
    dates = [(start_date + timedelta(days=i)).date() for i in range(31)]
    labels = [d.strftime('%d/%m') for d in dates]
    
    def get_counts(queryset, date_field):
        """
        Retourne une liste de 31 valeurs (une par jour) correspondant au nombre
        d'objets du queryset par jour entre start_date et end_date (inclus).
        Utilise un alias 'day' pour éviter les conflits avec d'éventuels champs 'date'.
        """
        data = (
            queryset.filter(**{f"{date_field}__gte": start_date})
            .annotate(day=TruncDay(date_field))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        count_dict = {item["day"].date(): item["count"] for item in data if item["day"]}
        return [count_dict.get(d, 0) for d in dates]

    chart_data = {
        'labels': labels,
        'acteurs': get_counts(ActeurEconomique.objects.all(), 'date_enregistrement'),
        'institutions': get_counts(InstitutionFinanciere.objects.all(), 'date_enregistrement'),
        'jeunes': get_counts(ProfilEmploi.objects.filter(type_profil='jeune'), 'date_inscription'),
        'retraites': get_counts(ProfilEmploi.objects.filter(type_profil='retraite'), 'date_inscription'),
        'visites': get_counts(VisiteSite.objects.all(), 'date'),
    }
    
    # Nombre total de visites sur les 30 derniers jours (toutes pages confondues)
    total_visites_30j = VisiteSite.objects.filter(date__gte=start_date, date__lte=end_date).count()

    context = {
        'stats': stats,
        'chart_data_json': json.dumps(chart_data, cls=DjangoJSONEncoder),
        'total_visites_30j': total_visites_30j,
    }
    
    return render(request, "admin/tableau_bord.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_acteurs_economiques(request):
    """Liste des acteurs économiques enregistrés."""
    
    acteurs = ActeurEconomique.objects.all().order_by('-date_enregistrement')
    
    # Récupération des paramètres de filtrage
    q = request.GET.get('q', '')
    type_acteur = request.GET.get('type', '')
    secteur = request.GET.get('secteur', '')
    
    # Application des filtres
    if q:
        acteurs = acteurs.filter(
            Q(raison_sociale__icontains=q) |
            Q(nom_responsable__icontains=q) |
            Q(email__icontains=q) |
            Q(telephone1__icontains=q)
        )
    
    if type_acteur:
        acteurs = acteurs.filter(type_acteur=type_acteur)
        
    if secteur:
        acteurs = acteurs.filter(secteur_activite=secteur)
    
    context = {
        'acteurs': acteurs,
        'titre': 'Acteurs Économiques',
        'type_choices': ActeurEconomique.TYPE_ACTEUR_CHOICES,
        'secteur_choices': ActeurEconomique.SECTEUR_ACTIVITE_CHOICES,
        'current_filters': {
            'q': q,
            'type': type_acteur,
            'secteur': secteur
        }
    }
    
    return render(request, "admin/liste_inscriptions.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_institutions_financieres(request):
    """Liste des institutions financières enregistrées."""
    
    institutions = InstitutionFinanciere.objects.all().order_by('-date_enregistrement')
    
    # Récupération des paramètres de filtrage
    q = request.GET.get('q', '')
    type_inst = request.GET.get('type', '')
    
    # Application des filtres
    if q:
        institutions = institutions.filter(
            Q(nom_institution__icontains=q) |
            Q(sigle__icontains=q) |
            Q(nom_responsable__icontains=q) |
            Q(email__icontains=q) |
            Q(telephone1__icontains=q)
        )
    
    if type_inst:
        institutions = institutions.filter(type_institution=type_inst)
    
    context = {
        'institutions': institutions,
        'titre': 'Institutions Financières',
        'type_choices': InstitutionFinanciere.TYPE_INSTITUTION_CHOICES,
        'current_filters': {
            'q': q,
            'type': type_inst
        }
    }
    
    return render(request, "admin/liste_institutions.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_jeunes(request):
    """Liste des jeunes demandeurs d'emploi."""
    
    jeunes = ProfilEmploi.objects.filter(type_profil='jeune').order_by('-date_inscription')
    
    # Récupération des paramètres de filtrage
    q = request.GET.get('q', '')
    niveau = request.GET.get('niveau', '')
    dispo = request.GET.get('dispo', '')
    
    # Application des filtres
    if q:
        jeunes = jeunes.filter(
            Q(nom__icontains=q) |
            Q(prenoms__icontains=q) |
            Q(email__icontains=q) |
            Q(telephone1__icontains=q) |
            Q(domaine_competence__icontains=q)
        )
        
    if niveau:
        jeunes = jeunes.filter(niveau_etude=niveau)
        
    if dispo:
        jeunes = jeunes.filter(disponibilite=dispo)
    
    context = {
        'profils': jeunes,
        'titre': 'Jeunes Demandeurs d\'Emploi',
        'type_profil': 'jeune',
        'niveau_choices': ProfilEmploi.NIVEAU_ETUDE_CHOICES,
        'dispo_choices': ProfilEmploi.DISPONIBILITE_CHOICES,
        'current_filters': {
            'q': q,
            'niveau': niveau,
            'dispo': dispo
        }
    }
    
    return render(request, "admin/liste_profils_emploi.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_retraites(request):
    """Liste des retraités actifs."""
    
    retraites = ProfilEmploi.objects.filter(type_profil='retraite').order_by('-date_inscription')
    
    # Récupération des paramètres de filtrage
    q = request.GET.get('q', '')
    niveau = request.GET.get('niveau', '')
    dispo = request.GET.get('dispo', '')
    
    # Application des filtres
    if q:
        retraites = retraites.filter(
            Q(nom__icontains=q) |
            Q(prenoms__icontains=q) |
            Q(email__icontains=q) |
            Q(telephone1__icontains=q) |
            Q(domaine_competence__icontains=q)
        )
        
    if niveau:
        retraites = retraites.filter(niveau_etude=niveau)
        
    if dispo:
        retraites = retraites.filter(disponibilite=dispo)
    
    context = {
        'profils': retraites,
        'titre': 'Retraités Actifs',
        'type_profil': 'retraite',
        'niveau_choices': ProfilEmploi.NIVEAU_ETUDE_CHOICES,
        'dispo_choices': ProfilEmploi.DISPONIBILITE_CHOICES,
        'current_filters': {
            'q': q,
            'niveau': niveau,
            'dispo': dispo
        }
    }
    
    return render(request, "admin/liste_profils_emploi.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_candidatures(request):
    """Liste des candidatures aux appels d'offres."""
    
    candidatures = Candidature.objects.all().select_related('appel_offre', 'candidat').order_by('-date_soumission')
    
    # Récupération des paramètres de filtrage
    q = request.GET.get('q', '')
    statut = request.GET.get('statut', '')
    
    # Application des filtres
    if q:
        candidatures = candidatures.filter(
            Q(appel_offre__titre__icontains=q) |
            Q(appel_offre__reference__icontains=q) |
            Q(candidat__first_name__icontains=q) |
            Q(candidat__last_name__icontains=q) |
            Q(candidat__email__icontains=q)
        )
    
    if statut:
        candidatures = candidatures.filter(statut=statut)
    
    # Grouper les candidatures par appel d'offres et compter les acceptées
    appels_offres_avec_candidatures = {}
    for candidature in candidatures:
        appel_id = candidature.appel_offre.id
        if appel_id not in appels_offres_avec_candidatures:
            appels_offres_avec_candidatures[appel_id] = {
                'appel_offre': candidature.appel_offre,
                'nb_acceptees': 0
            }
        if candidature.statut == 'acceptee':
            appels_offres_avec_candidatures[appel_id]['nb_acceptees'] += 1
    
    context = {
        'candidatures': candidatures,
        'appels_offres_avec_candidatures': appels_offres_avec_candidatures,
        'titre': 'Candidatures aux Appels d\'Offres',
        'statut_choices': Candidature.STATUT_CANDIDATURE,
        'current_filters': {
            'q': q,
            'statut': statut
        }
    }
    
    return render(request, "admin/liste_candidatures.html", context)


@login_required
@user_passes_test(is_staff_user)
def export_pdf_candidatures(request, appel_offre_id):
    """
    Génère un PDF des candidatures acceptées pour un appel d'offres spécifique.
    """
    appel_offre = get_object_or_404(AppelOffre, pk=appel_offre_id)
    
    candidatures = Candidature.objects.filter(
        appel_offre=appel_offre,
        statut="acceptee"
    ).select_related("appel_offre", "candidat").order_by("-date_soumission")

    if not candidatures.exists():
        messages.warning(
            request,
            f"Aucun dossier accepté pour l'appel d'offres '{appel_offre.titre}'.",
        )
        return redirect("liste_candidatures")

    conf = ConfigurationMairie.objects.filter(est_active=True).first()
    response = HttpResponse(content_type="application/pdf")
    filename = _make_pdf_filename("candidatures-acceptees", appel_offre.reference or appel_offre.titre)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#006233"),
        alignment=1,
        spaceAfter=12,
    )
    story = [
        Paragraph("Candidatures acceptées", title_style),
        Paragraph(f"Appel d'offres : {escape(appel_offre.titre)}", styles["Heading2"]),
        Spacer(1, 0.2 * cm),
    ]
    
    if appel_offre.reference:
        story.append(Paragraph(f"Référence : {escape(appel_offre.reference)}", styles["Normal"]))
    
    story.append(Spacer(1, 0.4 * cm))

    # Tableau : Nom de l'entreprise ou Nom & Prénoms du candidat, Email, Date soumission, Téléphone
    data = [["Nom / Raison sociale", "Email", "Date de soumission", "Téléphone"]]
    for candidature in candidatures:
        user = candidature.candidat

        # Nom / Raison sociale
        full_name = user.get_full_name() or user.username
        display_name = full_name

        # Si l'utilisateur est lié à une entreprise ou institution, on affiche la raison sociale
        acteur = getattr(user, "acteur_economique", None)
        institution = getattr(user, "institution_financiere", None)
        profil = getattr(user, "profil_emploi", None)

        if acteur is not None:
            display_name = acteur.raison_sociale
        elif institution is not None:
            display_name = institution.nom_institution
        elif profil is not None:
            display_name = f"{profil.nom} {profil.prenoms}"

        # Numéro de téléphone
        telephone = ""
        if acteur is not None:
            telephone = acteur.telephone1
        elif institution is not None:
            telephone = institution.telephone1
        elif profil is not None:
            telephone = profil.telephone1

        data.append(
            [
                escape(display_name),
                user.email,
                candidature.date_soumission.strftime("%d/%m/%Y %H:%M"),
                telephone,
            ]
        )

    table = Table(data, colWidths=[7 * cm, 7 * cm, 4.5 * cm, 4.5 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F5E9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph("Date et Signature : ________________________________", styles["Normal"]))

    def on_page(canvas, doc):
        width, height = doc.pagesize
        y = height - 40
        canvas.saveState()
        canvas.translate(width / 2, height / 2)
        canvas.rotate(45)
        canvas.setFont("Helvetica-Bold", 36)
        canvas.setFillColorRGB(0.9, 0.9, 0.9)
        canvas.drawCentredString(0, 0, (conf.nom_commune if conf else "Mairie de Kloto 1").upper())
        canvas.restoreState()
        if conf and getattr(conf, "logo", None) and getattr(conf.logo, "path", None):
            try:
                canvas.drawImage(conf.logo.path, 40, y - 30, width=40, height=40, preserveAspectRatio=True, mask="auto")
            except Exception:
                pass
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(100, y, f"République Togolaise – {conf.nom_commune if conf else 'Mairie de Kloto 1'}")

        canvas.setFont("Helvetica", 9)
        canvas.drawString(40, 30, timezone.now().strftime("Édité le %d/%m/%Y %H:%M"))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page, canvasmaker=NumberedCanvas)
    return response


@login_required
@user_passes_test(is_staff_user)
@require_POST
def changer_statut(request, model_name, pk, action):
    """Change le statut d'un objet (accepter/refuser)."""
    
    model_map = {
        'candidature': Candidature,
        'acteur': ActeurEconomique,
        'institution': InstitutionFinanciere,
        'jeune': ProfilEmploi,
        'retraite': ProfilEmploi,
    }
    
    ModelClass = model_map.get(model_name)
    if not ModelClass:
        messages.error(request, "Type d'objet invalide.")
        return redirect('tableau_bord')
        
    obj = get_object_or_404(ModelClass, pk=pk)
    
    if model_name == 'candidature':
        if action == 'accepter':
            obj.statut = 'acceptee'
            messages.success(request, f"Candidature de {obj.candidat} acceptée.")
        elif action in ['refuser', 'rejeter']:
            obj.statut = 'refusee'
            messages.warning(request, f"Candidature de {obj.candidat} refusée.")
    else:
        # Pour les autres modèles, on utilise est_valide_par_mairie
        if action == 'accepter':
            obj.est_valide_par_mairie = True
            messages.success(request, f"{obj} validé avec succès.")
        elif action in ['refuser', 'rejeter']:
            obj.est_valide_par_mairie = False
            messages.warning(request, f"{obj} refusé/invalidé.")
            
    obj.save()
    
    # Redirection vers la liste appropriée
    redirect_map = {
        'candidature': 'liste_candidatures',
        'acteur': 'liste_acteurs',
        'institution': 'liste_institutions',
        'jeune': 'liste_jeunes',
        'retraite': 'liste_retraites',
    }
    
    return redirect(redirect_map.get(model_name, 'tableau_bord'))


@login_required
@user_passes_test(is_staff_user)
def export_pdf_acteur_detail(request, pk):
    acteur = get_object_or_404(ActeurEconomique, pk=pk)
    sections = [
        (
            "Informations générales",
            [
                ("Raison sociale", acteur.raison_sociale),
                ("Sigle / Acronyme", acteur.sigle),
                ("Type d'acteur", acteur.get_type_acteur_display()),
                ("Secteur d'activité", acteur.get_secteur_activite_display()),
                ("Statut juridique", acteur.get_statut_juridique_display()),
                ("Description", acteur.description),
            ],
        ),
        (
            "Informations légales et fiscales",
            [
                ("N° RCCM", acteur.rccm),
                ("N° CFE", acteur.cfe),
                ("N° Carte opérateur économique", acteur.numero_carte_operateur),
                ("NIF", acteur.nif),
                ("Date de création", acteur.date_creation),
                (
                    "Capital social",
                    f"{acteur.capital_social} FCFA" if acteur.capital_social is not None else None,
                ),
            ],
        ),
        (
            "Responsable et contacts",
            [
                ("Nom du responsable", acteur.nom_responsable),
                ("Fonction", acteur.fonction_responsable),
                ("Téléphone principal", acteur.telephone1),
                ("Téléphone secondaire", acteur.telephone2),
                ("Email professionnel", acteur.email),
                ("Site web", acteur.site_web),
            ],
        ),
        (
            "Localisation et présence",
            [
                ("Situation", acteur.get_situation_display()),
                ("Quartier", acteur.quartier),
                ("Canton", acteur.canton),
                ("Adresse complète", acteur.adresse_complete),
            ],
        ),
        (
            "Informations complémentaires",
            [
                (
                    "Nombre d'employés",
                    acteur.get_nombre_employes_display() if acteur.nombre_employes else None,
                ),
                (
                    "Chiffre d'affaires",
                    acteur.get_chiffre_affaires_display() if acteur.chiffre_affaires else None,
                ),
                ("Accepte publication publique", acteur.accepte_public),
                ("Certifie les informations", acteur.certifie_information),
                ("Accepte les conditions", acteur.accepte_conditions),
                ("Validé par la mairie", acteur.est_valide_par_mairie),
                ("Date d'enregistrement", acteur.date_enregistrement),
            ],
        ),
    ]

    filename = _make_pdf_filename("acteur", acteur.raison_sociale)
    title = f"Fiche Acteur Économique - {acteur.raison_sociale}"
    return _build_detail_pdf(filename, title, sections)


@login_required
@user_passes_test(is_staff_user)
def export_pdf_institution_detail(request, pk):
    institution = get_object_or_404(InstitutionFinanciere, pk=pk)
    services_text = (
        ", ".join(part.strip().title() for part in institution.services.split(",") if part.strip())
        if institution.services
        else None
    )

    sections = [
        (
            "Informations générales",
            [
                ("Nom de l'institution", institution.nom_institution),
                ("Sigle", institution.sigle),
                ("Type d'institution", institution.get_type_institution_display()),
                ("Année de création", institution.annee_creation),
                ("Numéro d'agrément", institution.numero_agrement),
                ("IFU", institution.ifu),
                ("Description des services", institution.description_services),
                ("Services disponibles", services_text),
            ],
        ),
        (
            "Conditions financières",
            [
                ("Taux crédit", institution.taux_credit),
                ("Taux épargne", institution.taux_epargne),
                ("Conditions d'éligibilité", institution.conditions_eligibilite),
                ("Public cible", institution.public_cible),
            ],
        ),
        (
            "Responsable et contacts",
            [
                ("Nom du responsable", institution.nom_responsable),
                ("Fonction", institution.fonction_responsable),
                ("Téléphone principal", institution.telephone1),
                ("Téléphone secondaire", institution.telephone2),
                ("WhatsApp", institution.whatsapp),
                ("Email", institution.email),
                ("Site web", institution.site_web),
                ("Page Facebook", institution.facebook),
            ],
        ),
        (
            "Localisation et présence",
            [
                ("Situation", institution.get_situation_display()),
                ("Quartier", institution.quartier),
                ("Canton", institution.canton),
                ("Adresse complète", institution.adresse_complete),
                ("Nombre d'agences dans Kloto 1", institution.nombre_agences),
                ("Horaires d'ouverture", institution.horaires),
            ],
        ),
        (
            "Engagements et statut",
            [
                ("Certifie les informations", institution.certifie_info),
                ("Accepte la publication publique", institution.accepte_public),
                ("Accepte d'être contacté", institution.accepte_contact),
                ("Engagement pris", institution.engagement),
                ("Validée par la mairie", institution.est_valide_par_mairie),
                ("Date d'enregistrement", institution.date_enregistrement),
            ],
        ),
    ]

    filename = _make_pdf_filename("institution", institution.nom_institution)
    title = f"Fiche Institution Financière - {institution.nom_institution}"
    return _build_detail_pdf(filename, title, sections)


def _export_pdf_profil_detail(pk, profil_type):
    profil = get_object_or_404(ProfilEmploi, pk=pk, type_profil=profil_type)

    sections = [
        (
            "Identité",
            [
                ("Type de profil", profil.get_type_profil_display()),
                ("Nom", profil.nom),
                ("Prénoms", profil.prenoms),
                ("Sexe", profil.get_sexe_display()),
                ("Date de naissance", profil.date_naissance),
                ("Nationalité", profil.nationalite),
                ("Résident Kloto 1", profil.est_resident_kloto),
            ],
        ),
        (
            "Coordonnées",
            [
                ("Téléphone principal", profil.telephone1),
                ("Téléphone secondaire", profil.telephone2),
                ("Email", profil.email),
                ("Quartier", profil.quartier),
                ("Canton", profil.canton),
                ("Adresse complète", profil.adresse_complete),
            ],
        ),
        (
            "Formation et compétences",
            [
                ("Niveau d'étude", profil.get_niveau_etude_display() if profil.niveau_etude else None),
                ("Diplôme principal", profil.diplome_principal),
                ("Domaine de compétence", profil.domaine_competence),
                ("Expériences", profil.experiences),
                ("Dernier poste occupé", profil.dernier_poste),
                ("Années d'expérience", profil.annees_experience),
            ],
        ),
        (
            "Situation professionnelle",
            [
                ("Situation actuelle", profil.get_situation_actuelle_display()),
                ("Employeur actuel", profil.employeur_actuel),
                ("Disponibilité", profil.get_disponibilite_display()),
                (
                    "Type de contrat souhaité",
                    profil.get_type_contrat_souhaite_display() if profil.type_contrat_souhaite else None,
                ),
                ("Salaire souhaité", profil.salaire_souhaite),
                ("Caisse de retraite / régime", profil.caisse_retraite),
            ],
        ),
        (
            "Consentements et statut",
            [
                ("Accepte le traitement des données", profil.accepte_rgpd),
                ("Accepte d'être contacté", profil.accepte_contact),
                ("Validé par la mairie", profil.est_valide_par_mairie),
                ("Date d'inscription", profil.date_inscription),
            ],
        ),
    ]

    filename = _make_pdf_filename(profil_type, f"{profil.nom}-{profil.prenoms}")
    title = f"Fiche {profil.get_type_profil_display()} - {profil.nom} {profil.prenoms}"
    return _build_detail_pdf(filename, title, sections)


@login_required
@user_passes_test(is_staff_user)
def export_pdf_jeune_detail(request, pk):
    return _export_pdf_profil_detail(pk, "jeune")


@login_required
@user_passes_test(is_staff_user)
def export_pdf_retraite_detail(request, pk):
    return _export_pdf_profil_detail(pk, "retraite")


@login_required
@user_passes_test(is_staff_user)
def export_pdf_acteurs(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    qs = ActeurEconomique.objects.all()
    conf = ConfigurationMairie.objects.filter(est_active=True).first()
    if start:
        try:
            sd = datetime.strptime(start, "%Y-%m-%d").date()
            qs = qs.filter(date_enregistrement__date__gte=sd)
        except ValueError:
            pass
    if end:
        try:
            ed = datetime.strptime(end, "%Y-%m-%d").date()
            qs = qs.filter(date_enregistrement__date__lte=ed)
        except ValueError:
            pass
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="acteurs_economiques.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#006233"), alignment=1, spaceAfter=12)
    story.append(Paragraph("Acteurs Économiques", title_style))
    if start or end:
        story.append(Paragraph(f"Période: {start or '...'} au {end or '...'}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))
    data = [["Raison sociale", "Type", "Secteur", "Responsable", "Téléphone"]]
    for a in qs.order_by("-date_enregistrement")[:1000]:
        data.append([
            a.raison_sociale,
            a.get_type_acteur_display(),
            a.get_secteur_activite_display(),
            a.nom_responsable,
            a.telephone1,
        ])
    table = Table(data, colWidths=[7*cm, 4*cm, 5*cm, 6*cm, 4*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph("Date et Signature : ________________________________", styles["Normal"]))
    
    def on_page(c, d):
        width, height = d.pagesize
        y = height - 40
        c.saveState()
        c.translate(width/2, height/2)
        c.rotate(45)
        c.setFont("Helvetica-Bold", 36)
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.drawCentredString(0, 0, (conf.nom_commune if conf else "Mairie de Kloto 1").upper())
        c.restoreState()
        if conf and getattr(conf, "logo", None) and getattr(conf.logo, "path", None):
            try:
                c.drawImage(conf.logo.path, 40, y-30, width=40, height=40, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y, f"République Togolaise – {conf.nom_commune if conf else 'Mairie de Kloto 1'}")
        
        c.setFont("Helvetica", 9)
        c.drawString(40, 30, timezone.now().strftime("Édité le %d/%m/%Y %H:%M"))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page, canvasmaker=NumberedCanvas)
    return response


@login_required
@user_passes_test(is_staff_user)
def notifications_candidats(request):
    """Liste des appels d'offres avec candidats acceptés pour envoyer des notifications."""
    
    # Récupérer tous les appels d'offres qui ont au moins une candidature acceptée
    appels_offres = AppelOffre.objects.filter(
        candidatures__statut='acceptee'
    ).distinct().annotate(
        nb_candidats_acceptes=Count('candidatures', filter=Q(candidatures__statut='acceptee'))
    ).order_by('-date_debut')
    
    context = {
        'appels_offres': appels_offres,
    }
    
    return render(request, "admin/notifications_candidats.html", context)


@login_required
@user_passes_test(is_staff_user)
def envoyer_notifications_candidats(request, appel_offre_id):
    """Affiche le formulaire et traite l'envoi de notifications aux candidats acceptés."""
    
    appel_offre = get_object_or_404(AppelOffre, pk=appel_offre_id)
    
    # Récupérer uniquement les candidats acceptés pour cet appel d'offres
    candidats_acceptes = Candidature.objects.filter(
        appel_offre=appel_offre,
        statut='acceptee'
    ).select_related('candidat')
    
    if not candidats_acceptes.exists():
        messages.warning(request, "Aucun candidat accepté trouvé pour cet appel d'offres.")
        return redirect('notifications_candidats')
    
    if request.method == 'POST':
        titre = request.POST.get('titre', '')
        message = request.POST.get('message', '')
        type_notification = request.POST.get('type', Notification.TYPE_INFO)
        
        if not titre or not message:
            messages.error(request, "Le titre et le message sont obligatoires.")
        else:
            # Créer une notification pour chaque candidat accepté
            notifications_creees = 0
            for candidature in candidats_acceptes:
                Notification.objects.create(
                    recipient=candidature.candidat,
                    title=titre,
                    message=message,
                    type=type_notification,
                    created_by=request.user,
                )
                notifications_creees += 1
            
            messages.success(
                request, 
                f"Notifications envoyées avec succès à {notifications_creees} candidat(s) accepté(s)."
            )
            return redirect('notifications_candidats')
    
    context = {
        'appel_offre': appel_offre,
        'candidats_acceptes': candidats_acceptes,
        'nb_candidats': candidats_acceptes.count(),
        'type_choices': Notification.TYPE_CHOICES,
    }
    
    return render(request, "admin/envoyer_notifications_candidats.html", context)


@login_required
@user_passes_test(is_staff_user)
def export_pdf_entreprises(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    qs = ActeurEconomique.objects.filter(type_acteur="entreprise")
    conf = ConfigurationMairie.objects.filter(est_active=True).first()
    if start:
        try:
            sd = datetime.strptime(start, "%Y-%m-%d").date()
            qs = qs.filter(date_enregistrement__date__gte=sd)
        except ValueError:
            pass
    if end:
        try:
            ed = datetime.strptime(end, "%Y-%m-%d").date()
            qs = qs.filter(date_enregistrement__date__lte=ed)
        except ValueError:
            pass
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="entreprises.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#006233"), alignment=1, spaceAfter=12)
    story.append(Paragraph("Entreprises", title_style))
    if start or end:
        story.append(Paragraph(f"Période: {start or '...'} au {end or '...'}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))
    data = [["Raison sociale", "Secteur", "Responsable", "Téléphone"]]
    for a in qs.order_by("-date_enregistrement")[:1000]:
        data.append([
            a.raison_sociale,
            a.get_secteur_activite_display(),
            a.nom_responsable,
            a.telephone1,
        ])
    table = Table(data, colWidths=[8*cm, 7*cm, 7*cm, 5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph("Date et Signature : ________________________________", styles["Normal"]))
    
    def on_page(c, d):
        width, height = d.pagesize
        y = height - 40
        c.saveState()
        c.translate(width/2, height/2)
        c.rotate(45)
        c.setFont("Helvetica-Bold", 36)
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.drawCentredString(0, 0, (conf.nom_commune if conf else "Mairie de Kloto 1").upper())
        c.restoreState()
        if conf and getattr(conf, "logo", None) and getattr(conf.logo, "path", None):
            try:
                c.drawImage(conf.logo.path, 40, y-30, width=40, height=40, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y, f"République Togolaise – {conf.nom_commune if conf else 'Mairie de Kloto 1'}")
        
        c.setFont("Helvetica", 9)
        c.drawString(40, 30, timezone.now().strftime("Édité le %d/%m/%Y %H:%M"))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page, canvasmaker=NumberedCanvas)
    return response


@login_required
@user_passes_test(is_staff_user)
def notifications_candidats(request):
    """Liste des appels d'offres avec candidats acceptés pour envoyer des notifications."""
    
    # Récupérer tous les appels d'offres qui ont au moins une candidature acceptée
    appels_offres = AppelOffre.objects.filter(
        candidatures__statut='acceptee'
    ).distinct().annotate(
        nb_candidats_acceptes=Count('candidatures', filter=Q(candidatures__statut='acceptee'))
    ).order_by('-date_debut')
    
    context = {
        'appels_offres': appels_offres,
    }
    
    return render(request, "admin/notifications_candidats.html", context)


@login_required
@user_passes_test(is_staff_user)
def envoyer_notifications_candidats(request, appel_offre_id):
    """Affiche le formulaire et traite l'envoi de notifications aux candidats acceptés."""
    
    appel_offre = get_object_or_404(AppelOffre, pk=appel_offre_id)
    
    # Récupérer uniquement les candidats acceptés pour cet appel d'offres
    candidats_acceptes = Candidature.objects.filter(
        appel_offre=appel_offre,
        statut='acceptee'
    ).select_related('candidat')
    
    if not candidats_acceptes.exists():
        messages.warning(request, "Aucun candidat accepté trouvé pour cet appel d'offres.")
        return redirect('notifications_candidats')
    
    if request.method == 'POST':
        titre = request.POST.get('titre', '')
        message = request.POST.get('message', '')
        type_notification = request.POST.get('type', Notification.TYPE_INFO)
        
        if not titre or not message:
            messages.error(request, "Le titre et le message sont obligatoires.")
        else:
            # Créer une notification pour chaque candidat accepté
            notifications_creees = 0
            for candidature in candidats_acceptes:
                Notification.objects.create(
                    recipient=candidature.candidat,
                    title=titre,
                    message=message,
                    type=type_notification,
                    created_by=request.user,
                )
                notifications_creees += 1
            
            messages.success(
                request, 
                f"Notifications envoyées avec succès à {notifications_creees} candidat(s) accepté(s)."
            )
            return redirect('notifications_candidats')
    
    context = {
        'appel_offre': appel_offre,
        'candidats_acceptes': candidats_acceptes,
        'nb_candidats': candidats_acceptes.count(),
        'type_choices': Notification.TYPE_CHOICES,
    }
    
    return render(request, "admin/envoyer_notifications_candidats.html", context)


@login_required
@user_passes_test(is_staff_user)
def export_pdf_jeunes(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    qs = ProfilEmploi.objects.filter(type_profil="jeune")
    conf = ConfigurationMairie.objects.filter(est_active=True).first()
    if start:
        try:
            sd = datetime.strptime(start, "%Y-%m-%d").date()
            qs = qs.filter(date_inscription__date__gte=sd)
        except ValueError:
            pass
    if end:
        try:
            ed = datetime.strptime(end, "%Y-%m-%d").date()
            qs = qs.filter(date_inscription__date__lte=ed)
        except ValueError:
            pass
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="jeunes_demandeurs.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#006233"), alignment=1, spaceAfter=12)
    story.append(Paragraph("Jeunes Demandeurs d'Emploi", title_style))
    if start or end:
        story.append(Paragraph(f"Période: {start or '...'} au {end or '...'}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))
    data = [["Nom", "Prénoms", "Diplôme", "Téléphone", "Quartier", "Compétences"]]
    for p in qs.order_by("-date_inscription")[:1000]:
        data.append([
            p.nom,
            p.prenoms,
            (p.diplome_principal or "")[:30],
            p.telephone1,
            p.quartier,
            (p.domaine_competence or "")[:60],
        ])
    table = Table(data, colWidths=[3.5*cm, 4*cm, 4*cm, 3.5*cm, 3*cm, 8*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph("Date et Signature : ________________________________", styles["Normal"]))
    
    def on_page(c, d):
        width, height = d.pagesize
        y = height - 40
        c.saveState()
        c.translate(width/2, height/2)
        c.rotate(45)
        c.setFont("Helvetica-Bold", 36)
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.drawCentredString(0, 0, (conf.nom_commune if conf else "Mairie de Kloto 1").upper())
        c.restoreState()
        if conf and getattr(conf, "logo", None) and getattr(conf.logo, "path", None):
            try:
                c.drawImage(conf.logo.path, 40, y-30, width=40, height=40, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y, f"République Togolaise – {conf.nom_commune if conf else 'Mairie de Kloto 1'}")
        
        c.setFont("Helvetica", 9)
        c.drawString(40, 30, timezone.now().strftime("Édité le %d/%m/%Y %H:%M"))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page, canvasmaker=NumberedCanvas)
    return response


@login_required
@user_passes_test(is_staff_user)
def notifications_candidats(request):
    """Liste des appels d'offres avec candidats acceptés pour envoyer des notifications."""
    
    # Récupérer tous les appels d'offres qui ont au moins une candidature acceptée
    appels_offres = AppelOffre.objects.filter(
        candidatures__statut='acceptee'
    ).distinct().annotate(
        nb_candidats_acceptes=Count('candidatures', filter=Q(candidatures__statut='acceptee'))
    ).order_by('-date_debut')
    
    context = {
        'appels_offres': appels_offres,
    }
    
    return render(request, "admin/notifications_candidats.html", context)


@login_required
@user_passes_test(is_staff_user)
def envoyer_notifications_candidats(request, appel_offre_id):
    """Affiche le formulaire et traite l'envoi de notifications aux candidats acceptés."""
    
    appel_offre = get_object_or_404(AppelOffre, pk=appel_offre_id)
    
    # Récupérer uniquement les candidats acceptés pour cet appel d'offres
    candidats_acceptes = Candidature.objects.filter(
        appel_offre=appel_offre,
        statut='acceptee'
    ).select_related('candidat')
    
    if not candidats_acceptes.exists():
        messages.warning(request, "Aucun candidat accepté trouvé pour cet appel d'offres.")
        return redirect('notifications_candidats')
    
    if request.method == 'POST':
        titre = request.POST.get('titre', '')
        message = request.POST.get('message', '')
        type_notification = request.POST.get('type', Notification.TYPE_INFO)
        
        if not titre or not message:
            messages.error(request, "Le titre et le message sont obligatoires.")
        else:
            # Créer une notification pour chaque candidat accepté
            notifications_creees = 0
            for candidature in candidats_acceptes:
                Notification.objects.create(
                    recipient=candidature.candidat,
                    title=titre,
                    message=message,
                    type=type_notification,
                    created_by=request.user,
                )
                notifications_creees += 1
            
            messages.success(
                request, 
                f"Notifications envoyées avec succès à {notifications_creees} candidat(s) accepté(s)."
            )
            return redirect('notifications_candidats')
    
    context = {
        'appel_offre': appel_offre,
        'candidats_acceptes': candidats_acceptes,
        'nb_candidats': candidats_acceptes.count(),
        'type_choices': Notification.TYPE_CHOICES,
    }
    
    return render(request, "admin/envoyer_notifications_candidats.html", context)


@login_required
@user_passes_test(is_staff_user)
def export_pdf_retraites(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    qs = ProfilEmploi.objects.filter(type_profil="retraite")
    conf = ConfigurationMairie.objects.filter(est_active=True).first()
    if start:
        try:
            sd = datetime.strptime(start, "%Y-%m-%d").date()
            qs = qs.filter(date_inscription__date__gte=sd)
        except ValueError:
            pass
    if end:
        try:
            ed = datetime.strptime(end, "%Y-%m-%d").date()
            qs = qs.filter(date_inscription__date__lte=ed)
        except ValueError:
            pass
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="retraites_actifs.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#006233"), alignment=1, spaceAfter=12)
    story.append(Paragraph("Retraités Actifs", title_style))
    if start or end:
        story.append(Paragraph(f"Période: {start or '...'} au {end or '...'}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))
    data = [["Nom", "Prénoms", "Diplôme", "Téléphone", "Quartier", "Dernier poste"]]
    for p in qs.order_by("-date_inscription")[:1000]:
        data.append([
            p.nom,
            p.prenoms,
            (p.diplome_principal or "")[:30],
            p.telephone1,
            p.quartier,
            (p.dernier_poste or "")[:60],
        ])
    table = Table(data, colWidths=[3.5*cm, 4*cm, 4*cm, 3.5*cm, 3*cm, 8*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph("Date et Signature : ________________________________", styles["Normal"]))
    
    def on_page(c, d):
        width, height = d.pagesize
        y = height - 40
        c.saveState()
        c.translate(width/2, height/2)
        c.rotate(45)
        c.setFont("Helvetica-Bold", 36)
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.drawCentredString(0, 0, (conf.nom_commune if conf else "Mairie de Kloto 1").upper())
        c.restoreState()
        if conf and getattr(conf, "logo", None) and getattr(conf.logo, "path", None):
            try:
                c.drawImage(conf.logo.path, 40, y-30, width=40, height=40, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y, f"République Togolaise – {conf.nom_commune if conf else 'Mairie de Kloto 1'}")
        
        c.setFont("Helvetica", 9)
        c.drawString(40, 30, timezone.now().strftime("Édité le %d/%m/%Y %H:%M"))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page, canvasmaker=NumberedCanvas)
    return response


@login_required
@user_passes_test(is_staff_user)
def notifications_candidats(request):
    """Liste des appels d'offres avec candidats acceptés pour envoyer des notifications."""
    
    # Récupérer tous les appels d'offres qui ont au moins une candidature acceptée
    appels_offres = AppelOffre.objects.filter(
        candidatures__statut='acceptee'
    ).distinct().annotate(
        nb_candidats_acceptes=Count('candidatures', filter=Q(candidatures__statut='acceptee'))
    ).order_by('-date_debut')
    
    context = {
        'appels_offres': appels_offres,
    }
    
    return render(request, "admin/notifications_candidats.html", context)


@login_required
@user_passes_test(is_staff_user)
def envoyer_notifications_candidats(request, appel_offre_id):
    """Affiche le formulaire et traite l'envoi de notifications aux candidats acceptés."""
    
    appel_offre = get_object_or_404(AppelOffre, pk=appel_offre_id)
    
    # Récupérer uniquement les candidats acceptés pour cet appel d'offres
    candidats_acceptes = Candidature.objects.filter(
        appel_offre=appel_offre,
        statut='acceptee'
    ).select_related('candidat')
    
    if not candidats_acceptes.exists():
        messages.warning(request, "Aucun candidat accepté trouvé pour cet appel d'offres.")
        return redirect('notifications_candidats')
    
    if request.method == 'POST':
        titre = request.POST.get('titre', '')
        message = request.POST.get('message', '')
        type_notification = request.POST.get('type', Notification.TYPE_INFO)
        
        if not titre or not message:
            messages.error(request, "Le titre et le message sont obligatoires.")
        else:
            # Créer une notification pour chaque candidat accepté
            notifications_creees = 0
            for candidature in candidats_acceptes:
                Notification.objects.create(
                    recipient=candidature.candidat,
                    title=titre,
                    message=message,
                    type=type_notification,
                    created_by=request.user,
                )
                notifications_creees += 1
            
            messages.success(
                request, 
                f"Notifications envoyées avec succès à {notifications_creees} candidat(s) accepté(s)."
            )
            return redirect('notifications_candidats')
    
    context = {
        'appel_offre': appel_offre,
        'candidats_acceptes': candidats_acceptes,
        'nb_candidats': candidats_acceptes.count(),
        'type_choices': Notification.TYPE_CHOICES,
    }
    
    return render(request, "admin/envoyer_notifications_candidats.html", context)
