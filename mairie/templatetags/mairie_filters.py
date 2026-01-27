from django import template

register = template.Library()


@register.filter
def clean_phone(value):
    """Nettoie un numéro de téléphone pour les liens tel:."""
    if not value:
        return ""
    # Convertir en string si ce n'est pas déjà le cas
    value = str(value).strip()
    # Enlever les espaces, tirets, parenthèses et autres caractères
    cleaned = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "").replace("_", "")
    # S'assurer qu'il commence par + si ce n'est pas déjà le cas
    if not cleaned.startswith("+"):
        # Si ça commence par 228, ajouter +
        if cleaned.startswith("228"):
            cleaned = "+" + cleaned
        else:
            # Sinon, supposer que c'est un numéro local et ajouter +228
            cleaned = "+228" + cleaned
    return cleaned


@register.filter
def ussd_link(value):
    """
    Prépare une syntaxe de transfert (USSD) pour un lien tel:.
    Exemple en base : *145*1*NUM*MTN#  ->  *145*1*NUM*MTN%23
    """
    if not value:
        return ""
    v = str(value).strip()
    # enlever les espaces internes, garder *, chiffres, etc.
    v = v.replace(" ", "")
    # encoder le # pour les liens tel:
    v = v.replace("#", "%23")
    return v
