from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Q
from acteurs.models import ActeurEconomique, InstitutionFinanciere
from emploi.models import ProfilEmploi
from .models import Notification
from .views import get_recipient_display_name

User = get_user_model()


# Configuration admin pour User avec recherche personnalisée pour l'autocomplete
# Désenregistrer User s'il est déjà enregistré pour éviter les conflits
if admin.site.is_registered(User):
    admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personnalisé pour User avec recherche étendue."""
    
    search_fields = (
        'username', 
        'email',
        'acteur_economique__raison_sociale',
        'institution_financiere__nom_institution',
        'profil_emploi__nom',
        'profil_emploi__prenoms'
    )
    
    def get_search_results(self, request, queryset, search_term):
        """Recherche personnalisée incluant les profils liés."""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        if search_term:
            # Recherche dans les noms d'entreprises
            queryset |= User.objects.filter(
                acteur_economique__raison_sociale__icontains=search_term
            )
            # Recherche dans les noms d'institutions
            queryset |= User.objects.filter(
                institution_financiere__nom_institution__icontains=search_term
            )
            # Recherche dans les noms et prénoms des profils emploi
            queryset |= User.objects.filter(
                Q(profil_emploi__nom__icontains=search_term) |
                Q(profil_emploi__prenoms__icontains=search_term)
            )
            use_distinct = True
        
        return queryset, use_distinct
    
    def get_urls(self):
        """Enregistre la vue d'autocomplete personnalisée."""
        from django.urls import path
        from .views import UserAutocompleteView
        
        urls = super().get_urls()
        # Enregistrer la vue d'autocomplete personnalisée
        # Django Admin cherche l'URL avec le pattern: <app_label>_<model_name>_autocomplete
        custom_urls = [
            path('autocomplete/', self.admin_site.admin_view(UserAutocompleteView.as_view()), name='auth_user_autocomplete'),
        ]
        return custom_urls + urls


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    class Form(forms.ModelForm):
        class Meta:
            model = Notification
            fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Inclure tous les utilisateurs qui ont un profil (entreprise, institution ou emploi)
            qs = User.objects.filter(
                Q(acteur_economique__isnull=False) |
                Q(institution_financiere__isnull=False) |
                Q(profil_emploi__isnull=False)
            ).select_related("acteur_economique", "institution_financiere", "profil_emploi").distinct()
            
            # Le widget d'autocomplete sera utilisé automatiquement via autocomplete_fields
            # Mais on limite le queryset aux utilisateurs avec profils
            self.fields["recipient"].queryset = qs
            self.fields["recipient"].label_from_instance = get_recipient_display_name
            self.fields["recipient"].help_text = "Recherchez par nom d'entreprise, institution ou nom/prénom d'une personne"

    form = Form
    list_display = ("title", "recipient_display", "type", "rendezvous_datetime", "is_read", "created_at", "sender")
    list_filter = ("type", "is_read", "created_at")
    search_fields = (
        "title", 
        "message", 
        "recipient__username", 
        "recipient__email",
        "recipient__acteur_economique__raison_sociale",
        "recipient__institution_financiere__nom_institution",
        "recipient__profil_emploi__nom",
        "recipient__profil_emploi__prenoms"
    )
    date_hierarchy = "created_at"
    actions = ["mark_as_read", "mark_as_unread"]
    fields = ("recipient", "type", "title", "message", "rendezvous_datetime", "is_read")
    autocomplete_fields = ["recipient"]
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Personnalise le queryset pour le champ recipient dans l'autocomplete."""
        if db_field.name == "recipient":
            # Filtrer pour n'inclure que les utilisateurs avec un profil
            kwargs["queryset"] = User.objects.filter(
                Q(acteur_economique__isnull=False) |
                Q(institution_financiere__isnull=False) |
                Q(profil_emploi__isnull=False)
            ).select_related("acteur_economique", "institution_financiere", "profil_emploi").distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def recipient_display(self, obj):
        """Affiche le nom du destinataire selon son type."""
        return get_recipient_display_name(obj.recipient)
    recipient_display.short_description = "Destinataire"

    def sender(self, obj):
        if obj.created_by:
            return obj.created_by.get_username()
        return format_html("<i>system</i>")
    
    def get_search_results(self, request, queryset, search_term):
        """Personnalise la recherche pour inclure tous les types de destinataires."""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        if search_term:
            # Recherche dans les noms d'entreprises
            queryset |= queryset.filter(
                recipient__acteur_economique__raison_sociale__icontains=search_term
            )
            # Recherche dans les noms d'institutions
            queryset |= queryset.filter(
                recipient__institution_financiere__nom_institution__icontains=search_term
            )
            # Recherche dans les noms et prénoms des profils emploi
            queryset |= queryset.filter(
                Q(recipient__profil_emploi__nom__icontains=search_term) |
                Q(recipient__profil_emploi__prenoms__icontains=search_term)
            )
            use_distinct = True
        
        return queryset, use_distinct
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Marquer comme non lu"
