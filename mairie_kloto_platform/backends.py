"""
Backend d'authentification personnalisé pour permettre la connexion par email.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Backend d'authentification qui permet la connexion avec le nom d'utilisateur OU l'email.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('username')
        
        if username is None or password is None:
            return None
        
        try:
            # Chercher l'utilisateur par username ou email
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            # Exécuter le hash du mot de passe pour éviter les attaques par timing
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Si plusieurs utilisateurs ont le même email, prendre le premier
            user = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()
        
        # Vérifier le mot de passe et les permissions
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None

