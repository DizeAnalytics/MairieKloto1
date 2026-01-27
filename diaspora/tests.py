from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import MembreDiaspora


class MembreDiasporaModelTest(TestCase):
    """Tests pour le modèle MembreDiaspora."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_diaspora',
            email='test@example.com',
            password='testpass123'
        )
        
        self.membre = MembreDiaspora.objects.create(
            user=self.user,
            nom='Test',
            prenoms='Membre Diaspora',
            sexe='masculin',
            date_naissance='1990-01-01',
            nationalites='Togolaise',
            numero_piece_identite='123456789',
            pays_residence_actuelle='France',
            ville_residence_actuelle='Paris',
            adresse_complete_etranger='123 Rue de la Paix, 75001 Paris',
            commune_origine='Kloto 1',
            quartier_village_origine='Centre-ville',
            nom_parent_tuteur_originaire='Parent Test',
            annee_depart_pays=2015,
            frequence_retour_pays='chaque_annee',
            telephone_whatsapp='+33123456789',
            email='test@example.com',
            contact_au_pays_nom='Contact Togo',
            contact_au_pays_telephone='+22890123456',
            niveau_etudes='master',
            domaine_formation='Informatique',
            profession_actuelle='Développeur',
            secteur_activite='informatique',
            annees_experience=5,
            statut_professionnel='salarie',
            comment_contribuer='Contribuer au développement numérique',
            disposition_participation='oui',
            domaine_intervention_prioritaire='Informatique et éducation',
            accepte_rgpd=True,
            accepte_contact=True,
        )
    
    def test_membre_creation(self):
        """Test de création d'un membre de la diaspora."""
        self.assertEqual(self.membre.nom, 'Test')
        self.assertEqual(self.membre.prenoms, 'Membre Diaspora')
        self.assertEqual(self.membre.pays_residence_actuelle, 'France')
        self.assertFalse(self.membre.est_valide_par_mairie)
    
    def test_membre_str(self):
        """Test de la représentation string du membre."""
        expected = 'Test Membre Diaspora (France)'
        self.assertEqual(str(self.membre), expected)
    
    def test_get_appuis_financiers(self):
        """Test de la méthode get_appuis_financiers."""
        self.membre.appui_investissement_projets = True
        self.membre.appui_financement_infrastructures = True
        self.membre.save()
        
        appuis = self.membre.get_appuis_financiers()
        self.assertEqual(len(appuis), 2)
        self.assertIn('Investissement dans des projets communaux', appuis)
        self.assertIn('Financement d\'infrastructures', appuis)
    
    def test_get_competences_techniques(self):
        """Test de la méthode get_competences_techniques."""
        self.membre.transfert_competences = True
        self.membre.formation_jeunes = True
        self.membre.save()
        
        competences = self.membre.get_competences_techniques()
        self.assertEqual(len(competences), 2)
        self.assertIn('Transfert de compétences', competences)
        self.assertIn('Formation des jeunes', competences)


class DiasporaViewTest(TestCase):
    """Tests pour les vues de la diaspora."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_inscription_diaspora_get(self):
        """Test d'accès à la page d'inscription."""
        response = self.client.get(reverse('diaspora:inscription'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inscription')
    
    def test_inscription_diaspora_post_success(self):
        """Test d'inscription réussie."""
        data = {
            'username': 'nouveau_membre',
            'password': 'motdepasse123',
            'confirm_password': 'motdepasse123',
            'nom': 'Nouveau',
            'prenoms': 'Membre',
            'sexe': 'masculin',
            'date_naissance': '1985-05-15',
            'nationalites': 'Togolaise',
            'numero_piece_identite': '987654321',
            'pays_residence_actuelle': 'Allemagne',
            'ville_residence_actuelle': 'Berlin',
            'adresse_complete_etranger': 'Alexanderplatz 1, Berlin',
            'commune_origine': 'Kloto 1',
            'quartier_village_origine': 'Nouveau Quartier',
            'nom_parent_tuteur_originaire': 'Parent Nouveau',
            'annee_depart_pays': 2010,
            'frequence_retour_pays': 'tous_2_3_ans',
            'telephone_whatsapp': '+49123456789',
            'email': 'nouveau@example.com',
            'contact_au_pays_nom': 'Contact Berlin',
            'contact_au_pays_telephone': '+22890654321',
            'niveau_etudes': 'licence',
            'domaine_formation': 'Commerce',
            'profession_actuelle': 'Commercial',
            'secteur_activite': 'commerce',
            'annees_experience': 8,
            'statut_professionnel': 'entrepreneur',
            'comment_contribuer': 'Développer le commerce local',
            'disposition_participation': 'oui',
            'domaine_intervention_prioritaire': 'Commerce et entrepreneuriat',
            'accepte_rgpd': True,
            'accepte_contact': True,
        }
        
        response = self.client.post(reverse('diaspora:inscription'), data)
        # Doit rediriger vers le profil après inscription
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le membre a été créé
        self.assertTrue(MembreDiaspora.objects.filter(nom='Nouveau').exists())
    
    def test_liste_diaspora_requires_staff(self):
        """Test que la liste des membres nécessite d'être staff."""
        self.client.login(username='test_user', password='testpass123')
        response = self.client.get(reverse('diaspora:liste'))
        # Doit rediriger car l'utilisateur n'est pas staff
        self.assertEqual(response.status_code, 302)
    
    def test_modifier_diaspora_requires_login(self):
        """Test que la modification nécessite d'être connecté."""
        response = self.client.get(reverse('diaspora:modifier'))
        # Doit rediriger vers la page de connexion
        self.assertEqual(response.status_code, 302)