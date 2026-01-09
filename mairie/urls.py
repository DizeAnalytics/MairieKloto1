from django.urls import path

from . import views

app_name = 'mairie'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('etat-civil/', views.etat_civil, name='etat_civil'),
    path('contactez-nous/', views.contactez_nous, name='contactez_nous'),
    path('appels-offres/', views.liste_appels_offres, name='appels_offres'),
    path('appels-offres/<int:pk>/', views.detail_appel_offre, name='appel_offre_detail'),
    path('appels-offres/<int:pk>/pdf/', views.generer_pdf_appel_offre, name='appel_offre_pdf'),
    path('appels-offres/<int:pk>/candidater/', views.soumettre_candidature, name='soumettre_candidature'),
]

