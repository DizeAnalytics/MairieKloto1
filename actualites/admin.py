from django.contrib import admin

from .models import Actualite


@admin.register(Actualite)
class ActualiteAdmin(admin.ModelAdmin):
    list_display = ("titre", "date_publication", "est_publie")
    list_filter = ("est_publie", "date_publication")
    search_fields = ("titre", "resume", "contenu", "titre1", "titre2", "titre3", "texte1", "texte2", "texte3")
    ordering = ("-date_publication",)
    
    fieldsets = (
        ("Informations générales", {
            "fields": ("titre", "resume", "est_publie")
        }),
        ("Bloc 1 : Photo 1 - Titre 1 - Texte 1", {
            "fields": (
                "photo1",
                "titre1",
                "texte1",
            ),
            "description": "Premier bloc : photo1 → titre1 → texte1"
        }),
        ("Bloc 2 : Photo 2 - Titre 2 - Texte 2", {
            "fields": (
                "photo2",
                "titre2",
                "texte2",
            ),
            "description": "Deuxième bloc : photo2 → titre2 → texte2"
        }),
        ("Bloc 3 : Photo 3 - Titre 3 - Texte 3", {
            "fields": (
                "photo3",
                "titre3",
                "texte3",
            ),
            "description": "Troisième bloc : photo3 → titre3 → texte3"
        }),
        ("Ancien format (compatibilité)", {
            "fields": ("contenu",),
            "description": "Ancien format conservé pour compatibilité. Si vous utilisez le nouveau format ci-dessus, ce champ n'est pas nécessaire.",
            "classes": ("collapse",)
        }),
    )


