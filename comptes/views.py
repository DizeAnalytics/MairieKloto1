from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def inscription(request):
    """Vue pour l'inscription des utilisateurs."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Connexion automatique après inscription
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {username} ! Votre compte a été créé avec succès.')
                return redirect('enregistrement')
    else:
        form = UserCreationForm()
    
    return render(request, 'comptes/inscription.html', {'form': form})


def connexion(request):
    """Vue pour la connexion des utilisateurs."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            # Rediriger vers la page demandée ou la page par défaut
            next_url = request.GET.get('next', 'enregistrement')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'comptes/connexion.html')


@login_required
def deconnexion(request):
    """Vue pour la déconnexion des utilisateurs."""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('mairie:accueil')


@login_required
def profil(request):
    """Vue pour afficher le profil de l'utilisateur."""
    return render(request, 'comptes/profil.html')
