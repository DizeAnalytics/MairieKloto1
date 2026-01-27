# Generated manually

import mairie.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mairie', '0014_campagnepublicitaire_publicite'),
    ]

    operations = [
        migrations.CreateModel(
            name='Projet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(help_text='Titre du projet', max_length=255)),
                ('slug', models.SlugField(help_text="Identifiant technique pour l'URL (ex: rehabilitation-marche-central)", max_length=255, unique=True)),
                ('description', models.TextField(help_text='Description détaillée du projet')),
                ('resume', models.TextField(blank=True, help_text='Résumé court du projet (affiché dans la liste)')),
                ('statut', models.CharField(choices=[('en_cours', 'En cours'), ('realise', 'Réalisé')], default='en_cours', help_text='Statut du projet', max_length=20)),
                ('date_debut', models.DateField(help_text='Date de début du projet')),
                ('date_fin', models.DateField(blank=True, help_text='Date de fin du projet (surtout pour les projets réalisés)', null=True)),
                ('budget', models.DecimalField(blank=True, decimal_places=2, help_text='Budget alloué au projet (en FCFA)', max_digits=15, null=True)),
                ('localisation', models.CharField(blank=True, help_text='Localisation du projet (quartier, secteur, etc.)', max_length=255)),
                ('photo_principale', models.ImageField(blank=True, help_text='Photo principale du projet', null=True, upload_to='mairie/projets/', validators=[mairie.models.validate_file_size])),
                ('ordre_affichage', models.PositiveIntegerField(default=0, help_text="Ordre d'affichage (0 = premier, plus grand = plus bas)")),
                ('est_visible', models.BooleanField(default=True, help_text='Afficher ce projet sur le site public')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Projet',
                'verbose_name_plural': 'Projets',
                'ordering': ['ordre_affichage', '-date_debut', '-date_creation'],
            },
        ),
    ]
