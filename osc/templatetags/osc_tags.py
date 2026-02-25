from django import template

from osc.models import get_osc_type_display

register = template.Library()


@register.filter
def osc_type_display(value):
    """Retourne le libellé du type d'OSC à partir de sa valeur (code)."""
    return get_osc_type_display(value)
