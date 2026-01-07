from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.contrib.auth import get_user_model
from acteurs.models import ActeurEconomique
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    class Form(forms.ModelForm):
        class Meta:
            model = Notification
            fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            User = get_user_model()
            qs = User.objects.filter(acteur_economique__isnull=False).select_related("acteur_economique")
            self.fields["recipient"] = forms.ModelChoiceField(
                queryset=qs
            )
            def _label(u):
                ae = getattr(u, "acteur_economique", None)
                return ae.raison_sociale if ae else u.get_username()
            self.fields["recipient"].label_from_instance = _label

    form = Form
    list_display = ("title", "recipient_company", "type", "rendezvous_datetime", "is_read", "created_at", "sender")
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("title", "message", "recipient__username", "recipient__email", "recipient__acteur_economique__raison_sociale")
    date_hierarchy = "created_at"
    actions = ["mark_as_read", "mark_as_unread"]
    fields = ("recipient", "type", "title", "message", "rendezvous_datetime", "is_read")
    
    def recipient_company(self, obj):
        ae = getattr(obj.recipient, "acteur_economique", None)
        return ae.raison_sociale if ae else obj.recipient.get_username()
    recipient_company.short_description = "Destinataire"

    def sender(self, obj):
        if obj.created_by:
            return obj.created_by.get_username()
        return format_html("<i>system</i>")
    
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
