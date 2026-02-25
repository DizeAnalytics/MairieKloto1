from django.urls import path

from . import views

app_name = "osc"

urlpatterns = [
    path("inscription/", views.inscription_osc, name="inscription"),
    path("mes-organisations/", views.liste_osc, name="liste"),
    path("modifier/<int:pk>/", views.modifier_osc, name="modifier"),
]

