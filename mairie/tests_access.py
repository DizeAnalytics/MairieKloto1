from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from mairie.models import AppelOffre
from django.utils import timezone
from datetime import timedelta

class AccessControlTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.appel = AppelOffre.objects.create(
            titre="Test Appel",
            description="Description",
            date_debut=timezone.now(),
            date_fin=timezone.now() + timedelta(days=10),
            est_publie_sur_site=True,
            statut='publie'
        )

    def test_liste_appels_offres_requires_login(self):
        url = reverse('mairie:appels_offres')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/comptes/connexion/', response.url)

    def test_detail_appel_offre_requires_login(self):
        url = reverse('mairie:appel_offre_detail', args=[self.appel.pk])
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/comptes/connexion/', response.url)

    def test_pdf_appel_offre_requires_login(self):
        url = reverse('mairie:appel_offre_pdf', args=[self.appel.pk])
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/comptes/connexion/', response.url)

    def test_access_granted_when_logged_in(self):
        self.client.login(username='testuser', password='password')
        
        url_list = reverse('mairie:appels_offres')
        response_list = self.client.get(url_list)
        self.assertEqual(response_list.status_code, 200)

        url_detail = reverse('mairie:appel_offre_detail', args=[self.appel.pk])
        response_detail = self.client.get(url_detail)
        self.assertEqual(response_detail.status_code, 200)

    def test_link_visibility_unauthenticated(self):
        """Vérifie que le lien est visible même pour les utilisateurs non connectés."""
        url = reverse('mairie:accueil')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Le lien vers appels d'offres doit être présent
        self.assertContains(response, reverse('mairie:appels_offres'))
