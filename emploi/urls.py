from django.urls import path

from . import views

app_name = "emploi"

urlpatterns = [
    path("jeunes/", views.inscription_jeune, name="inscription_jeunes"),
    path("retraites/", views.inscription_retraite, name="inscription_retraites"),
    path("pdf/jeunes/", views.generer_pdf_jeune, name="pdf_jeunes"),
    path("pdf/retraites/", views.generer_pdf_retraite, name="pdf_retraites"),
]


