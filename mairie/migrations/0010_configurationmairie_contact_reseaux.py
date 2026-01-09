# Generated manually for contact and social media fields

import mairie.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mairie', '0009_configurationmairie_favicon'),
    ]

    operations = [
        migrations.AddField(
            model_name='configurationmairie',
            name='adresse',
            field=models.CharField(blank=True, default='Hôtel de Ville de Kpalimé', help_text="Adresse de la mairie (ex: Hôtel de Ville de Kpalimé)", max_length=255),
        ),
        migrations.AddField(
            model_name='configurationmairie',
            name='telephone',
            field=models.CharField(blank=True, default='+228 XX XX XX XX', help_text='Numéro de téléphone (ex: +228 XX XX XX XX)', max_length=50),
        ),
        migrations.AddField(
            model_name='configurationmairie',
            name='email',
            field=models.EmailField(blank=True, default='contact@mairiekloto1.tg', help_text='Adresse email de contact', max_length=254),
        ),
        migrations.AddField(
            model_name='configurationmairie',
            name='horaires',
            field=models.CharField(blank=True, default='Lundi - Vendredi : 08h00 - 17h00', help_text="Horaires d'ouverture (ex: Lundi - Vendredi : 08h00 - 17h00)", max_length=255),
        ),
        migrations.AddField(
            model_name='configurationmairie',
            name='url_facebook',
            field=models.URLField(blank=True, help_text='URL de la page Facebook'),
        ),
        migrations.AddField(
            model_name='configurationmairie',
            name='url_twitter',
            field=models.URLField(blank=True, help_text='URL du compte Twitter/X'),
        ),
        migrations.AddField(
            model_name='configurationmairie',
            name='url_instagram',
            field=models.URLField(blank=True, help_text='URL du compte Instagram'),
        ),
        migrations.AddField(
            model_name='configurationmairie',
            name='url_youtube',
            field=models.URLField(blank=True, help_text='URL de la chaîne YouTube'),
        ),
    ]
