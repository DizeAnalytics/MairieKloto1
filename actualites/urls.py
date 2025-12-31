from django.urls import path

from . import views

app_name = 'actualites'

urlpatterns = [
    path('', views.liste_actualites, name='liste'),
    path('<int:pk>/', views.detail_actualite, name='detail'),
]

