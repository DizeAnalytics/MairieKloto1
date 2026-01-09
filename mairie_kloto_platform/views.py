from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta, datetime
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
    
    context = {
        'stats': stats,
        'chart_data_json': json.dumps(chart_data, cls=DjangoJSONEncoder),
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
    
    context = {
        'candidatures': candidatures,
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
