from mairie.models import AppelOffre

dossier_standard = """
1. Une lettre de motivation adressée à Monsieur le Maire.
2. Un CV détaillé et actualisé.
3. Une copie légalisée de la carte d'identité ou du passeport.
4. Une copie des diplômes et attestations.
5. Un casier judiciaire datant de moins de 3 mois.
"""

# Récupérer tous les appels d'offres
appels = AppelOffre.objects.all()

print(f"Mise à jour de {appels.count()} appels d'offres...")

for appel in appels:
    # On met à jour seulement si le champ est vide pour ne pas écraser d'éventuelles données manuelles (peu probable ici mais bonne pratique)
    if not appel.dossier_candidature:
        appel.dossier_candidature = dossier_standard
        appel.save()
        print(f" - Mis à jour : {appel.titre}")
    else:
        print(f" - Déjà renseigné : {appel.titre}")

print("Terminé !")
