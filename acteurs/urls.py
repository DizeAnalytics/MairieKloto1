from django.urls import path

from . import views

app_name = "acteurs"

urlpatterns = [
    path("enregistrement/", views.enregistrer_acteur, name="enregistrement"),
    path(
        "institutions/",
        views.inscrire_institution_financiere,
        name="inscription_institutions",
    ),
    path("modifier-acteur/", views.modifier_acteur, name="modifier_acteur"),
    path("modifier-institution/", views.modifier_institution, name="modifier_institution"),
    path("sites/", views.enregistrer_site_touristique, name="sites"),
    path("sites-touristiques/", views.liste_sites_touristiques, name="sites_public"),
    path("sites-touristiques/<int:pk>/", views.site_detail, name="site_detail"),
    path("pdf/acteurs/", views.generer_pdf_acteur, name="pdf_acteurs"),
    path("pdf/institutions/", views.generer_pdf_institution, name="pdf_institutions"),
]

