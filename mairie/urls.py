from django.urls import path

from . import views

app_name = 'mairie'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('organigramme/', views.organigramme_mairie, name='organigramme'),
    path('organigramme/section/<int:pk>/services/', views.section_services_detail, name='section_services'),
    path('cartographie/', views.cartographie_commune, name='cartographie'),
    path('contactez-nous/', views.contactez_nous, name='contactez_nous'),
    path('appels-offres/', views.liste_appels_offres, name='appels_offres'),
    path('appels-offres/<int:pk>/', views.detail_appel_offre, name='appel_offre_detail'),
    path('appels-offres/<int:pk>/pdf/', views.generer_pdf_appel_offre, name='appel_offre_pdf'),
    path('appels-offres/<int:pk>/candidater/', views.soumettre_candidature, name='soumettre_candidature'),
    path('nos-projets/', views.liste_projets, name='projets'),
    path('nos-projets/<slug:slug>/', views.detail_projet, name='projet_detail'),
    path('inscription-contribuable/', views.inscrire_contribuable, name='inscription_contribuable'),
]

