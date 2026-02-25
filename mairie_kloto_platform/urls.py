"""
URL configuration for mairie_kloto_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    # Route sécurisée pour l'admin Django (renommée pour la sécurité)
    path("Securelogin/", admin.site.urls),
    # Fausse route admin pour tromper les attaquants
    path("admin/", views.fake_admin, name="fake_admin"),
    # Page d'accueil avec mot du maire et informations
    path("", include("mairie.urls", namespace="mairie")),
    # Page d'enregistrement (ancienne page d'accueil)
    path("enregistrement/", views.home, name="enregistrement"),
    path("acteurs/", include("acteurs.urls", namespace="acteurs")),
    path("emploi/", include("emploi.urls", namespace="emploi")),
    path("actualites/", include("actualites.urls", namespace="actualites")),
    path("comptes/", include("comptes.urls", namespace="comptes")),
    path("diaspora/", include("diaspora.urls", namespace="diaspora")),
    path("osc/", include("osc.urls", namespace="osc")),
    # Politique de cookies (conformité / données personnelles)
    path("politique-cookies/", views.politique_cookies, name="politique_cookies"),
    # Newsletter (inscription globale, utilisée notamment par le popup de publicité)
    path("newsletter/inscription/", views.newsletter_subscribe, name="newsletter_inscription"),
    # Tableau de bord administrateur
    path("tableau-bord/", views.tableau_bord, name="tableau_bord"),
    path("tableau-bord/newsletters/", views.newsletters_admin, name="newsletters_admin"),
    path("tableau-bord/acteurs-economiques/", views.liste_acteurs_economiques, name="liste_acteurs"),
    path("tableau-bord/acteurs-economiques/<int:pk>/pdf/", views.export_pdf_acteur_detail, name="export_pdf_acteur_detail"),
    path("tableau-bord/institutions-financieres/", views.liste_institutions_financieres, name="liste_institutions"),
    path("tableau-bord/institutions-financieres/<int:pk>/pdf/", views.export_pdf_institution_detail, name="export_pdf_institution_detail"),
    path("tableau-bord/jeunes/", views.liste_jeunes, name="liste_jeunes"),
    path("tableau-bord/jeunes/<int:pk>/pdf/", views.export_pdf_jeune_detail, name="export_pdf_jeune_detail"),
    path("tableau-bord/retraites/", views.liste_retraites, name="liste_retraites"),
    path("tableau-bord/retraites/<int:pk>/pdf/", views.export_pdf_retraite_detail, name="export_pdf_retraite_detail"),
    path("tableau-bord/diaspora/", views.liste_diaspora_tableau_bord, name="liste_diaspora_tableau_bord"),
    path("tableau-bord/diaspora/<int:pk>/pdf/", views.export_pdf_diaspora_detail, name="export_pdf_diaspora_detail"),
    path("tableau-bord/osc/", views.liste_osc_tableau_bord, name="liste_osc_tableau_bord"),
    path("tableau-bord/osc/<int:pk>/pdf/", views.export_pdf_osc_detail, name="export_pdf_osc_detail"),
    path("tableau-bord/agents-collecteurs/", views.liste_agents_collecteurs, name="liste_agents_collecteurs"),
    path("tableau-bord/agents-collecteurs/ajouter/", views.ajouter_agent_collecteur, name="ajouter_agent_collecteur"),
    path("tableau-bord/agents-collecteurs/<int:agent_id>/modifier/", views.modifier_agent_collecteur, name="modifier_agent_collecteur"),
    path("tableau-bord/contribuables/", views.liste_contribuables, name="liste_contribuables"),
    path("tableau-bord/boutiques/", views.liste_boutiques, name="liste_boutiques"),
    path("tableau-bord/boutiques/creer-emplacement/", views.creer_emplacement_ajax, name="creer_emplacement_ajax"),
    path("tableau-bord/infrastructures/sauvegarder/", views.sauvegarder_infrastructure_ajax, name="sauvegarder_infrastructure_ajax"),
    path("tableau-bord/contributions/", views.liste_contributions, name="liste_contributions"),
    path("tableau-bord/cotisations-acteurs-institutions/", views.liste_cotisations_acteurs_institutions, name="liste_cotisations_acteurs_institutions"),
    path("tableau-bord/definir-taxe-acteur/<int:acteur_id>/", views.definir_taxe_acteur, name="definir_taxe_acteur"),
    path("tableau-bord/definir-taxe-institution/<int:institution_id>/", views.definir_taxe_institution, name="definir_taxe_institution"),
    path("tableau-bord/suggestions/", views.liste_suggestions, name="liste_suggestions"),
    path("tableau-bord/suggestions/<int:pk>/", views.detail_suggestion, name="detail_suggestion"),
    path("tableau-bord/candidatures/", views.liste_candidatures, name="liste_candidatures"),
    path("tableau-bord/candidatures/<int:appel_offre_id>/pdf/", views.export_pdf_candidatures, name="export_pdf_candidatures"),
    path("tableau-bord/notifications-candidats/", views.notifications_candidats, name="notifications_candidats"),
    path("tableau-bord/notifications-candidats/<int:appel_offre_id>/envoyer/", views.envoyer_notifications_candidats, name="envoyer_notifications_candidats"),
    path("tableau-bord/changer-statut/<str:model_name>/<int:pk>/<str:action>/", views.changer_statut, name="changer_statut"),
    path("tableau-bord/export/acteurs/", views.export_pdf_acteurs, name="export_pdf_acteurs"),
    path("tableau-bord/export/entreprises/", views.export_pdf_entreprises, name="export_pdf_entreprises"),
    path("tableau-bord/export/institutions/", views.export_pdf_institutions, name="export_pdf_institutions"),
    path("tableau-bord/export/jeunes/", views.export_pdf_jeunes, name="export_pdf_jeunes"),
    path("tableau-bord/export/retraites/", views.export_pdf_retraites, name="export_pdf_retraites"),
    path("tableau-bord/export/diaspora/", views.export_pdf_diaspora, name="export_pdf_diaspora"),
    path("tableau-bord/export/osc/", views.export_pdf_osc, name="export_pdf_osc"),
    # Exports Excel
    path("tableau-bord/export-excel/acteurs/", views.export_excel_acteurs, name="export_excel_acteurs"),
    path("tableau-bord/export-excel/institutions/", views.export_excel_institutions, name="export_excel_institutions"),
    path("tableau-bord/export-excel/jeunes/", views.export_excel_jeunes, name="export_excel_jeunes"),
    path("tableau-bord/export-excel/retraites/", views.export_excel_retraites, name="export_excel_retraites"),
    path("tableau-bord/export-excel/diaspora/", views.export_excel_diaspora, name="export_excel_diaspora"),
    path("tableau-bord/export-excel/candidatures/", views.export_excel_candidatures, name="export_excel_candidatures"),
    path("tableau-bord/export-excel/osc/", views.export_excel_osc, name="export_excel_osc"),
    # Exports agents, contribuables, boutiques, contributions, cotisations acteurs/institutions
    path("tableau-bord/export/agents-collecteurs/", views.export_pdf_agents_collecteurs, name="export_pdf_agents_collecteurs"),
    path("tableau-bord/export-excel/agents-collecteurs/", views.export_excel_agents_collecteurs, name="export_excel_agents_collecteurs"),
    path("tableau-bord/export/contribuables/", views.export_pdf_contribuables, name="export_pdf_contribuables"),
    path("tableau-bord/export-excel/contribuables/", views.export_excel_contribuables, name="export_excel_contribuables"),
    path("tableau-bord/export/boutiques/", views.export_pdf_boutiques, name="export_pdf_boutiques"),
    path("tableau-bord/export-excel/boutiques/", views.export_excel_boutiques, name="export_excel_boutiques"),
    path("tableau-bord/export/contributions/", views.export_pdf_contributions, name="export_pdf_contributions"),
    path("tableau-bord/export-excel/contributions/", views.export_excel_contributions, name="export_excel_contributions"),
    path("tableau-bord/export/cotisations-acteurs-institutions/", views.export_pdf_cotisations_acteurs_institutions, name="export_pdf_cotisations_acteurs_institutions"),
    path("tableau-bord/export-excel/cotisations-acteurs-institutions/", views.export_excel_cotisations_acteurs_institutions, name="export_excel_cotisations_acteurs_institutions"),
    path("tableau-bord/publicites/", views.gestion_publicites, name="gestion_publicites"),
    path(
        "tableau-bord/publicites/<int:pk>/",
        views.detail_campagne_publicite,
        name="detail_campagne_publicite",
    ),
    path("tableau-bord/organigramme/", views.tableau_bord_organigramme, name="tableau_bord_organigramme"),
    path("tableau-bord/export/organigramme/", views.export_pdf_organigramme, name="export_pdf_organigramme"),
    path("tableau-bord/export-excel/organigramme/", views.export_excel_organigramme, name="export_excel_organigramme"),
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
