from __future__ import annotations

from django.utils import timezone

from mairie.models import VisiteSite


class TrackVisitorMiddleware:
    """
    Middleware pour enregistrer les visites du site.

    - Enregistre l'IP, le user-agent, le chemin et la session.
    - Ignore les fichiers statiques, médias et l'administration Django.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.path or ""

        # Ignorer certains chemins (admin, static, media)
        if path.startswith("/Securelogin/") or path.startswith("/admin/") or path.startswith("/static/") or path.startswith("/media/"):
            return response

        try:
            ip = request.META.get("REMOTE_ADDR", "")
            user_agent = request.META.get("HTTP_USER_AGENT", "") or ""
            session_key = request.session.session_key or ""

            # S'assurer que la session existe
            if not session_key:
                request.session.save()
                session_key = request.session.session_key or ""

            VisiteSite.objects.create(
                date=timezone.now(),
                ip_address=ip or None,
                user_agent=user_agent[:255],
                path=path[:255],
                session_key=session_key[:40],
            )
        except Exception:
            # Ne jamais casser le site si la sauvegarde des stats échoue
            pass

        return response

