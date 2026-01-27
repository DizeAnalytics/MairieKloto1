# Generated manually on 2026-01-24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emploi', '0003_profilemploi_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilemploi',
            name='service_citoyen_obligatoire',
            field=models.BooleanField(default=False, help_text="Je m'engage à effectuer le service citoyen obligatoire (requis pour les jeunes diplômés sans emploi)."),
        ),
    ]