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
from mairie.models import (
    ConfigurationMairie,
    VisiteSite,
    CampagnePublicitaire,
    Publicite,
    Suggestion,
)

from acteurs.models import ActeurEconomique, InstitutionFinanciere
from emploi.models import ProfilEmploi
from mairie.models import Candidature, AppelOffre
from comptes.models import Notification
from diaspora.models import MembreDiaspora
from django.utils.html import escape
from django.utils.text import slugify
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


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


def politique_cookies(request):
    """
    Page d'information sur les cookies (conformité / transparence).
    Le consentement est géré côté client via le cookie 'cookie_consent'.
    """
    return render(request, "legal/politique_cookies.html", {})


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
        'diaspora': MembreDiaspora.objects.count(),
        'candidatures': Candidature.objects.count(),
        'suggestions': Suggestion.objects.count(),
        'total_inscriptions': (
            ActeurEconomique.objects.count() +
            InstitutionFinanciere.objects.count() +
            ProfilEmploi.objects.count() +
            MembreDiaspora.objects.count()
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
        'diaspora': get_counts(MembreDiaspora.objects.all(), 'date_inscription'),
        'visites': get_counts(VisiteSite.objects.all(), 'date'),
    }
    
    # Nombre total de visites sur les 30 derniers jours (toutes pages confondues)
    total_visites_30j = VisiteSite.objects.filter(date__gte=start_date, date__lte=end_date).count()

    # Données pour la carte : acteurs économiques et institutions avec géolocalisation
    map_markers = []
    for a in ActeurEconomique.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True):
        try:
            map_markers.append({
                "nom": a.raison_sociale,
                "lat": float(a.latitude),
                "lng": float(a.longitude),
                "type": "acteur",
            })
        except (TypeError, ValueError):
            pass
    for i in InstitutionFinanciere.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True):
        try:
            map_markers.append({
                "nom": i.nom_institution,
                "lat": float(i.latitude),
                "lng": float(i.longitude),
                "type": "institution",
            })
        except (TypeError, ValueError):
            pass

    context = {
        'stats': stats,
        'chart_data_json': json.dumps(chart_data, cls=DjangoJSONEncoder),
        'total_visites_30j': total_visites_30j,
        'map_markers_json': json.dumps(map_markers, ensure_ascii=False),
    }
    
    return render(request, "admin/tableau_bord.html", context)


@login_required
@user_passes_test(is_staff_user)
def gestion_publicites(request):
    """Gestion des campagnes publicitaires (validation, paiement, activation)."""

    # Filtrage par statut optionnel
    statut = request.GET.get("statut", "")

    campagnes = CampagnePublicitaire.objects.select_related("proprietaire").order_by(
        "-date_demande"
    )
    if statut:
        campagnes = campagnes.filter(statut=statut)

    if request.method == "POST":
        campagne_id = request.POST.get("campagne_id")
        action = request.POST.get("action")
        campagne = get_object_or_404(CampagnePublicitaire, pk=campagne_id)

        if action == "set_statut":
            nouveau_statut = request.POST.get("nouveau_statut")
            if nouveau_statut in dict(CampagnePublicitaire.STATUT_CHOICES):
                ancien_statut = campagne.statut
                campagne.statut = nouveau_statut
                campagne.save()

                # Notification automatique au demandeur quand la mairie accepte la demande
                if ancien_statut != "acceptee" and nouveau_statut == "acceptee":
                    montant_txt = (
                        f"{campagne.montant:,.0f} FCFA".replace(",", " ")
                        if campagne.montant is not None
                        else "le montant indiqué par la mairie"
                    )
                    Notification.objects.create(
                        recipient=campagne.proprietaire,
                        title="Votre campagne publicitaire a été acceptée",
                        message=(
                            f"Bonjour,\n\n"
                            f"Votre demande de campagne publicitaire « {campagne.titre} » a été acceptée par la mairie.\n\n"
                            f"Prochaine étape : paiement des frais de publicité ({montant_txt}).\n"
                            f"Merci de vous rapprocher du service compétent de la mairie pour effectuer le paiement et "
                            f"faire enregistrer votre règlement.\n\n"
                            f"Après enregistrement du paiement, vous pourrez créer vos publicités depuis votre compte."
                        ),
                        type=Notification.TYPE_INFO,
                        created_by=request.user,
                    )
                messages.success(
                    request,
                    f"Le statut de la campagne « {campagne.titre} » a été mis à jour ({campagne.get_statut_display()}).",
                )
        elif action == "update_montant":
            montant = request.POST.get("montant") or ""
            try:
                campagne.montant = float(montant.replace(",", ".") or 0)
                campagne.save()
                messages.success(
                    request,
                    f"Le montant de la campagne « {campagne.titre} » a été mis à jour.",
                )
            except ValueError:
                messages.error(request, "Montant invalide.")
        elif action == "set_dates":
            date_debut = request.POST.get("date_debut") or ""
            date_fin = request.POST.get("date_fin") or ""
            try:
                campagne.date_debut = (
                    datetime.strptime(date_debut, "%Y-%m-%dT%H:%M")
                    if date_debut
                    else None
                )
                campagne.date_fin = (
                    datetime.strptime(date_fin, "%Y-%m-%dT%H:%M") if date_fin else None
                )
                campagne.save()
                messages.success(
                    request,
                    f"Les dates de diffusion de la campagne « {campagne.titre} » ont été mises à jour.",
                )
            except ValueError:
                messages.error(request, "Format de date invalide.")
        elif action == "renew_campaign":
            # Renouveler une campagne terminée : on crée une nouvelle période à partir
            # de maintenant (ou de l'ancienne date de fin si elle est dans le futur)
            maintenant = timezone.now()
            point_depart = campagne.date_fin or maintenant
            if point_depart < maintenant:
                point_depart = maintenant

            # Utilise la durée de la campagne pour recalculer la nouvelle date de fin
            duree = campagne.duree_jours or 30
            campagne.date_debut = point_depart
            campagne.date_fin = point_depart + timedelta(days=duree)
            campagne.statut = "active"
            campagne.save()
            messages.success(
                request,
                (
                    f"La campagne « {campagne.titre} » a été renouvelée. "
                    f"Nouvelle période du {campagne.date_debut.strftime('%d/%m/%Y %H:%M')} "
                    f"au {campagne.date_fin.strftime('%d/%m/%Y %H:%M')}."
                ),
            )

        return redirect("gestion_publicites")

    # Pré-calcul du nombre de publicités par campagne
    campagnes = campagnes.annotate(nb_publicites=Count("publicites"))

    context = {
        "campagnes": campagnes,
        "statut": statut,
    }
    return render(request, "admin/gestion_publicites.html", context)


@login_required
@user_passes_test(is_staff_user)
def detail_campagne_publicite(request, pk: int):
    """Détail d'une demande/campagne publicitaire (vue admin tableau de bord)."""

    campagne = get_object_or_404(
        CampagnePublicitaire.objects.select_related("proprietaire"), pk=pk
    )
    publicites = Publicite.objects.filter(campagne=campagne).order_by("-date_creation")

    # Envoi optionnel d'instructions de paiement personnalisées
    if request.method == "POST":
        titre = request.POST.get("titre", "").strip() or "Paiement de votre campagne publicitaire"
        message_libre = request.POST.get("message", "").strip()
        moyens = []
        if request.POST.get("tmoney"):
            moyens.append("Tmoney")
        if request.POST.get("flooz"):
            moyens.append("Flooz")
        if request.POST.get("carte"):
            moyens.append("Carte bancaire")

        if not message_libre:
            messages.error(request, "Le message d'explication du paiement est obligatoire.")
        else:
            lignes = [
                "Bonjour,",
                "",
                f"Votre campagne publicitaire « {campagne.titre} » est en cours de traitement par la mairie.",
                "",
            ]
            if moyens:
                lignes.append(
                    "Vous pouvez effectuer le paiement de vos frais de publicité via : "
                    + ", ".join(moyens)
                    + "."
                )
                lignes.append("")
            lignes.append(message_libre)
            lignes.append("")
            lignes.append(
                "Après validation de votre paiement par la mairie, vous pourrez créer vos publicités "
                "depuis votre compte sur la plateforme."
            )

            Notification.objects.create(
                recipient=campagne.proprietaire,
                title=titre,
                message="\n".join(lignes),
                type=Notification.TYPE_INFO,
                created_by=request.user,
            )
            messages.success(
                request,
                "Les instructions de paiement ont été envoyées au demandeur dans son espace personnel.",
            )
            return redirect("detail_campagne_publicite", pk=campagne.pk)

    context = {
        "campagne": campagne,
        "publicites": publicites,
    }
    return render(request, "admin/detail_campagne_publicite.html", context)


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
def liste_diaspora_tableau_bord(request):
    """Liste des membres de la diaspora pour le tableau de bord."""
    
    membres = MembreDiaspora.objects.all().order_by('-date_inscription')
    
    # Récupération des paramètres de filtrage
    q = request.GET.get('q', '')
    pays = request.GET.get('pays', '')
    secteur = request.GET.get('secteur', '')
    
    # Application des filtres
    if q:
        membres = membres.filter(
            Q(nom__icontains=q) |
            Q(prenoms__icontains=q) |
            Q(email__icontains=q) |
            Q(telephone_whatsapp__icontains=q) |
            Q(profession_actuelle__icontains=q) |
            Q(domaine_formation__icontains=q)
        )
        
    if pays:
        membres = membres.filter(pays_residence_actuelle__icontains=pays)
        
    if secteur:
        membres = membres.filter(secteur_activite=secteur)
    
    context = {
        'membres': membres,
        'titre': '🌍 Membres de la Diaspora',
        'secteur_choices': MembreDiaspora.SECTEUR_ACTIVITE_CHOICES,
        'current_filters': {
            'q': q,
            'pays': pays,
            'secteur': secteur
        }
    }
    
    return render(request, "admin/liste_diaspora.html", context)


@login_required
@user_passes_test(is_staff_user)
def detail_suggestion(request, pk):
    """Affiche le détail d'une suggestion."""
    
    suggestion = get_object_or_404(Suggestion, pk=pk)
    
    # Marquer automatiquement comme lue si ce n'est pas déjà fait
    if not suggestion.est_lue:
        suggestion.est_lue = True
        if not suggestion.date_lecture:
            suggestion.date_lecture = timezone.now()
        suggestion.save()
    
    context = {
        'suggestion': suggestion,
    }
    
    return render(request, "admin/detail_suggestion.html", context)


@login_required
@user_passes_test(is_staff_user)
def liste_suggestions(request):
    """Liste des suggestions soumises par les visiteurs."""
    
    suggestions = Suggestion.objects.all().order_by('-date_soumission')
    
    # Récupération des paramètres de filtrage
    q = request.GET.get('q', '')
    est_lue = request.GET.get('est_lue', '')
    
    # Application des filtres
    if q:
        suggestions = suggestions.filter(
            Q(nom__icontains=q) |
            Q(email__icontains=q) |
            Q(telephone__icontains=q) |
            Q(sujet__icontains=q) |
            Q(message__icontains=q)
        )
    
    if est_lue == 'oui':
        suggestions = suggestions.filter(est_lue=True)
    elif est_lue == 'non':
        suggestions = suggestions.filter(est_lue=False)
    
    context = {
        'suggestions': suggestions,
        'titre': 'Suggestions des Visiteurs',
        'current_filters': {
            'q': q,
            'est_lue': est_lue
        }
    }
    
    return render(request, "admin/liste_suggestions.html", context)


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
    
    # Créer une liste triée des appels d'offres avec candidatures acceptées pour faciliter l'affichage
    appels_avec_acceptees = [
        (appel_id, info) 
        for appel_id, info in appels_offres_avec_candidatures.items() 
        if info['nb_acceptees'] > 0
    ]
    
    context = {
        'candidatures': candidatures,
        'appels_offres_avec_candidatures': appels_offres_avec_candidatures,
        'appels_avec_acceptees': appels_avec_acceptees,
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
        'diaspora': MembreDiaspora,
        'suggestion': Suggestion,
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
    elif model_name == 'suggestion':
        if action == 'marquer_lue':
            obj.est_lue = True
            if not obj.date_lecture:
                obj.date_lecture = timezone.now()
            messages.success(request, f"Suggestion de {obj.nom} marquée comme lue.")
    else:
        # Pour les autres modèles, on utilise est_valide_par_mairie
        if action == 'accepter':
            obj.est_valide_par_mairie = True
            messages.success(request, f"{obj} validé avec succès.")
        elif action in ['refuser', 'rejeter']:
            obj.est_valide_par_mairie = False
            messages.warning(request, f"{obj} refusé/invalidé.")
            
    obj.save()
    
    # Vérifier si une redirection personnalisée est demandée
    redirect_to = request.POST.get('redirect_to')
    if redirect_to:
        return redirect(redirect_to)
    
    # Redirection vers la liste appropriée
    redirect_map = {
        'candidature': 'liste_candidatures',
        'acteur': 'liste_acteurs',
        'institution': 'liste_institutions',
        'jeune': 'liste_jeunes',
        'retraite': 'liste_retraites',
        'diaspora': 'liste_diaspora_tableau_bord',
        'suggestion': 'liste_suggestions',
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
def export_pdf_diaspora_detail(request, pk):
    """Génère un PDF détaillé pour un membre de la diaspora."""
    membre = get_object_or_404(MembreDiaspora, pk=pk)
    
    # Récupérer les appuis financiers
    appuis_financiers = []
    if membre.appui_investissement_projets:
        appuis_financiers.append("Investissement dans des projets communaux")
    if membre.appui_financement_infrastructures:
        appuis_financiers.append("Financement d'infrastructures")
    if membre.appui_parrainage_communautaire:
        appuis_financiers.append("Parrainage de projets communautaires")
    if membre.appui_jeunes_femmes_entrepreneurs:
        appuis_financiers.append("Appui aux jeunes et femmes entrepreneurs")
    
    # Récupérer les compétences techniques
    competences_techniques = []
    if membre.transfert_competences:
        competences_techniques.append("Transfert de compétences")
    if membre.formation_jeunes:
        competences_techniques.append("Formation des jeunes")
    if membre.appui_digitalisation:
        competences_techniques.append("Appui à la digitalisation")
    if membre.conseils_techniques:
        competences_techniques.append("Conseils techniques / expertise")
    if membre.encadrement_mentorat:
        competences_techniques.append("Encadrement à distance (mentorat)")
    
    # Création d'emplois
    creation_emplois = []
    if membre.creation_entreprise_locale:
        creation_emplois.append("Création d'entreprise locale")
    if membre.appui_pme_locales:
        creation_emplois.append("Appui aux PME locales")
    if membre.recrutement_jeunes_commune:
        creation_emplois.append("Recrutement de jeunes de la commune")
    
    # Partenariats
    partenariats = []
    if membre.mise_relation_ong:
        partenariats.append("Mise en relation avec ONG")
    if membre.cooperation_decentralisee:
        partenariats.append("Coopération décentralisée")
    if membre.recherche_financements_internationaux:
        partenariats.append("Recherche de financements internationaux")
    if membre.promotion_commune_international:
        partenariats.append("Promotion de la commune à l'international")
    
    # Engagement citoyen
    engagement_citoyen = []
    if membre.participation_activites_communales:
        engagement_citoyen.append("Participation aux activités communales")
    if membre.participation_reunions_diaspora:
        engagement_citoyen.append("Participation aux réunions de la diaspora")
    if membre.appui_actions_sociales_culturelles:
        engagement_citoyen.append("Appui aux actions sociales et culturelles")
    
    sections = [
        (
            "Informations d'identification",
            [
                ("Nom", membre.nom),
                ("Prénoms", membre.prenoms),
                ("Sexe", membre.get_sexe_display()),
                ("Date de naissance", membre.date_naissance),
                ("Nationalité(s)", membre.nationalites),
                ("Numéro de pièce d'identité", membre.numero_piece_identite),
            ],
        ),
        (
            "Résidence actuelle",
            [
                ("Pays de résidence", membre.pays_residence_actuelle),
                ("Ville de résidence", membre.ville_residence_actuelle),
                ("Adresse complète à l'étranger", membre.adresse_complete_etranger),
            ],
        ),
        (
            "Lien avec la commune",
            [
                ("Commune d'origine", membre.commune_origine),
                ("Quartier / Village d'origine", membre.quartier_village_origine),
                ("Nom du parent/tuteur originaire", membre.nom_parent_tuteur_originaire),
                ("Année de départ du pays", membre.annee_depart_pays),
                ("Fréquence de retour au pays", membre.get_frequence_retour_pays_display()),
            ],
        ),
        (
            "Informations de contact",
            [
                ("Téléphone (WhatsApp)", membre.telephone_whatsapp),
                ("Email", membre.email),
                ("Réseaux sociaux", membre.reseaux_sociaux or "Non renseigné"),
                ("Contact au pays - Nom", membre.contact_au_pays_nom),
                ("Contact au pays - Téléphone", membre.contact_au_pays_telephone),
            ],
        ),
        (
            "Situation professionnelle",
            [
                ("Niveau d'études", membre.get_niveau_etudes_display()),
                ("Domaine de formation", membre.domaine_formation),
                ("Profession actuelle", membre.profession_actuelle),
                ("Secteur d'activité", membre.get_secteur_activite_display()),
                ("Secteur d'activité (autre)", membre.secteur_activite_autre or "Non renseigné"),
                ("Années d'expérience", membre.annees_experience),
                ("Statut professionnel", membre.get_statut_professionnel_display()),
                ("Type de titre de séjour", membre.type_titre_sejour or "Non renseigné"),
            ],
        ),
        (
            "Appui financier proposé",
            [
                ("Types d'appui", ", ".join(appuis_financiers) if appuis_financiers else "Aucun"),
            ],
        ),
        (
            "Appui technique & compétences",
            [
                ("Compétences proposées", ", ".join(competences_techniques) if competences_techniques else "Aucune"),
            ],
        ),
        (
            "Création d'emplois",
            [
                ("Actions proposées", ", ".join(creation_emplois) if creation_emplois else "Aucune"),
            ],
        ),
        (
            "Partenariats & relations internationales",
            [
                ("Actions proposées", ", ".join(partenariats) if partenariats else "Aucune"),
            ],
        ),
        (
            "Engagement citoyen",
            [
                ("Actions proposées", ", ".join(engagement_citoyen) if engagement_citoyen else "Aucune"),
            ],
        ),
        (
            "Questions clés",
            [
                ("Comment souhaitez-vous contribuer ?", membre.comment_contribuer),
                ("Disposition à participer", membre.get_disposition_participation_display()),
                ("Domaine d'intervention prioritaire", membre.domaine_intervention_prioritaire),
            ],
        ),
        (
            "Validation et métadonnées",
            [
                ("Accepte RGPD", membre.accepte_rgpd),
                ("Accepte d'être contacté", membre.accepte_contact),
                ("Validé par la mairie", membre.est_valide_par_mairie),
                ("Date d'inscription", membre.date_inscription),
                ("Date de modification", membre.date_modification),
            ],
        ),
    ]
    
    filename = _make_pdf_filename("diaspora", f"{membre.nom}-{membre.prenoms}")
    title = f"Fiche Membre de la Diaspora - {membre.nom} {membre.prenoms}"
    return _build_detail_pdf(filename, title, sections)


@login_required
@user_passes_test(is_staff_user)
def export_pdf_acteurs(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    type_acteur = request.GET.get("type") or ""
    secteur = request.GET.get("secteur") or ""

    # Uniquement les acteurs validés par la mairie
    qs = ActeurEconomique.objects.filter(est_valide_par_mairie=True)
    conf = ConfigurationMairie.objects.filter(est_active=True).first()
    if type_acteur:
        qs = qs.filter(type_acteur=type_acteur)
    if secteur:
        qs = qs.filter(secteur_activite=secteur)

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
    response["Content-Disposition"] = 'attachment; filename="acteurs_economiques_valides.pdf"'
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
def export_pdf_diaspora(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    pays = request.GET.get("pays") or ""

    # Uniquement les membres validés par la mairie
    qs = MembreDiaspora.objects.filter(est_valide_par_mairie=True)
    if pays:
        qs = qs.filter(pays_residence_actuelle__icontains=pays)
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
    response["Content-Disposition"] = 'attachment; filename="diaspora_valides.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#006233"), alignment=1, spaceAfter=12)
    story.append(Paragraph("Membres de la Diaspora", title_style))
    if start or end:
        story.append(Paragraph(f"Période: {start or '...'} au {end or '...'}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))
    data = [["Nom", "Prénoms", "Pays de résidence", "Ville", "Téléphone", "Email", "Profession"]]
    for m in qs.order_by("-date_inscription")[:1000]:
        data.append([
            m.nom,
            m.prenoms,
            m.pays_residence_actuelle[:25] if m.pays_residence_actuelle else "",
            m.ville_residence_actuelle[:20] if m.ville_residence_actuelle else "",
            m.telephone_whatsapp[:15] if m.telephone_whatsapp else "",
            m.email[:30] if m.email else "",
            m.profession_actuelle[:30] if m.profession_actuelle else "",
        ])
    table = Table(data, colWidths=[3.5*cm, 4*cm, 4*cm, 3.5*cm, 3.5*cm, 5*cm, 4.5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
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


# ========== FONCTIONS D'EXPORT EXCEL ==========

def _format_excel_value(value):
    """Formate une valeur pour l'export Excel."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Oui" if value else "Non"
    if isinstance(value, (datetime, date)):
        return value.strftime("%d/%m/%Y %H:%M") if isinstance(value, datetime) else value.strftime("%d/%m/%Y")
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value if item)
    return str(value)


def _style_excel_header(ws, row_num):
    """Applique un style au header Excel."""
    header_fill = PatternFill(start_color="006233", end_color="006233", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    for cell in ws[row_num]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border


@login_required
@user_passes_test(is_staff_user)
def export_excel_acteurs(request):
    """Exporte tous les acteurs économiques en Excel avec tous les champs."""
    acteurs = ActeurEconomique.objects.all().order_by('-date_enregistrement')
    
    # Appliquer les filtres comme dans la vue liste
    q = request.GET.get('q', '')
    type_acteur = request.GET.get('type', '')
    secteur = request.GET.get('secteur', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Acteurs Economiques"
    
    # En-têtes
    headers = [
        "ID", "Raison sociale", "Sigle", "Type d'acteur", "Secteur d'activité", "Statut juridique",
        "Description", "RCCM", "CFE", "N° Carte opérateur", "NIF", "Date de création",
        "Capital social (FCFA)", "Nom responsable", "Fonction responsable", "Téléphone 1",
        "Téléphone 2", "Email", "Site web", "Quartier", "Canton", "Adresse complète",
        "Situation", "Latitude", "Longitude", "Nombre d'employés", "Chiffre d'affaires",
        "Accepte publication", "Certifie informations", "Accepte conditions",
        "Validé par mairie", "Date d'enregistrement"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for acteur in acteurs:
        row = [
            acteur.pk,
            acteur.raison_sociale,
            acteur.sigle or "",
            acteur.get_type_acteur_display(),
            acteur.get_secteur_activite_display(),
            acteur.get_statut_juridique_display(),
            acteur.description,
            acteur.rccm or "",
            acteur.cfe or "",
            acteur.numero_carte_operateur or "",
            acteur.nif or "",
            _format_excel_value(acteur.date_creation),
            acteur.capital_social if acteur.capital_social else "",
            acteur.nom_responsable,
            acteur.fonction_responsable,
            acteur.telephone1,
            acteur.telephone2 or "",
            acteur.email,
            acteur.site_web or "",
            acteur.quartier,
            acteur.canton or "",
            acteur.adresse_complete,
            acteur.get_situation_display(),
            acteur.latitude if acteur.latitude else "",
            acteur.longitude if acteur.longitude else "",
            acteur.get_nombre_employes_display() if acteur.nombre_employes else "",
            acteur.get_chiffre_affaires_display() if acteur.chiffre_affaires else "",
            "Oui" if acteur.accepte_public else "Non",
            "Oui" if acteur.certifie_information else "Non",
            "Oui" if acteur.accepte_conditions else "Non",
            "Oui" if acteur.est_valide_par_mairie else "Non",
            _format_excel_value(acteur.date_enregistrement),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="acteurs_economiques.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_institutions(request):
    """Exporte toutes les institutions financières en Excel avec tous les champs."""
    institutions = InstitutionFinanciere.objects.all().order_by('-date_enregistrement')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    type_inst = request.GET.get('type', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Institutions Financieres"
    
    # En-têtes
    headers = [
        "ID", "Nom institution", "Sigle", "Type institution", "Année création",
        "N° Agrément", "IFU", "Description services", "Services disponibles",
        "Taux crédit", "Taux épargne", "Conditions éligibilité", "Public cible",
        "Nom responsable", "Fonction responsable", "Téléphone 1", "Téléphone 2",
        "WhatsApp", "Email", "Site web", "Facebook", "Quartier", "Canton",
        "Adresse complète", "Situation", "Latitude", "Longitude", "Nombre agences",
        "Horaires", "Certifie informations", "Accepte publication", "Accepte contact",
        "Engagement", "Validé par mairie", "Date d'enregistrement"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for inst in institutions:
        services_text = ", ".join(part.strip().title() for part in inst.services.split(",") if part.strip()) if inst.services else ""
        row = [
            inst.pk,
            inst.nom_institution,
            inst.sigle or "",
            inst.get_type_institution_display(),
            inst.annee_creation if inst.annee_creation else "",
            inst.numero_agrement or "",
            inst.ifu or "",
            inst.description_services,
            services_text,
            inst.taux_credit or "",
            inst.taux_epargne or "",
            inst.conditions_eligibilite or "",
            inst.public_cible or "",
            inst.nom_responsable,
            inst.fonction_responsable,
            inst.telephone1,
            inst.telephone2 or "",
            inst.whatsapp or "",
            inst.email,
            inst.site_web or "",
            inst.facebook or "",
            inst.quartier,
            inst.canton or "",
            inst.adresse_complete,
            inst.get_situation_display(),
            inst.latitude if inst.latitude else "",
            inst.longitude if inst.longitude else "",
            inst.nombre_agences if inst.nombre_agences else "",
            inst.horaires,
            "Oui" if inst.certifie_info else "Non",
            "Oui" if inst.accepte_public else "Non",
            "Oui" if inst.accepte_contact else "Non",
            "Oui" if inst.engagement else "Non",
            "Oui" if inst.est_valide_par_mairie else "Non",
            _format_excel_value(inst.date_enregistrement),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="institutions_financieres.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_jeunes(request):
    """Exporte tous les jeunes demandeurs d'emploi en Excel avec tous les champs."""
    jeunes = ProfilEmploi.objects.filter(type_profil='jeune').order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    niveau = request.GET.get('niveau', '')
    dispo = request.GET.get('dispo', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Jeunes Demandeurs Emploi"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité",
        "Téléphone 1", "Téléphone 2", "Email", "Quartier", "Canton",
        "Adresse complète", "Résident Kloto 1", "Niveau étude", "Diplôme principal",
        "Domaine compétence", "Expériences", "Situation actuelle", "Employeur actuel",
        "Disponibilité", "Type contrat souhaité", "Salaire souhaité",
        "Service citoyen obligatoire", "Accepte RGPD", "Accepte contact",
        "Validé par mairie", "Date inscription"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for jeune in jeunes:
        row = [
            jeune.pk,
            jeune.nom,
            jeune.prenoms,
            jeune.get_sexe_display(),
            _format_excel_value(jeune.date_naissance),
            jeune.nationalite or "",
            jeune.telephone1,
            jeune.telephone2 or "",
            jeune.email,
            jeune.quartier,
            jeune.canton or "",
            jeune.adresse_complete,
            "Oui" if jeune.est_resident_kloto else "Non",
            jeune.get_niveau_etude_display() if jeune.niveau_etude else "",
            jeune.diplome_principal or "",
            jeune.domaine_competence,
            jeune.experiences or "",
            jeune.get_situation_actuelle_display(),
            jeune.employeur_actuel or "",
            jeune.get_disponibilite_display(),
            jeune.get_type_contrat_souhaite_display() if jeune.type_contrat_souhaite else "",
            jeune.salaire_souhaite or "",
            "Oui" if jeune.service_citoyen_obligatoire else "Non",
            "Oui" if jeune.accepte_rgpd else "Non",
            "Oui" if jeune.accepte_contact else "Non",
            "Oui" if jeune.est_valide_par_mairie else "Non",
            _format_excel_value(jeune.date_inscription),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="jeunes_demandeurs_emploi.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_retraites(request):
    """Exporte tous les retraités actifs en Excel avec tous les champs."""
    retraites = ProfilEmploi.objects.filter(type_profil='retraite').order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    niveau = request.GET.get('niveau', '')
    dispo = request.GET.get('dispo', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Retraites Actifs"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité",
        "Téléphone 1", "Téléphone 2", "Email", "Quartier", "Canton",
        "Adresse complète", "Résident Kloto 1", "Niveau étude", "Diplôme principal",
        "Domaine compétence", "Expériences", "Situation actuelle", "Employeur actuel",
        "Disponibilité", "Type contrat souhaité", "Salaire souhaité",
        "Caisse retraite", "Dernier poste", "Années expérience",
        "Accepte RGPD", "Accepte contact", "Validé par mairie", "Date inscription"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for retraite in retraites:
        row = [
            retraite.pk,
            retraite.nom,
            retraite.prenoms,
            retraite.get_sexe_display(),
            _format_excel_value(retraite.date_naissance),
            retraite.nationalite or "",
            retraite.telephone1,
            retraite.telephone2 or "",
            retraite.email,
            retraite.quartier,
            retraite.canton or "",
            retraite.adresse_complete,
            "Oui" if retraite.est_resident_kloto else "Non",
            retraite.get_niveau_etude_display() if retraite.niveau_etude else "",
            retraite.diplome_principal or "",
            retraite.domaine_competence,
            retraite.experiences or "",
            retraite.get_situation_actuelle_display(),
            retraite.employeur_actuel or "",
            retraite.get_disponibilite_display(),
            retraite.get_type_contrat_souhaite_display() if retraite.type_contrat_souhaite else "",
            retraite.salaire_souhaite or "",
            retraite.caisse_retraite or "",
            retraite.dernier_poste or "",
            retraite.annees_experience if retraite.annees_experience else "",
            "Oui" if retraite.accepte_rgpd else "Non",
            "Oui" if retraite.accepte_contact else "Non",
            "Oui" if retraite.est_valide_par_mairie else "Non",
            _format_excel_value(retraite.date_inscription),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="retraites_actifs.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_diaspora(request):
    """Exporte tous les membres de la diaspora en Excel avec tous les champs."""
    membres = MembreDiaspora.objects.all().order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    pays = request.GET.get('pays', '')
    secteur = request.GET.get('secteur', '')
    
    if q:
        membres = membres.filter(
            Q(nom__icontains=q) |
            Q(prenoms__icontains=q) |
            Q(email__icontains=q) |
            Q(telephone_whatsapp__icontains=q) |
            Q(profession_actuelle__icontains=q) |
            Q(domaine_formation__icontains=q)
        )
    if pays:
        membres = membres.filter(pays_residence_actuelle__icontains=pays)
    if secteur:
        membres = membres.filter(secteur_activite=secteur)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Membres Diaspora"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité(s)",
        "N° Pièce identité", "Pays résidence", "Ville résidence", "Adresse étranger",
        "Commune origine", "Quartier/Village origine", "Nom parent/tuteur", "Année départ",
        "Fréquence retour", "Téléphone WhatsApp", "Email", "Réseaux sociaux",
        "Contact pays - Nom", "Contact pays - Téléphone", "Niveau études",
        "Domaine formation", "Profession actuelle", "Secteur activité",
        "Secteur activité (autre)", "Années expérience", "Statut professionnel",
        "Type titre séjour", "Appui investissement projets", "Appui financement infrastructures",
        "Appui parrainage communautaire", "Appui jeunes/femmes entrepreneurs",
        "Transfert compétences", "Formation jeunes", "Appui digitalisation",
        "Conseils techniques", "Encadrement mentorat", "Création entreprise locale",
        "Appui PME locales", "Recrutement jeunes commune", "Mise relation ONG",
        "Coopération décentralisée", "Recherche financements internationaux",
        "Promotion commune international", "Participation activités communales",
        "Participation réunions diaspora", "Appui actions sociales/culturelles",
        "Comment contribuer", "Disposition participation", "Domaine intervention prioritaire",
        "Accepte RGPD", "Accepte contact", "Validé par mairie", "Date inscription", "Date modification"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for membre in membres:
        row = [
            membre.pk,
            membre.nom,
            membre.prenoms,
            membre.get_sexe_display(),
            _format_excel_value(membre.date_naissance),
            membre.nationalites,
            membre.numero_piece_identite,
            membre.pays_residence_actuelle,
            membre.ville_residence_actuelle,
            membre.adresse_complete_etranger,
            membre.commune_origine,
            membre.quartier_village_origine,
            membre.nom_parent_tuteur_originaire,
            membre.annee_depart_pays,
            membre.get_frequence_retour_pays_display(),
            membre.telephone_whatsapp,
            membre.email,
            membre.reseaux_sociaux or "",
            membre.contact_au_pays_nom,
            membre.contact_au_pays_telephone,
            membre.get_niveau_etudes_display(),
            membre.domaine_formation,
            membre.profession_actuelle,
            membre.get_secteur_activite_display(),
            membre.secteur_activite_autre or "",
            membre.annees_experience,
            membre.get_statut_professionnel_display(),
            membre.type_titre_sejour or "",
            "Oui" if membre.appui_investissement_projets else "Non",
            "Oui" if membre.appui_financement_infrastructures else "Non",
            "Oui" if membre.appui_parrainage_communautaire else "Non",
            "Oui" if membre.appui_jeunes_femmes_entrepreneurs else "Non",
            "Oui" if membre.transfert_competences else "Non",
            "Oui" if membre.formation_jeunes else "Non",
            "Oui" if membre.appui_digitalisation else "Non",
            "Oui" if membre.conseils_techniques else "Non",
            "Oui" if membre.encadrement_mentorat else "Non",
            "Oui" if membre.creation_entreprise_locale else "Non",
            "Oui" if membre.appui_pme_locales else "Non",
            "Oui" if membre.recrutement_jeunes_commune else "Non",
            "Oui" if membre.mise_relation_ong else "Non",
            "Oui" if membre.cooperation_decentralisee else "Non",
            "Oui" if membre.recherche_financements_internationaux else "Non",
            "Oui" if membre.promotion_commune_international else "Non",
            "Oui" if membre.participation_activites_communales else "Non",
            "Oui" if membre.participation_reunions_diaspora else "Non",
            "Oui" if membre.appui_actions_sociales_culturelles else "Non",
            membre.comment_contribuer,
            membre.get_disposition_participation_display(),
            membre.domaine_intervention_prioritaire,
            "Oui" if membre.accepte_rgpd else "Non",
            "Oui" if membre.accepte_contact else "Non",
            "Oui" if membre.est_valide_par_mairie else "Non",
            _format_excel_value(membre.date_inscription),
            _format_excel_value(membre.date_modification),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="membres_diaspora.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_candidatures(request):
    """Exporte toutes les candidatures en Excel avec tous les champs."""
    candidatures = Candidature.objects.all().select_related('appel_offre', 'candidat').order_by('-date_soumission')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    statut = request.GET.get('statut', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Candidatures"
    
    # En-têtes
    headers = [
        "ID", "Appel d'offres - Titre", "Appel d'offres - Référence", "Appel d'offres - Description",
        "Appel d'offres - Public cible", "Appel d'offres - Date début", "Appel d'offres - Date fin",
        "Appel d'offres - Budget estimé", "Candidat - Username", "Candidat - Nom", "Candidat - Prénom",
        "Candidat - Email", "Statut candidature", "Message accompagnement", "Date soumission"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for candidature in candidatures:
        row = [
            candidature.pk,
            candidature.appel_offre.titre,
            candidature.appel_offre.reference or "",
            candidature.appel_offre.description,
            candidature.appel_offre.get_public_cible_display(),
            _format_excel_value(candidature.appel_offre.date_debut),
            _format_excel_value(candidature.appel_offre.date_fin),
            candidature.appel_offre.budget_estime if candidature.appel_offre.budget_estime else "",
            candidature.candidat.username,
            candidature.candidat.last_name or "",
            candidature.candidat.first_name or "",
            candidature.candidat.email,
            candidature.get_statut_display(),
            candidature.message_accompagnement or "",
            _format_excel_value(candidature.date_soumission),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 25
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="candidatures.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_pdf_entreprises(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    secteur = request.GET.get("secteur") or ""

    # Uniquement les entreprises validées
    qs = ActeurEconomique.objects.filter(type_acteur="entreprise", est_valide_par_mairie=True)
    if secteur:
        qs = qs.filter(secteur_activite=secteur)
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
    response["Content-Disposition"] = 'attachment; filename="entreprises_valides.pdf"'
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
def export_pdf_institutions(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    type_inst = request.GET.get("type") or ""

    # Uniquement les institutions validées
    qs = InstitutionFinanciere.objects.filter(est_valide_par_mairie=True)
    if type_inst:
        qs = qs.filter(type_institution=type_inst)

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
    response["Content-Disposition"] = 'attachment; filename="institutions_financieres_valides.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#006233"),
        alignment=1,
        spaceAfter=12,
    )
    story.append(Paragraph("Institutions Financières Validées", title_style))
    if start or end:
        story.append(
            Paragraph(f"Période: {start or '...'} au {end or '...'}", styles["Normal"])
        )
    story.append(Spacer(1, 0.4 * cm))
    data = [["Nom de l'institution", "Type", "Responsable", "Téléphone", "Quartier"]]
    for inst in qs.order_by("-date_enregistrement")[:1000]:
        data.append(
            [
                inst.nom_institution,
                inst.get_type_institution_display(),
                inst.nom_responsable,
                inst.telephone1,
                inst.quartier,
            ]
        )
    table = Table(data, colWidths=[8 * cm, 6 * cm, 6 * cm, 4 * cm, 5 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F5E9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.6 * cm))
    story.append(
        Paragraph(
            "Date et Signature : ________________________________", styles["Normal"]
        )
    )

    def on_page(c, d):
        width, height = d.pagesize
        y = height - 40
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(45)
        c.setFont("Helvetica-Bold", 36)
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.drawCentredString(
            0,
            0,
            (conf.nom_commune if conf else "Mairie de Kloto 1").upper(),
        )
        c.restoreState()
        if conf and getattr(conf, "logo", None) and getattr(conf.logo, "path", None):
            try:
                c.drawImage(
                    conf.logo.path,
                    40,
                    y - 30,
                    width=40,
                    height=40,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception:
                pass
        c.setFont("Helvetica-Bold", 12)
        c.drawString(
            100,
            y,
            f"République Togolaise – {conf.nom_commune if conf else 'Mairie de Kloto 1'}",
        )

        c.setFont("Helvetica", 9)
        c.drawString(40, 30, timezone.now().strftime("Édité le %d/%m/%Y %H:%M"))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page, canvasmaker=NumberedCanvas)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_pdf_diaspora(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    pays = request.GET.get("pays") or ""

    # Uniquement les membres validés par la mairie
    qs = MembreDiaspora.objects.filter(est_valide_par_mairie=True)
    if pays:
        qs = qs.filter(pays_residence_actuelle__icontains=pays)
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
    response["Content-Disposition"] = 'attachment; filename="diaspora_valides.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#006233"), alignment=1, spaceAfter=12)
    story.append(Paragraph("Membres de la Diaspora", title_style))
    if start or end:
        story.append(Paragraph(f"Période: {start or '...'} au {end or '...'}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))
    data = [["Nom", "Prénoms", "Pays de résidence", "Ville", "Téléphone", "Email", "Profession"]]
    for m in qs.order_by("-date_inscription")[:1000]:
        data.append([
            m.nom,
            m.prenoms,
            m.pays_residence_actuelle[:25] if m.pays_residence_actuelle else "",
            m.ville_residence_actuelle[:20] if m.ville_residence_actuelle else "",
            m.telephone_whatsapp[:15] if m.telephone_whatsapp else "",
            m.email[:30] if m.email else "",
            m.profession_actuelle[:30] if m.profession_actuelle else "",
        ])
    table = Table(data, colWidths=[3.5*cm, 4*cm, 4*cm, 3.5*cm, 3.5*cm, 5*cm, 4.5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
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


# ========== FONCTIONS D'EXPORT EXCEL ==========

def _format_excel_value(value):
    """Formate une valeur pour l'export Excel."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Oui" if value else "Non"
    if isinstance(value, (datetime, date)):
        return value.strftime("%d/%m/%Y %H:%M") if isinstance(value, datetime) else value.strftime("%d/%m/%Y")
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value if item)
    return str(value)


def _style_excel_header(ws, row_num):
    """Applique un style au header Excel."""
    header_fill = PatternFill(start_color="006233", end_color="006233", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    for cell in ws[row_num]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border


@login_required
@user_passes_test(is_staff_user)
def export_excel_acteurs(request):
    """Exporte tous les acteurs économiques en Excel avec tous les champs."""
    acteurs = ActeurEconomique.objects.all().order_by('-date_enregistrement')
    
    # Appliquer les filtres comme dans la vue liste
    q = request.GET.get('q', '')
    type_acteur = request.GET.get('type', '')
    secteur = request.GET.get('secteur', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Acteurs Economiques"
    
    # En-têtes
    headers = [
        "ID", "Raison sociale", "Sigle", "Type d'acteur", "Secteur d'activité", "Statut juridique",
        "Description", "RCCM", "CFE", "N° Carte opérateur", "NIF", "Date de création",
        "Capital social (FCFA)", "Nom responsable", "Fonction responsable", "Téléphone 1",
        "Téléphone 2", "Email", "Site web", "Quartier", "Canton", "Adresse complète",
        "Situation", "Latitude", "Longitude", "Nombre d'employés", "Chiffre d'affaires",
        "Accepte publication", "Certifie informations", "Accepte conditions",
        "Validé par mairie", "Date d'enregistrement"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for acteur in acteurs:
        row = [
            acteur.pk,
            acteur.raison_sociale,
            acteur.sigle or "",
            acteur.get_type_acteur_display(),
            acteur.get_secteur_activite_display(),
            acteur.get_statut_juridique_display(),
            acteur.description,
            acteur.rccm or "",
            acteur.cfe or "",
            acteur.numero_carte_operateur or "",
            acteur.nif or "",
            _format_excel_value(acteur.date_creation),
            acteur.capital_social if acteur.capital_social else "",
            acteur.nom_responsable,
            acteur.fonction_responsable,
            acteur.telephone1,
            acteur.telephone2 or "",
            acteur.email,
            acteur.site_web or "",
            acteur.quartier,
            acteur.canton or "",
            acteur.adresse_complete,
            acteur.get_situation_display(),
            acteur.latitude if acteur.latitude else "",
            acteur.longitude if acteur.longitude else "",
            acteur.get_nombre_employes_display() if acteur.nombre_employes else "",
            acteur.get_chiffre_affaires_display() if acteur.chiffre_affaires else "",
            "Oui" if acteur.accepte_public else "Non",
            "Oui" if acteur.certifie_information else "Non",
            "Oui" if acteur.accepte_conditions else "Non",
            "Oui" if acteur.est_valide_par_mairie else "Non",
            _format_excel_value(acteur.date_enregistrement),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="acteurs_economiques.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_institutions(request):
    """Exporte toutes les institutions financières en Excel avec tous les champs."""
    institutions = InstitutionFinanciere.objects.all().order_by('-date_enregistrement')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    type_inst = request.GET.get('type', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Institutions Financieres"
    
    # En-têtes
    headers = [
        "ID", "Nom institution", "Sigle", "Type institution", "Année création",
        "N° Agrément", "IFU", "Description services", "Services disponibles",
        "Taux crédit", "Taux épargne", "Conditions éligibilité", "Public cible",
        "Nom responsable", "Fonction responsable", "Téléphone 1", "Téléphone 2",
        "WhatsApp", "Email", "Site web", "Facebook", "Quartier", "Canton",
        "Adresse complète", "Situation", "Latitude", "Longitude", "Nombre agences",
        "Horaires", "Certifie informations", "Accepte publication", "Accepte contact",
        "Engagement", "Validé par mairie", "Date d'enregistrement"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for inst in institutions:
        services_text = ", ".join(part.strip().title() for part in inst.services.split(",") if part.strip()) if inst.services else ""
        row = [
            inst.pk,
            inst.nom_institution,
            inst.sigle or "",
            inst.get_type_institution_display(),
            inst.annee_creation if inst.annee_creation else "",
            inst.numero_agrement or "",
            inst.ifu or "",
            inst.description_services,
            services_text,
            inst.taux_credit or "",
            inst.taux_epargne or "",
            inst.conditions_eligibilite or "",
            inst.public_cible or "",
            inst.nom_responsable,
            inst.fonction_responsable,
            inst.telephone1,
            inst.telephone2 or "",
            inst.whatsapp or "",
            inst.email,
            inst.site_web or "",
            inst.facebook or "",
            inst.quartier,
            inst.canton or "",
            inst.adresse_complete,
            inst.get_situation_display(),
            inst.latitude if inst.latitude else "",
            inst.longitude if inst.longitude else "",
            inst.nombre_agences if inst.nombre_agences else "",
            inst.horaires,
            "Oui" if inst.certifie_info else "Non",
            "Oui" if inst.accepte_public else "Non",
            "Oui" if inst.accepte_contact else "Non",
            "Oui" if inst.engagement else "Non",
            "Oui" if inst.est_valide_par_mairie else "Non",
            _format_excel_value(inst.date_enregistrement),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="institutions_financieres.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_jeunes(request):
    """Exporte tous les jeunes demandeurs d'emploi en Excel avec tous les champs."""
    jeunes = ProfilEmploi.objects.filter(type_profil='jeune').order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    niveau = request.GET.get('niveau', '')
    dispo = request.GET.get('dispo', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Jeunes Demandeurs Emploi"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité",
        "Téléphone 1", "Téléphone 2", "Email", "Quartier", "Canton",
        "Adresse complète", "Résident Kloto 1", "Niveau étude", "Diplôme principal",
        "Domaine compétence", "Expériences", "Situation actuelle", "Employeur actuel",
        "Disponibilité", "Type contrat souhaité", "Salaire souhaité",
        "Service citoyen obligatoire", "Accepte RGPD", "Accepte contact",
        "Validé par mairie", "Date inscription"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for jeune in jeunes:
        row = [
            jeune.pk,
            jeune.nom,
            jeune.prenoms,
            jeune.get_sexe_display(),
            _format_excel_value(jeune.date_naissance),
            jeune.nationalite or "",
            jeune.telephone1,
            jeune.telephone2 or "",
            jeune.email,
            jeune.quartier,
            jeune.canton or "",
            jeune.adresse_complete,
            "Oui" if jeune.est_resident_kloto else "Non",
            jeune.get_niveau_etude_display() if jeune.niveau_etude else "",
            jeune.diplome_principal or "",
            jeune.domaine_competence,
            jeune.experiences or "",
            jeune.get_situation_actuelle_display(),
            jeune.employeur_actuel or "",
            jeune.get_disponibilite_display(),
            jeune.get_type_contrat_souhaite_display() if jeune.type_contrat_souhaite else "",
            jeune.salaire_souhaite or "",
            "Oui" if jeune.service_citoyen_obligatoire else "Non",
            "Oui" if jeune.accepte_rgpd else "Non",
            "Oui" if jeune.accepte_contact else "Non",
            "Oui" if jeune.est_valide_par_mairie else "Non",
            _format_excel_value(jeune.date_inscription),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="jeunes_demandeurs_emploi.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_retraites(request):
    """Exporte tous les retraités actifs en Excel avec tous les champs."""
    retraites = ProfilEmploi.objects.filter(type_profil='retraite').order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    niveau = request.GET.get('niveau', '')
    dispo = request.GET.get('dispo', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Retraites Actifs"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité",
        "Téléphone 1", "Téléphone 2", "Email", "Quartier", "Canton",
        "Adresse complète", "Résident Kloto 1", "Niveau étude", "Diplôme principal",
        "Domaine compétence", "Expériences", "Situation actuelle", "Employeur actuel",
        "Disponibilité", "Type contrat souhaité", "Salaire souhaité",
        "Caisse retraite", "Dernier poste", "Années expérience",
        "Accepte RGPD", "Accepte contact", "Validé par mairie", "Date inscription"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for retraite in retraites:
        row = [
            retraite.pk,
            retraite.nom,
            retraite.prenoms,
            retraite.get_sexe_display(),
            _format_excel_value(retraite.date_naissance),
            retraite.nationalite or "",
            retraite.telephone1,
            retraite.telephone2 or "",
            retraite.email,
            retraite.quartier,
            retraite.canton or "",
            retraite.adresse_complete,
            "Oui" if retraite.est_resident_kloto else "Non",
            retraite.get_niveau_etude_display() if retraite.niveau_etude else "",
            retraite.diplome_principal or "",
            retraite.domaine_competence,
            retraite.experiences or "",
            retraite.get_situation_actuelle_display(),
            retraite.employeur_actuel or "",
            retraite.get_disponibilite_display(),
            retraite.get_type_contrat_souhaite_display() if retraite.type_contrat_souhaite else "",
            retraite.salaire_souhaite or "",
            retraite.caisse_retraite or "",
            retraite.dernier_poste or "",
            retraite.annees_experience if retraite.annees_experience else "",
            "Oui" if retraite.accepte_rgpd else "Non",
            "Oui" if retraite.accepte_contact else "Non",
            "Oui" if retraite.est_valide_par_mairie else "Non",
            _format_excel_value(retraite.date_inscription),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="retraites_actifs.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_diaspora(request):
    """Exporte tous les membres de la diaspora en Excel avec tous les champs."""
    membres = MembreDiaspora.objects.all().order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    pays = request.GET.get('pays', '')
    secteur = request.GET.get('secteur', '')
    
    if q:
        membres = membres.filter(
            Q(nom__icontains=q) |
            Q(prenoms__icontains=q) |
            Q(email__icontains=q) |
            Q(telephone_whatsapp__icontains=q) |
            Q(profession_actuelle__icontains=q) |
            Q(domaine_formation__icontains=q)
        )
    if pays:
        membres = membres.filter(pays_residence_actuelle__icontains=pays)
    if secteur:
        membres = membres.filter(secteur_activite=secteur)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Membres Diaspora"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité(s)",
        "N° Pièce identité", "Pays résidence", "Ville résidence", "Adresse étranger",
        "Commune origine", "Quartier/Village origine", "Nom parent/tuteur", "Année départ",
        "Fréquence retour", "Téléphone WhatsApp", "Email", "Réseaux sociaux",
        "Contact pays - Nom", "Contact pays - Téléphone", "Niveau études",
        "Domaine formation", "Profession actuelle", "Secteur activité",
        "Secteur activité (autre)", "Années expérience", "Statut professionnel",
        "Type titre séjour", "Appui investissement projets", "Appui financement infrastructures",
        "Appui parrainage communautaire", "Appui jeunes/femmes entrepreneurs",
        "Transfert compétences", "Formation jeunes", "Appui digitalisation",
        "Conseils techniques", "Encadrement mentorat", "Création entreprise locale",
        "Appui PME locales", "Recrutement jeunes commune", "Mise relation ONG",
        "Coopération décentralisée", "Recherche financements internationaux",
        "Promotion commune international", "Participation activités communales",
        "Participation réunions diaspora", "Appui actions sociales/culturelles",
        "Comment contribuer", "Disposition participation", "Domaine intervention prioritaire",
        "Accepte RGPD", "Accepte contact", "Validé par mairie", "Date inscription", "Date modification"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for membre in membres:
        row = [
            membre.pk,
            membre.nom,
            membre.prenoms,
            membre.get_sexe_display(),
            _format_excel_value(membre.date_naissance),
            membre.nationalites,
            membre.numero_piece_identite,
            membre.pays_residence_actuelle,
            membre.ville_residence_actuelle,
            membre.adresse_complete_etranger,
            membre.commune_origine,
            membre.quartier_village_origine,
            membre.nom_parent_tuteur_originaire,
            membre.annee_depart_pays,
            membre.get_frequence_retour_pays_display(),
            membre.telephone_whatsapp,
            membre.email,
            membre.reseaux_sociaux or "",
            membre.contact_au_pays_nom,
            membre.contact_au_pays_telephone,
            membre.get_niveau_etudes_display(),
            membre.domaine_formation,
            membre.profession_actuelle,
            membre.get_secteur_activite_display(),
            membre.secteur_activite_autre or "",
            membre.annees_experience,
            membre.get_statut_professionnel_display(),
            membre.type_titre_sejour or "",
            "Oui" if membre.appui_investissement_projets else "Non",
            "Oui" if membre.appui_financement_infrastructures else "Non",
            "Oui" if membre.appui_parrainage_communautaire else "Non",
            "Oui" if membre.appui_jeunes_femmes_entrepreneurs else "Non",
            "Oui" if membre.transfert_competences else "Non",
            "Oui" if membre.formation_jeunes else "Non",
            "Oui" if membre.appui_digitalisation else "Non",
            "Oui" if membre.conseils_techniques else "Non",
            "Oui" if membre.encadrement_mentorat else "Non",
            "Oui" if membre.creation_entreprise_locale else "Non",
            "Oui" if membre.appui_pme_locales else "Non",
            "Oui" if membre.recrutement_jeunes_commune else "Non",
            "Oui" if membre.mise_relation_ong else "Non",
            "Oui" if membre.cooperation_decentralisee else "Non",
            "Oui" if membre.recherche_financements_internationaux else "Non",
            "Oui" if membre.promotion_commune_international else "Non",
            "Oui" if membre.participation_activites_communales else "Non",
            "Oui" if membre.participation_reunions_diaspora else "Non",
            "Oui" if membre.appui_actions_sociales_culturelles else "Non",
            membre.comment_contribuer,
            membre.get_disposition_participation_display(),
            membre.domaine_intervention_prioritaire,
            "Oui" if membre.accepte_rgpd else "Non",
            "Oui" if membre.accepte_contact else "Non",
            "Oui" if membre.est_valide_par_mairie else "Non",
            _format_excel_value(membre.date_inscription),
            _format_excel_value(membre.date_modification),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="membres_diaspora.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_candidatures(request):
    """Exporte toutes les candidatures en Excel avec tous les champs."""
    candidatures = Candidature.objects.all().select_related('appel_offre', 'candidat').order_by('-date_soumission')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    statut = request.GET.get('statut', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Candidatures"
    
    # En-têtes
    headers = [
        "ID", "Appel d'offres - Titre", "Appel d'offres - Référence", "Appel d'offres - Description",
        "Appel d'offres - Public cible", "Appel d'offres - Date début", "Appel d'offres - Date fin",
        "Appel d'offres - Budget estimé", "Candidat - Username", "Candidat - Nom", "Candidat - Prénom",
        "Candidat - Email", "Statut candidature", "Message accompagnement", "Date soumission"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for candidature in candidatures:
        row = [
            candidature.pk,
            candidature.appel_offre.titre,
            candidature.appel_offre.reference or "",
            candidature.appel_offre.description,
            candidature.appel_offre.get_public_cible_display(),
            _format_excel_value(candidature.appel_offre.date_debut),
            _format_excel_value(candidature.appel_offre.date_fin),
            candidature.appel_offre.budget_estime if candidature.appel_offre.budget_estime else "",
            candidature.candidat.username,
            candidature.candidat.last_name or "",
            candidature.candidat.first_name or "",
            candidature.candidat.email,
            candidature.get_statut_display(),
            candidature.message_accompagnement or "",
            _format_excel_value(candidature.date_soumission),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 25
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="candidatures.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_pdf_jeunes(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    niveau = request.GET.get("niveau") or ""

    # Uniquement les profils validés par la mairie
    qs = ProfilEmploi.objects.filter(type_profil="jeune", est_valide_par_mairie=True)
    if niveau:
        qs = qs.filter(niveau_etude=niveau)
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
    response["Content-Disposition"] = 'attachment; filename="jeunes_demandeurs_valides.pdf"'
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
def export_pdf_diaspora(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    pays = request.GET.get("pays") or ""

    # Uniquement les membres validés par la mairie
    qs = MembreDiaspora.objects.filter(est_valide_par_mairie=True)
    if pays:
        qs = qs.filter(pays_residence_actuelle__icontains=pays)
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
    response["Content-Disposition"] = 'attachment; filename="diaspora_valides.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#006233"), alignment=1, spaceAfter=12)
    story.append(Paragraph("Membres de la Diaspora", title_style))
    if start or end:
        story.append(Paragraph(f"Période: {start or '...'} au {end or '...'}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))
    data = [["Nom", "Prénoms", "Pays de résidence", "Ville", "Téléphone", "Email", "Profession"]]
    for m in qs.order_by("-date_inscription")[:1000]:
        data.append([
            m.nom,
            m.prenoms,
            m.pays_residence_actuelle[:25] if m.pays_residence_actuelle else "",
            m.ville_residence_actuelle[:20] if m.ville_residence_actuelle else "",
            m.telephone_whatsapp[:15] if m.telephone_whatsapp else "",
            m.email[:30] if m.email else "",
            m.profession_actuelle[:30] if m.profession_actuelle else "",
        ])
    table = Table(data, colWidths=[3.5*cm, 4*cm, 4*cm, 3.5*cm, 3.5*cm, 5*cm, 4.5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
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


# ========== FONCTIONS D'EXPORT EXCEL ==========

def _format_excel_value(value):
    """Formate une valeur pour l'export Excel."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Oui" if value else "Non"
    if isinstance(value, (datetime, date)):
        return value.strftime("%d/%m/%Y %H:%M") if isinstance(value, datetime) else value.strftime("%d/%m/%Y")
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value if item)
    return str(value)


def _style_excel_header(ws, row_num):
    """Applique un style au header Excel."""
    header_fill = PatternFill(start_color="006233", end_color="006233", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    for cell in ws[row_num]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border


@login_required
@user_passes_test(is_staff_user)
def export_excel_acteurs(request):
    """Exporte tous les acteurs économiques en Excel avec tous les champs."""
    acteurs = ActeurEconomique.objects.all().order_by('-date_enregistrement')
    
    # Appliquer les filtres comme dans la vue liste
    q = request.GET.get('q', '')
    type_acteur = request.GET.get('type', '')
    secteur = request.GET.get('secteur', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Acteurs Economiques"
    
    # En-têtes
    headers = [
        "ID", "Raison sociale", "Sigle", "Type d'acteur", "Secteur d'activité", "Statut juridique",
        "Description", "RCCM", "CFE", "N° Carte opérateur", "NIF", "Date de création",
        "Capital social (FCFA)", "Nom responsable", "Fonction responsable", "Téléphone 1",
        "Téléphone 2", "Email", "Site web", "Quartier", "Canton", "Adresse complète",
        "Situation", "Latitude", "Longitude", "Nombre d'employés", "Chiffre d'affaires",
        "Accepte publication", "Certifie informations", "Accepte conditions",
        "Validé par mairie", "Date d'enregistrement"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for acteur in acteurs:
        row = [
            acteur.pk,
            acteur.raison_sociale,
            acteur.sigle or "",
            acteur.get_type_acteur_display(),
            acteur.get_secteur_activite_display(),
            acteur.get_statut_juridique_display(),
            acteur.description,
            acteur.rccm or "",
            acteur.cfe or "",
            acteur.numero_carte_operateur or "",
            acteur.nif or "",
            _format_excel_value(acteur.date_creation),
            acteur.capital_social if acteur.capital_social else "",
            acteur.nom_responsable,
            acteur.fonction_responsable,
            acteur.telephone1,
            acteur.telephone2 or "",
            acteur.email,
            acteur.site_web or "",
            acteur.quartier,
            acteur.canton or "",
            acteur.adresse_complete,
            acteur.get_situation_display(),
            acteur.latitude if acteur.latitude else "",
            acteur.longitude if acteur.longitude else "",
            acteur.get_nombre_employes_display() if acteur.nombre_employes else "",
            acteur.get_chiffre_affaires_display() if acteur.chiffre_affaires else "",
            "Oui" if acteur.accepte_public else "Non",
            "Oui" if acteur.certifie_information else "Non",
            "Oui" if acteur.accepte_conditions else "Non",
            "Oui" if acteur.est_valide_par_mairie else "Non",
            _format_excel_value(acteur.date_enregistrement),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="acteurs_economiques.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_institutions(request):
    """Exporte toutes les institutions financières en Excel avec tous les champs."""
    institutions = InstitutionFinanciere.objects.all().order_by('-date_enregistrement')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    type_inst = request.GET.get('type', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Institutions Financieres"
    
    # En-têtes
    headers = [
        "ID", "Nom institution", "Sigle", "Type institution", "Année création",
        "N° Agrément", "IFU", "Description services", "Services disponibles",
        "Taux crédit", "Taux épargne", "Conditions éligibilité", "Public cible",
        "Nom responsable", "Fonction responsable", "Téléphone 1", "Téléphone 2",
        "WhatsApp", "Email", "Site web", "Facebook", "Quartier", "Canton",
        "Adresse complète", "Situation", "Latitude", "Longitude", "Nombre agences",
        "Horaires", "Certifie informations", "Accepte publication", "Accepte contact",
        "Engagement", "Validé par mairie", "Date d'enregistrement"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for inst in institutions:
        services_text = ", ".join(part.strip().title() for part in inst.services.split(",") if part.strip()) if inst.services else ""
        row = [
            inst.pk,
            inst.nom_institution,
            inst.sigle or "",
            inst.get_type_institution_display(),
            inst.annee_creation if inst.annee_creation else "",
            inst.numero_agrement or "",
            inst.ifu or "",
            inst.description_services,
            services_text,
            inst.taux_credit or "",
            inst.taux_epargne or "",
            inst.conditions_eligibilite or "",
            inst.public_cible or "",
            inst.nom_responsable,
            inst.fonction_responsable,
            inst.telephone1,
            inst.telephone2 or "",
            inst.whatsapp or "",
            inst.email,
            inst.site_web or "",
            inst.facebook or "",
            inst.quartier,
            inst.canton or "",
            inst.adresse_complete,
            inst.get_situation_display(),
            inst.latitude if inst.latitude else "",
            inst.longitude if inst.longitude else "",
            inst.nombre_agences if inst.nombre_agences else "",
            inst.horaires,
            "Oui" if inst.certifie_info else "Non",
            "Oui" if inst.accepte_public else "Non",
            "Oui" if inst.accepte_contact else "Non",
            "Oui" if inst.engagement else "Non",
            "Oui" if inst.est_valide_par_mairie else "Non",
            _format_excel_value(inst.date_enregistrement),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="institutions_financieres.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_jeunes(request):
    """Exporte tous les jeunes demandeurs d'emploi en Excel avec tous les champs."""
    jeunes = ProfilEmploi.objects.filter(type_profil='jeune').order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    niveau = request.GET.get('niveau', '')
    dispo = request.GET.get('dispo', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Jeunes Demandeurs Emploi"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité",
        "Téléphone 1", "Téléphone 2", "Email", "Quartier", "Canton",
        "Adresse complète", "Résident Kloto 1", "Niveau étude", "Diplôme principal",
        "Domaine compétence", "Expériences", "Situation actuelle", "Employeur actuel",
        "Disponibilité", "Type contrat souhaité", "Salaire souhaité",
        "Service citoyen obligatoire", "Accepte RGPD", "Accepte contact",
        "Validé par mairie", "Date inscription"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for jeune in jeunes:
        row = [
            jeune.pk,
            jeune.nom,
            jeune.prenoms,
            jeune.get_sexe_display(),
            _format_excel_value(jeune.date_naissance),
            jeune.nationalite or "",
            jeune.telephone1,
            jeune.telephone2 or "",
            jeune.email,
            jeune.quartier,
            jeune.canton or "",
            jeune.adresse_complete,
            "Oui" if jeune.est_resident_kloto else "Non",
            jeune.get_niveau_etude_display() if jeune.niveau_etude else "",
            jeune.diplome_principal or "",
            jeune.domaine_competence,
            jeune.experiences or "",
            jeune.get_situation_actuelle_display(),
            jeune.employeur_actuel or "",
            jeune.get_disponibilite_display(),
            jeune.get_type_contrat_souhaite_display() if jeune.type_contrat_souhaite else "",
            jeune.salaire_souhaite or "",
            "Oui" if jeune.service_citoyen_obligatoire else "Non",
            "Oui" if jeune.accepte_rgpd else "Non",
            "Oui" if jeune.accepte_contact else "Non",
            "Oui" if jeune.est_valide_par_mairie else "Non",
            _format_excel_value(jeune.date_inscription),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="jeunes_demandeurs_emploi.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_retraites(request):
    """Exporte tous les retraités actifs en Excel avec tous les champs."""
    retraites = ProfilEmploi.objects.filter(type_profil='retraite').order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    niveau = request.GET.get('niveau', '')
    dispo = request.GET.get('dispo', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Retraites Actifs"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité",
        "Téléphone 1", "Téléphone 2", "Email", "Quartier", "Canton",
        "Adresse complète", "Résident Kloto 1", "Niveau étude", "Diplôme principal",
        "Domaine compétence", "Expériences", "Situation actuelle", "Employeur actuel",
        "Disponibilité", "Type contrat souhaité", "Salaire souhaité",
        "Caisse retraite", "Dernier poste", "Années expérience",
        "Accepte RGPD", "Accepte contact", "Validé par mairie", "Date inscription"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for retraite in retraites:
        row = [
            retraite.pk,
            retraite.nom,
            retraite.prenoms,
            retraite.get_sexe_display(),
            _format_excel_value(retraite.date_naissance),
            retraite.nationalite or "",
            retraite.telephone1,
            retraite.telephone2 or "",
            retraite.email,
            retraite.quartier,
            retraite.canton or "",
            retraite.adresse_complete,
            "Oui" if retraite.est_resident_kloto else "Non",
            retraite.get_niveau_etude_display() if retraite.niveau_etude else "",
            retraite.diplome_principal or "",
            retraite.domaine_competence,
            retraite.experiences or "",
            retraite.get_situation_actuelle_display(),
            retraite.employeur_actuel or "",
            retraite.get_disponibilite_display(),
            retraite.get_type_contrat_souhaite_display() if retraite.type_contrat_souhaite else "",
            retraite.salaire_souhaite or "",
            retraite.caisse_retraite or "",
            retraite.dernier_poste or "",
            retraite.annees_experience if retraite.annees_experience else "",
            "Oui" if retraite.accepte_rgpd else "Non",
            "Oui" if retraite.accepte_contact else "Non",
            "Oui" if retraite.est_valide_par_mairie else "Non",
            _format_excel_value(retraite.date_inscription),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="retraites_actifs.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_diaspora(request):
    """Exporte tous les membres de la diaspora en Excel avec tous les champs."""
    membres = MembreDiaspora.objects.all().order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    pays = request.GET.get('pays', '')
    secteur = request.GET.get('secteur', '')
    
    if q:
        membres = membres.filter(
            Q(nom__icontains=q) |
            Q(prenoms__icontains=q) |
            Q(email__icontains=q) |
            Q(telephone_whatsapp__icontains=q) |
            Q(profession_actuelle__icontains=q) |
            Q(domaine_formation__icontains=q)
        )
    if pays:
        membres = membres.filter(pays_residence_actuelle__icontains=pays)
    if secteur:
        membres = membres.filter(secteur_activite=secteur)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Membres Diaspora"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité(s)",
        "N° Pièce identité", "Pays résidence", "Ville résidence", "Adresse étranger",
        "Commune origine", "Quartier/Village origine", "Nom parent/tuteur", "Année départ",
        "Fréquence retour", "Téléphone WhatsApp", "Email", "Réseaux sociaux",
        "Contact pays - Nom", "Contact pays - Téléphone", "Niveau études",
        "Domaine formation", "Profession actuelle", "Secteur activité",
        "Secteur activité (autre)", "Années expérience", "Statut professionnel",
        "Type titre séjour", "Appui investissement projets", "Appui financement infrastructures",
        "Appui parrainage communautaire", "Appui jeunes/femmes entrepreneurs",
        "Transfert compétences", "Formation jeunes", "Appui digitalisation",
        "Conseils techniques", "Encadrement mentorat", "Création entreprise locale",
        "Appui PME locales", "Recrutement jeunes commune", "Mise relation ONG",
        "Coopération décentralisée", "Recherche financements internationaux",
        "Promotion commune international", "Participation activités communales",
        "Participation réunions diaspora", "Appui actions sociales/culturelles",
        "Comment contribuer", "Disposition participation", "Domaine intervention prioritaire",
        "Accepte RGPD", "Accepte contact", "Validé par mairie", "Date inscription", "Date modification"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for membre in membres:
        row = [
            membre.pk,
            membre.nom,
            membre.prenoms,
            membre.get_sexe_display(),
            _format_excel_value(membre.date_naissance),
            membre.nationalites,
            membre.numero_piece_identite,
            membre.pays_residence_actuelle,
            membre.ville_residence_actuelle,
            membre.adresse_complete_etranger,
            membre.commune_origine,
            membre.quartier_village_origine,
            membre.nom_parent_tuteur_originaire,
            membre.annee_depart_pays,
            membre.get_frequence_retour_pays_display(),
            membre.telephone_whatsapp,
            membre.email,
            membre.reseaux_sociaux or "",
            membre.contact_au_pays_nom,
            membre.contact_au_pays_telephone,
            membre.get_niveau_etudes_display(),
            membre.domaine_formation,
            membre.profession_actuelle,
            membre.get_secteur_activite_display(),
            membre.secteur_activite_autre or "",
            membre.annees_experience,
            membre.get_statut_professionnel_display(),
            membre.type_titre_sejour or "",
            "Oui" if membre.appui_investissement_projets else "Non",
            "Oui" if membre.appui_financement_infrastructures else "Non",
            "Oui" if membre.appui_parrainage_communautaire else "Non",
            "Oui" if membre.appui_jeunes_femmes_entrepreneurs else "Non",
            "Oui" if membre.transfert_competences else "Non",
            "Oui" if membre.formation_jeunes else "Non",
            "Oui" if membre.appui_digitalisation else "Non",
            "Oui" if membre.conseils_techniques else "Non",
            "Oui" if membre.encadrement_mentorat else "Non",
            "Oui" if membre.creation_entreprise_locale else "Non",
            "Oui" if membre.appui_pme_locales else "Non",
            "Oui" if membre.recrutement_jeunes_commune else "Non",
            "Oui" if membre.mise_relation_ong else "Non",
            "Oui" if membre.cooperation_decentralisee else "Non",
            "Oui" if membre.recherche_financements_internationaux else "Non",
            "Oui" if membre.promotion_commune_international else "Non",
            "Oui" if membre.participation_activites_communales else "Non",
            "Oui" if membre.participation_reunions_diaspora else "Non",
            "Oui" if membre.appui_actions_sociales_culturelles else "Non",
            membre.comment_contribuer,
            membre.get_disposition_participation_display(),
            membre.domaine_intervention_prioritaire,
            "Oui" if membre.accepte_rgpd else "Non",
            "Oui" if membre.accepte_contact else "Non",
            "Oui" if membre.est_valide_par_mairie else "Non",
            _format_excel_value(membre.date_inscription),
            _format_excel_value(membre.date_modification),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="membres_diaspora.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_candidatures(request):
    """Exporte toutes les candidatures en Excel avec tous les champs."""
    candidatures = Candidature.objects.all().select_related('appel_offre', 'candidat').order_by('-date_soumission')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    statut = request.GET.get('statut', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Candidatures"
    
    # En-têtes
    headers = [
        "ID", "Appel d'offres - Titre", "Appel d'offres - Référence", "Appel d'offres - Description",
        "Appel d'offres - Public cible", "Appel d'offres - Date début", "Appel d'offres - Date fin",
        "Appel d'offres - Budget estimé", "Candidat - Username", "Candidat - Nom", "Candidat - Prénom",
        "Candidat - Email", "Statut candidature", "Message accompagnement", "Date soumission"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for candidature in candidatures:
        row = [
            candidature.pk,
            candidature.appel_offre.titre,
            candidature.appel_offre.reference or "",
            candidature.appel_offre.description,
            candidature.appel_offre.get_public_cible_display(),
            _format_excel_value(candidature.appel_offre.date_debut),
            _format_excel_value(candidature.appel_offre.date_fin),
            candidature.appel_offre.budget_estime if candidature.appel_offre.budget_estime else "",
            candidature.candidat.username,
            candidature.candidat.last_name or "",
            candidature.candidat.first_name or "",
            candidature.candidat.email,
            candidature.get_statut_display(),
            candidature.message_accompagnement or "",
            _format_excel_value(candidature.date_soumission),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 25
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="candidatures.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_pdf_retraites(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    niveau = request.GET.get("niveau") or ""

    # Uniquement les profils validés par la mairie
    qs = ProfilEmploi.objects.filter(type_profil="retraite", est_valide_par_mairie=True)
    if niveau:
        qs = qs.filter(niveau_etude=niveau)
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
    response["Content-Disposition"] = 'attachment; filename="retraites_actifs_valides.pdf"'
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
def export_pdf_diaspora(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    pays = request.GET.get("pays") or ""

    # Uniquement les membres validés par la mairie
    qs = MembreDiaspora.objects.filter(est_valide_par_mairie=True)
    if pays:
        qs = qs.filter(pays_residence_actuelle__icontains=pays)
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
    response["Content-Disposition"] = 'attachment; filename="diaspora_valides.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#006233"), alignment=1, spaceAfter=12)
    story.append(Paragraph("Membres de la Diaspora", title_style))
    if start or end:
        story.append(Paragraph(f"Période: {start or '...'} au {end or '...'}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))
    data = [["Nom", "Prénoms", "Pays de résidence", "Ville", "Téléphone", "Email", "Profession"]]
    for m in qs.order_by("-date_inscription")[:1000]:
        data.append([
            m.nom,
            m.prenoms,
            m.pays_residence_actuelle[:25] if m.pays_residence_actuelle else "",
            m.ville_residence_actuelle[:20] if m.ville_residence_actuelle else "",
            m.telephone_whatsapp[:15] if m.telephone_whatsapp else "",
            m.email[:30] if m.email else "",
            m.profession_actuelle[:30] if m.profession_actuelle else "",
        ])
    table = Table(data, colWidths=[3.5*cm, 4*cm, 4*cm, 3.5*cm, 3.5*cm, 5*cm, 4.5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F5E9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
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


# ========== FONCTIONS D'EXPORT EXCEL ==========

def _format_excel_value(value):
    """Formate une valeur pour l'export Excel."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Oui" if value else "Non"
    if isinstance(value, (datetime, date)):
        return value.strftime("%d/%m/%Y %H:%M") if isinstance(value, datetime) else value.strftime("%d/%m/%Y")
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value if item)
    return str(value)


def _style_excel_header(ws, row_num):
    """Applique un style au header Excel."""
    header_fill = PatternFill(start_color="006233", end_color="006233", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    for cell in ws[row_num]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border


@login_required
@user_passes_test(is_staff_user)
def export_excel_acteurs(request):
    """Exporte tous les acteurs économiques en Excel avec tous les champs."""
    acteurs = ActeurEconomique.objects.all().order_by('-date_enregistrement')
    
    # Appliquer les filtres comme dans la vue liste
    q = request.GET.get('q', '')
    type_acteur = request.GET.get('type', '')
    secteur = request.GET.get('secteur', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Acteurs Economiques"
    
    # En-têtes
    headers = [
        "ID", "Raison sociale", "Sigle", "Type d'acteur", "Secteur d'activité", "Statut juridique",
        "Description", "RCCM", "CFE", "N° Carte opérateur", "NIF", "Date de création",
        "Capital social (FCFA)", "Nom responsable", "Fonction responsable", "Téléphone 1",
        "Téléphone 2", "Email", "Site web", "Quartier", "Canton", "Adresse complète",
        "Situation", "Latitude", "Longitude", "Nombre d'employés", "Chiffre d'affaires",
        "Accepte publication", "Certifie informations", "Accepte conditions",
        "Validé par mairie", "Date d'enregistrement"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for acteur in acteurs:
        row = [
            acteur.pk,
            acteur.raison_sociale,
            acteur.sigle or "",
            acteur.get_type_acteur_display(),
            acteur.get_secteur_activite_display(),
            acteur.get_statut_juridique_display(),
            acteur.description,
            acteur.rccm or "",
            acteur.cfe or "",
            acteur.numero_carte_operateur or "",
            acteur.nif or "",
            _format_excel_value(acteur.date_creation),
            acteur.capital_social if acteur.capital_social else "",
            acteur.nom_responsable,
            acteur.fonction_responsable,
            acteur.telephone1,
            acteur.telephone2 or "",
            acteur.email,
            acteur.site_web or "",
            acteur.quartier,
            acteur.canton or "",
            acteur.adresse_complete,
            acteur.get_situation_display(),
            acteur.latitude if acteur.latitude else "",
            acteur.longitude if acteur.longitude else "",
            acteur.get_nombre_employes_display() if acteur.nombre_employes else "",
            acteur.get_chiffre_affaires_display() if acteur.chiffre_affaires else "",
            "Oui" if acteur.accepte_public else "Non",
            "Oui" if acteur.certifie_information else "Non",
            "Oui" if acteur.accepte_conditions else "Non",
            "Oui" if acteur.est_valide_par_mairie else "Non",
            _format_excel_value(acteur.date_enregistrement),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="acteurs_economiques.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_institutions(request):
    """Exporte toutes les institutions financières en Excel avec tous les champs."""
    institutions = InstitutionFinanciere.objects.all().order_by('-date_enregistrement')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    type_inst = request.GET.get('type', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Institutions Financieres"
    
    # En-têtes
    headers = [
        "ID", "Nom institution", "Sigle", "Type institution", "Année création",
        "N° Agrément", "IFU", "Description services", "Services disponibles",
        "Taux crédit", "Taux épargne", "Conditions éligibilité", "Public cible",
        "Nom responsable", "Fonction responsable", "Téléphone 1", "Téléphone 2",
        "WhatsApp", "Email", "Site web", "Facebook", "Quartier", "Canton",
        "Adresse complète", "Situation", "Latitude", "Longitude", "Nombre agences",
        "Horaires", "Certifie informations", "Accepte publication", "Accepte contact",
        "Engagement", "Validé par mairie", "Date d'enregistrement"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for inst in institutions:
        services_text = ", ".join(part.strip().title() for part in inst.services.split(",") if part.strip()) if inst.services else ""
        row = [
            inst.pk,
            inst.nom_institution,
            inst.sigle or "",
            inst.get_type_institution_display(),
            inst.annee_creation if inst.annee_creation else "",
            inst.numero_agrement or "",
            inst.ifu or "",
            inst.description_services,
            services_text,
            inst.taux_credit or "",
            inst.taux_epargne or "",
            inst.conditions_eligibilite or "",
            inst.public_cible or "",
            inst.nom_responsable,
            inst.fonction_responsable,
            inst.telephone1,
            inst.telephone2 or "",
            inst.whatsapp or "",
            inst.email,
            inst.site_web or "",
            inst.facebook or "",
            inst.quartier,
            inst.canton or "",
            inst.adresse_complete,
            inst.get_situation_display(),
            inst.latitude if inst.latitude else "",
            inst.longitude if inst.longitude else "",
            inst.nombre_agences if inst.nombre_agences else "",
            inst.horaires,
            "Oui" if inst.certifie_info else "Non",
            "Oui" if inst.accepte_public else "Non",
            "Oui" if inst.accepte_contact else "Non",
            "Oui" if inst.engagement else "Non",
            "Oui" if inst.est_valide_par_mairie else "Non",
            _format_excel_value(inst.date_enregistrement),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="institutions_financieres.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_jeunes(request):
    """Exporte tous les jeunes demandeurs d'emploi en Excel avec tous les champs."""
    jeunes = ProfilEmploi.objects.filter(type_profil='jeune').order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    niveau = request.GET.get('niveau', '')
    dispo = request.GET.get('dispo', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Jeunes Demandeurs Emploi"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité",
        "Téléphone 1", "Téléphone 2", "Email", "Quartier", "Canton",
        "Adresse complète", "Résident Kloto 1", "Niveau étude", "Diplôme principal",
        "Domaine compétence", "Expériences", "Situation actuelle", "Employeur actuel",
        "Disponibilité", "Type contrat souhaité", "Salaire souhaité",
        "Service citoyen obligatoire", "Accepte RGPD", "Accepte contact",
        "Validé par mairie", "Date inscription"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for jeune in jeunes:
        row = [
            jeune.pk,
            jeune.nom,
            jeune.prenoms,
            jeune.get_sexe_display(),
            _format_excel_value(jeune.date_naissance),
            jeune.nationalite or "",
            jeune.telephone1,
            jeune.telephone2 or "",
            jeune.email,
            jeune.quartier,
            jeune.canton or "",
            jeune.adresse_complete,
            "Oui" if jeune.est_resident_kloto else "Non",
            jeune.get_niveau_etude_display() if jeune.niveau_etude else "",
            jeune.diplome_principal or "",
            jeune.domaine_competence,
            jeune.experiences or "",
            jeune.get_situation_actuelle_display(),
            jeune.employeur_actuel or "",
            jeune.get_disponibilite_display(),
            jeune.get_type_contrat_souhaite_display() if jeune.type_contrat_souhaite else "",
            jeune.salaire_souhaite or "",
            "Oui" if jeune.service_citoyen_obligatoire else "Non",
            "Oui" if jeune.accepte_rgpd else "Non",
            "Oui" if jeune.accepte_contact else "Non",
            "Oui" if jeune.est_valide_par_mairie else "Non",
            _format_excel_value(jeune.date_inscription),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="jeunes_demandeurs_emploi.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_retraites(request):
    """Exporte tous les retraités actifs en Excel avec tous les champs."""
    retraites = ProfilEmploi.objects.filter(type_profil='retraite').order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    niveau = request.GET.get('niveau', '')
    dispo = request.GET.get('dispo', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Retraites Actifs"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité",
        "Téléphone 1", "Téléphone 2", "Email", "Quartier", "Canton",
        "Adresse complète", "Résident Kloto 1", "Niveau étude", "Diplôme principal",
        "Domaine compétence", "Expériences", "Situation actuelle", "Employeur actuel",
        "Disponibilité", "Type contrat souhaité", "Salaire souhaité",
        "Caisse retraite", "Dernier poste", "Années expérience",
        "Accepte RGPD", "Accepte contact", "Validé par mairie", "Date inscription"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for retraite in retraites:
        row = [
            retraite.pk,
            retraite.nom,
            retraite.prenoms,
            retraite.get_sexe_display(),
            _format_excel_value(retraite.date_naissance),
            retraite.nationalite or "",
            retraite.telephone1,
            retraite.telephone2 or "",
            retraite.email,
            retraite.quartier,
            retraite.canton or "",
            retraite.adresse_complete,
            "Oui" if retraite.est_resident_kloto else "Non",
            retraite.get_niveau_etude_display() if retraite.niveau_etude else "",
            retraite.diplome_principal or "",
            retraite.domaine_competence,
            retraite.experiences or "",
            retraite.get_situation_actuelle_display(),
            retraite.employeur_actuel or "",
            retraite.get_disponibilite_display(),
            retraite.get_type_contrat_souhaite_display() if retraite.type_contrat_souhaite else "",
            retraite.salaire_souhaite or "",
            retraite.caisse_retraite or "",
            retraite.dernier_poste or "",
            retraite.annees_experience if retraite.annees_experience else "",
            "Oui" if retraite.accepte_rgpd else "Non",
            "Oui" if retraite.accepte_contact else "Non",
            "Oui" if retraite.est_valide_par_mairie else "Non",
            _format_excel_value(retraite.date_inscription),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="retraites_actifs.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_diaspora(request):
    """Exporte tous les membres de la diaspora en Excel avec tous les champs."""
    membres = MembreDiaspora.objects.all().order_by('-date_inscription')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    pays = request.GET.get('pays', '')
    secteur = request.GET.get('secteur', '')
    
    if q:
        membres = membres.filter(
            Q(nom__icontains=q) |
            Q(prenoms__icontains=q) |
            Q(email__icontains=q) |
            Q(telephone_whatsapp__icontains=q) |
            Q(profession_actuelle__icontains=q) |
            Q(domaine_formation__icontains=q)
        )
    if pays:
        membres = membres.filter(pays_residence_actuelle__icontains=pays)
    if secteur:
        membres = membres.filter(secteur_activite=secteur)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Membres Diaspora"
    
    # En-têtes
    headers = [
        "ID", "Nom", "Prénoms", "Sexe", "Date naissance", "Nationalité(s)",
        "N° Pièce identité", "Pays résidence", "Ville résidence", "Adresse étranger",
        "Commune origine", "Quartier/Village origine", "Nom parent/tuteur", "Année départ",
        "Fréquence retour", "Téléphone WhatsApp", "Email", "Réseaux sociaux",
        "Contact pays - Nom", "Contact pays - Téléphone", "Niveau études",
        "Domaine formation", "Profession actuelle", "Secteur activité",
        "Secteur activité (autre)", "Années expérience", "Statut professionnel",
        "Type titre séjour", "Appui investissement projets", "Appui financement infrastructures",
        "Appui parrainage communautaire", "Appui jeunes/femmes entrepreneurs",
        "Transfert compétences", "Formation jeunes", "Appui digitalisation",
        "Conseils techniques", "Encadrement mentorat", "Création entreprise locale",
        "Appui PME locales", "Recrutement jeunes commune", "Mise relation ONG",
        "Coopération décentralisée", "Recherche financements internationaux",
        "Promotion commune international", "Participation activités communales",
        "Participation réunions diaspora", "Appui actions sociales/culturelles",
        "Comment contribuer", "Disposition participation", "Domaine intervention prioritaire",
        "Accepte RGPD", "Accepte contact", "Validé par mairie", "Date inscription", "Date modification"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for membre in membres:
        row = [
            membre.pk,
            membre.nom,
            membre.prenoms,
            membre.get_sexe_display(),
            _format_excel_value(membre.date_naissance),
            membre.nationalites,
            membre.numero_piece_identite,
            membre.pays_residence_actuelle,
            membre.ville_residence_actuelle,
            membre.adresse_complete_etranger,
            membre.commune_origine,
            membre.quartier_village_origine,
            membre.nom_parent_tuteur_originaire,
            membre.annee_depart_pays,
            membre.get_frequence_retour_pays_display(),
            membre.telephone_whatsapp,
            membre.email,
            membre.reseaux_sociaux or "",
            membre.contact_au_pays_nom,
            membre.contact_au_pays_telephone,
            membre.get_niveau_etudes_display(),
            membre.domaine_formation,
            membre.profession_actuelle,
            membre.get_secteur_activite_display(),
            membre.secteur_activite_autre or "",
            membre.annees_experience,
            membre.get_statut_professionnel_display(),
            membre.type_titre_sejour or "",
            "Oui" if membre.appui_investissement_projets else "Non",
            "Oui" if membre.appui_financement_infrastructures else "Non",
            "Oui" if membre.appui_parrainage_communautaire else "Non",
            "Oui" if membre.appui_jeunes_femmes_entrepreneurs else "Non",
            "Oui" if membre.transfert_competences else "Non",
            "Oui" if membre.formation_jeunes else "Non",
            "Oui" if membre.appui_digitalisation else "Non",
            "Oui" if membre.conseils_techniques else "Non",
            "Oui" if membre.encadrement_mentorat else "Non",
            "Oui" if membre.creation_entreprise_locale else "Non",
            "Oui" if membre.appui_pme_locales else "Non",
            "Oui" if membre.recrutement_jeunes_commune else "Non",
            "Oui" if membre.mise_relation_ong else "Non",
            "Oui" if membre.cooperation_decentralisee else "Non",
            "Oui" if membre.recherche_financements_internationaux else "Non",
            "Oui" if membre.promotion_commune_international else "Non",
            "Oui" if membre.participation_activites_communales else "Non",
            "Oui" if membre.participation_reunions_diaspora else "Non",
            "Oui" if membre.appui_actions_sociales_culturelles else "Non",
            membre.comment_contribuer,
            membre.get_disposition_participation_display(),
            membre.domaine_intervention_prioritaire,
            "Oui" if membre.accepte_rgpd else "Non",
            "Oui" if membre.accepte_contact else "Non",
            "Oui" if membre.est_valide_par_mairie else "Non",
            _format_excel_value(membre.date_inscription),
            _format_excel_value(membre.date_modification),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="membres_diaspora.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_staff_user)
def export_excel_candidatures(request):
    """Exporte toutes les candidatures en Excel avec tous les champs."""
    candidatures = Candidature.objects.all().select_related('appel_offre', 'candidat').order_by('-date_soumission')
    
    # Appliquer les filtres
    q = request.GET.get('q', '')
    statut = request.GET.get('statut', '')
    
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
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Candidatures"
    
    # En-têtes
    headers = [
        "ID", "Appel d'offres - Titre", "Appel d'offres - Référence", "Appel d'offres - Description",
        "Appel d'offres - Public cible", "Appel d'offres - Date début", "Appel d'offres - Date fin",
        "Appel d'offres - Budget estimé", "Candidat - Username", "Candidat - Nom", "Candidat - Prénom",
        "Candidat - Email", "Statut candidature", "Message accompagnement", "Date soumission"
    ]
    ws.append(headers)
    _style_excel_header(ws, 1)
    
    # Données
    for candidature in candidatures:
        row = [
            candidature.pk,
            candidature.appel_offre.titre,
            candidature.appel_offre.reference or "",
            candidature.appel_offre.description,
            candidature.appel_offre.get_public_cible_display(),
            _format_excel_value(candidature.appel_offre.date_debut),
            _format_excel_value(candidature.appel_offre.date_fin),
            candidature.appel_offre.budget_estime if candidature.appel_offre.budget_estime else "",
            candidature.candidat.username,
            candidature.candidat.last_name or "",
            candidature.candidat.first_name or "",
            candidature.candidat.email,
            candidature.get_statut_display(),
            candidature.message_accompagnement or "",
            _format_excel_value(candidature.date_soumission),
        ]
        ws.append(row)
    
    # Ajuster la largeur des colonnes
    for idx, col in enumerate(ws.columns, 1):
        ws.column_dimensions[get_column_letter(idx)].width = 25
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="candidatures.xlsx"'
    wb.save(response)
    return response
