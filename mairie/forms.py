from django import forms
from .models import Candidature

class CandidatureForm(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = ['fichier_dossier', 'message_accompagnement']
        widgets = {
            'message_accompagnement': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Message optionnel pour accompagner votre dossier...',
                'class': 'form-control'
            }),
            'fichier_dossier': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            })
        }

    def clean_fichier_dossier(self):
        fichier = self.cleaned_data.get('fichier_dossier')
        if fichier:
            if not fichier.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Seuls les fichiers PDF sont acceptés.')
        return fichier
