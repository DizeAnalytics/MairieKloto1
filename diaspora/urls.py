from django.urls import path
from . import views

app_name = "diaspora"

urlpatterns = [
    # Inscription et modification
    path("inscription/", views.inscription_diaspora, name="inscription"),
    path("modifier/", views.modifier_diaspora, name="modifier"),
    
    # Administration
    path("liste/", views.liste_diaspora, name="liste"),
    path("detail/<int:membre_id>/", views.detail_diaspora, name="detail"),
    path("valider/<int:membre_id>/", views.valider_membre, name="valider"),
    
    # Statistiques publiques
    path("statistiques/", views.statistiques_diaspora, name="statistiques"),
]