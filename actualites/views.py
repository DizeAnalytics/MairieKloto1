from django.shortcuts import render, get_object_or_404

from .models import Actualite


def liste_actualites(request):
    """Affiche la liste des 3 dernières actualités publiées."""
    
    actualites = Actualite.objects.filter(est_publie=True).order_by('-date_publication')[:3]
    
    context = {
        'actualites': actualites,
    }
    
    return render(request, 'actualites/liste.html', context)


def detail_actualite(request, pk):
    """Affiche le détail d'une actualité."""
    
    actualite = get_object_or_404(Actualite, pk=pk, est_publie=True)
    
    # Récupérer les actualités récentes pour la sidebar
    actualites_recentes = Actualite.objects.filter(
        est_publie=True
    ).exclude(pk=pk).order_by('-date_publication')[:5]
    
    context = {
        'actualite': actualite,
        'actualites_recentes': actualites_recentes,
    }
    
    return render(request, 'actualites/detail.html', context)

