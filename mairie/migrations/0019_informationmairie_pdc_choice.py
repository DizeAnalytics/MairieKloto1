# Generated manually for PDC type info choice

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mairie', '0018_configurationmairie_pdc_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='informationmairie',
            name='type_info',
            field=models.CharField(choices=[('contact', 'Contact'), ('horaire', 'Horaires'), ('adresse', 'Adresse'), ('mission', 'Mission/Vision'), ('histoire', 'Histoire'), ('pdc', 'PDC'), ('autre', 'Autre')], default='autre', max_length=20),
        ),
    ]
