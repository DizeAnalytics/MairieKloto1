from django.contrib import admin

from .models import OrganisationSocieteCivile


@admin.register(OrganisationSocieteCivile)
class OrganisationSocieteCivileAdmin(admin.ModelAdmin):
    list_display = ("nom_osc", "type_osc", "telephone", "email", "date_enregistrement", "est_valide_par_mairie")
    list_filter = ("est_valide_par_mairie", "type_osc", "date_enregistrement")
    search_fields = ("nom_osc", "sigle", "telephone", "email")
    readonly_fields = ("date_enregistrement",)

