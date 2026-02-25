# Generated migration for agents collecteurs ManyToMany

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("acteurs", "0008_geolocalisation_acteurs_institutions"),
        ("mairie", "0027_agent_collecteur"),
    ]

    operations = [
        migrations.AddField(
            model_name="acteureconomique",
            name="agents_collecteurs",
            field=models.ManyToManyField(
                blank=True,
                help_text="Agents collecteurs assignés pour la collecte des cotisations de cet acteur.",
                related_name="acteurs_economiques",
                to="mairie.agentcollecteur",
            ),
        ),
        migrations.AddField(
            model_name="institutionfinanciere",
            name="agents_collecteurs",
            field=models.ManyToManyField(
                blank=True,
                help_text="Agents collecteurs assignés pour la collecte des cotisations de cette institution.",
                related_name="institutions_financieres",
                to="mairie.agentcollecteur",
            ),
        ),
    ]
