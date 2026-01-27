// Mapping des icônes pour les types d'information de la mairie
(function($) {
    'use strict';
    
    // Mapping des types d'information vers leurs icônes correspondantes
    const iconMapping = {
        'contact': '📞',
        'horaire': '🕒',
        'adresse': '📍',
        'mission': '🎯',
        'histoire': '📚',
        'pdc': '📄',
        'autre': 'ℹ️'
    };
    
    // Fonction pour mettre à jour l'icône
    function updateIcon() {
        const typeInfoField = $('#id_type_info');
        const iconField = $('#id_icone');
        
        if (typeInfoField.length && iconField.length) {
            const selectedType = typeInfoField.val();
            
            // Mettre à jour l'icône si un type est sélectionné
            if (selectedType && iconMapping[selectedType]) {
                iconField.val(iconMapping[selectedType]);
            }
        }
    }
    
    // Attendre que le DOM soit chargé
    $(document).ready(function() {
        // Mettre à jour l'icône au chargement de la page si le champ icône est vide
        const iconField = $('#id_icone');
        if (!iconField.val() || iconField.val().trim() === '') {
            updateIcon();
        }
        
        // Toujours mettre à jour l'icône quand le type d'information change
        $('#id_type_info').on('change', function() {
            updateIcon();
        });
    });
    
})(django.jQuery);
