"""
Commande Django pour configurer le thème admin avec les couleurs du drapeau togolais.
Usage: python manage.py setup_theme_togo
"""
from django.core.management.base import BaseCommand
from admin_interface.models import Theme

# Couleurs du drapeau togolais
COULEURS_TOGO = {
    'vert': '#006233',      # Vert principal
    'jaune': '#FFCD00',     # Jaune/Or
    'rouge': '#D21034',     # Rouge
    'blanc': '#FFFFFF',     # Blanc
}


class Command(BaseCommand):
    help = 'Configure le theme admin avec les couleurs du drapeau togolais'

    def handle(self, *args, **options):
        """Configure le thème admin avec les couleurs du drapeau togolais."""
        
        # Récupérer ou créer le thème par défaut
        theme, created = Theme.objects.get_or_create(
            name='Theme Mairie Kloto 1',
            defaults={
                'active': True,
            }
        )
        
        if not created:
            self.stdout.write(
                self.style.WARNING(f"Theme '{theme.name}' trouve, mise a jour en cours...")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Creation du theme '{theme.name}'...")
            )
        
        # Configuration des couleurs principales
        theme.logo_visible = True
        theme.logo_max_height = 50
        theme.logo_max_width = 200
        
        # Couleurs du header (vert du drapeau)
        theme.css_header_background_color = COULEURS_TOGO['vert']
        theme.css_header_text_color = COULEURS_TOGO['blanc']
        theme.css_header_link_color = COULEURS_TOGO['jaune']
        theme.css_header_link_hover_color = COULEURS_TOGO['jaune']
        
        # Couleurs du module (jaune du drapeau pour les sections actives)
        theme.css_module_background_color = COULEURS_TOGO['jaune']
        theme.css_module_text_color = COULEURS_TOGO['vert']
        theme.css_module_link_color = COULEURS_TOGO['vert']
        theme.css_module_link_hover_color = COULEURS_TOGO['rouge']
        theme.css_module_rounded_corners = True
        
        # Couleurs des boutons (rouge du drapeau)
        theme.css_button_text_color = COULEURS_TOGO['blanc']
        theme.css_button_background_color = COULEURS_TOGO['rouge']
        theme.css_button_hover_background_color = COULEURS_TOGO['vert']
        
        # Couleurs des liens
        theme.css_generic_link_color = COULEURS_TOGO['rouge']
        theme.css_generic_link_hover_color = COULEURS_TOGO['vert']
        theme.css_generic_link_active_color = COULEURS_TOGO['vert']
        
        # Couleurs des champs de formulaire
        theme.css_text_color = '#333333'
        theme.css_text_font_size = '14px'
        
        # Couleurs des messages
        theme.css_success_background_color = COULEURS_TOGO['vert']
        theme.css_success_text_color = COULEURS_TOGO['blanc']
        theme.css_success_link_color = COULEURS_TOGO['jaune']
        
        theme.css_warning_background_color = COULEURS_TOGO['jaune']
        theme.css_warning_text_color = COULEURS_TOGO['vert']
        theme.css_warning_link_color = COULEURS_TOGO['rouge']
        
        theme.css_error_background_color = COULEURS_TOGO['rouge']
        theme.css_error_text_color = COULEURS_TOGO['blanc']
        theme.css_error_link_color = COULEURS_TOGO['jaune']
        
        # Autres options
        theme.list_filter_dropdown = True
        theme.list_filter_sticky = True
        theme.form_sticky = True
        theme.form_submit_sticky = True
        theme.foldable_apps = True
        theme.show_fieldsets_as_tabs = True
        theme.show_inlines_as_tabs = True
        theme.environment_name = 'Mairie de Kloto 1'
        theme.environment_color = COULEURS_TOGO['rouge']
        
        # Titre et favicon
        theme.title = 'Mairie de Kloto 1 - Administration'
        theme.title_visible = True
        
        theme.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'='*60}\n"
                f"THEME CONFIGURE AVEC SUCCES\n"
                f"{'='*60}\n"
                f"\nTheme: {theme.name}\n"
                f"Actif: {theme.active}\n"
                f"\nCouleurs appliquees:\n"
                f"  - Vert (Header): {COULEURS_TOGO['vert']}\n"
                f"  - Jaune (Modules): {COULEURS_TOGO['jaune']}\n"
                f"  - Rouge (Boutons): {COULEURS_TOGO['rouge']}\n"
                f"  - Blanc (Texte): {COULEURS_TOGO['blanc']}\n"
                f"\nAccedez a l'admin pour voir le nouveau theme:\n"
                f"   http://localhost:8000/Securelogin/\n"
                f"{'='*60}"
            )
        )

