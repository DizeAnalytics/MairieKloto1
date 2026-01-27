# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mairie', '0019_informationmairie_pdc_choice'),
    ]

    operations = [
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(help_text='Nom du visiteur', max_length=255)),
                ('email', models.EmailField(help_text='Adresse email du visiteur', max_length=254)),
                ('telephone', models.CharField(blank=True, help_text='Numéro de téléphone (facultatif)', max_length=50)),
                ('sujet', models.CharField(help_text='Sujet de la suggestion', max_length=255)),
                ('message', models.TextField(help_text='Message détaillé de la suggestion')),
                ('date_soumission', models.DateTimeField(auto_now_add=True, help_text='Date et heure de soumission')),
                ('est_lue', models.BooleanField(default=False, help_text="Marquer comme lue par l'administration")),
                ('date_lecture', models.DateTimeField(blank=True, help_text="Date de lecture par l'administration", null=True)),
            ],
            options={
                'verbose_name': 'Suggestion',
                'verbose_name_plural': 'Suggestions',
                'ordering': ['-date_soumission'],
            },
        ),
    ]
