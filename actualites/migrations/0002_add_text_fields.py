# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actualites', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actualite',
            name='texte1',
            field=models.TextField(blank=True, help_text='Texte avant la première photo.'),
        ),
        migrations.AddField(
            model_name='actualite',
            name='texte2',
            field=models.TextField(blank=True, help_text='Texte entre la première et la deuxième photo.'),
        ),
        migrations.AddField(
            model_name='actualite',
            name='texte3',
            field=models.TextField(blank=True, help_text='Texte entre la deuxième et la troisième photo.'),
        ),
        migrations.AddField(
            model_name='actualite',
            name='texte4',
            field=models.TextField(blank=True, help_text='Texte après la troisième photo.'),
        ),
        migrations.AlterField(
            model_name='actualite',
            name='contenu',
            field=models.TextField(blank=True, help_text="Contenu détaillé de l'actualité (ancien format, conservé pour compatibilité)."),
        ),
    ]

