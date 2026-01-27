# Generated manually for WhatsApp field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mairie', '0016_projetphoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='configurationmairie',
            name='whatsapp',
            field=models.CharField(blank=True, help_text='Numéro WhatsApp (ex: +228 XX XX XX XX). Format: +228XXXXXXXXX (sans espaces ni tirets)', max_length=50),
        ),
    ]
