from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("acteurs", "0006_acteureconomique_sigle"),
    ]

    operations = [
        migrations.AddField(
            model_name="acteureconomique",
            name="situation",
            field=models.CharField(
                choices=[
                    ("dans_commune", "Dans la commune"),
                    ("hors_commune", "Hors commune"),
                ],
                default="dans_commune",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="institutionfinanciere",
            name="situation",
            field=models.CharField(
                choices=[
                    ("dans_commune", "Dans la commune"),
                    ("hors_commune", "Hors commune"),
                ],
                default="dans_commune",
                max_length=20,
            ),
        ),
    ]
