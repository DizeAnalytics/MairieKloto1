from django.urls import path

from . import views

app_name = 'comptes'

urlpatterns = [
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('profil/', views.profil, name='profil'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('publicites/demander/', views.demander_campagne_publicitaire, name='demande_publicite'),
    path('publicites/creer/', views.creer_publicite, name='creer_publicite'),
    # Espace agent collecteur
    path('espace-agent/', views.espace_agent, name='espace_agent'),
    path('payer-contribuable/<int:contribuable_id>/', views.payer_contribuable, name='payer_contribuable'),
    path('payer-acteur/<int:acteur_id>/', views.payer_acteur, name='payer_acteur'),
    path('payer-institution/<int:institution_id>/', views.payer_institution, name='payer_institution'),
]
