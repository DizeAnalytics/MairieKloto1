# Generated manually for PDC PDF field

from django.db import migrations, models
import mairie.models


class Migration(migrations.Migration):

    dependencies = [
        ('mairie', '0017_configurationmairie_whatsapp'),
    ]

    operations = [
        migrations.AddField(
            model_name='configurationmairie',
            name='pdc_pdf',
            field=models.FileField(blank=True, help_text='Plan de Développement Communal (PDF). Ce fichier sera accessible via un bouton flottant sur le site.', null=True, upload_to='mairie/pdc/', validators=[mairie.models.validate_file_size]),
        ),
    ]
