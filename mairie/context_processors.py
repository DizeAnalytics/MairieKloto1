from .models import ConfigurationMairie

def mairie_config(request):
    config = ConfigurationMairie.objects.filter(est_active=True).order_by("-date_modification").first()
    return {"mairie_config": config}
