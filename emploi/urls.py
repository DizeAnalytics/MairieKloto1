from django.urls import path

from . import views

app_name = "emploi"

urlpatterns = [
    path("jeunes/", views.inscription_jeune, name="inscription_jeunes"),
    path("modifier-jeune/", views.modifier_jeune, name="modifier_jeune"),
    path("retraites/", views.inscription_retraite, name="inscription_retraites"),
    path("modifier-retraite/", views.modifier_retraite, name="modifier_retraite"),
    path("pdf/jeunes/", views.generer_pdf_jeune, name="pdf_jeunes"),
    path("pdf/retraites/", views.generer_pdf_retraite, name="pdf_retraites"),
]
