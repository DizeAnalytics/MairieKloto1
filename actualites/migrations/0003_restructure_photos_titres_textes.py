# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actualites', '0002_add_text_fields'),
    ]

    operations = [
        # Ajouter les nouveaux champs titre1, titre2, titre3
        migrations.AddField(
            model_name='actualite',
            name='titre1',
            field=models.CharField(blank=True, help_text='Titre pour la première photo', max_length=255),
        ),
        migrations.AddField(
            model_name='actualite',
            name='titre2',
            field=models.CharField(blank=True, help_text='Titre pour la deuxième photo', max_length=255),
        ),
        migrations.AddField(
            model_name='actualite',
            name='titre3',
            field=models.CharField(blank=True, help_text='Titre pour la troisième photo', max_length=255),
        ),
        # Supprimer le champ texte4
        migrations.RemoveField(
            model_name='actualite',
            name='texte4',
        ),
        # Mettre à jour les help_text des champs texte1, texte2, texte3
        migrations.AlterField(
            model_name='actualite',
            name='texte1',
            field=models.TextField(blank=True, help_text='Texte pour la première photo.'),
        ),
        migrations.AlterField(
            model_name='actualite',
            name='texte2',
            field=models.TextField(blank=True, help_text='Texte pour la deuxième photo.'),
        ),
        migrations.AlterField(
            model_name='actualite',
            name='texte3',
            field=models.TextField(blank=True, help_text='Texte pour la troisième photo.'),
        ),
    ]

