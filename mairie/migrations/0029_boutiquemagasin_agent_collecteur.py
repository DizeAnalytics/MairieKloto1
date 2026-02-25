# Migration: Ajout du champ agent_collecteur à BoutiqueMagasin

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("mairie", "0028_boutiques_contribuable_null_types"),
    ]

    operations = [
        migrations.AddField(
            model_name="boutiquemagasin",
            name="agent_collecteur",
            field=models.ForeignKey(
                blank=True,
                help_text="Agent collecteur assigné à ce local pour la collecte des cotisations.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="boutiques_magasins",
                to="mairie.agentcollecteur",
            ),
        ),
    ]
