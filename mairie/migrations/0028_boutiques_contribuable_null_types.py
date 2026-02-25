# Migration: BoutiqueMagasin sans locataire obligatoire + types terrain/kiosque/réserve

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("mairie", "0027_agent_collecteur"),
    ]

    operations = [
        migrations.AlterField(
            model_name="boutiquemagasin",
            name="contribuable",
            field=models.ForeignKey(
                blank=True,
                help_text="Locataire (contribuable) du local. Vide si local non encore loué.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="boutiques_magasins",
                to="mairie.contribuable",
            ),
        ),
        migrations.AlterField(
            model_name="boutiquemagasin",
            name="activite_vendue",
            field=models.CharField(
                blank=True,
                help_text="Activité exercée par le locataire (ex: légumes, vêtements). Vide si non occupé.",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="boutiquemagasin",
            name="type_local",
            field=models.CharField(
                choices=[
                    ("magasin", "Magasin"),
                    ("boutique", "Boutique"),
                    ("local", "Local"),
                    ("terrain", "Terrain"),
                    ("kiosque", "Kiosque"),
                    ("reserve", "Réserve"),
                ],
                default="boutique",
                help_text="Type de local.",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="boutiquemagasin",
            name="superficie_m2",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Superficie en m².",
                max_digits=10,
            ),
        ),
        migrations.AlterField(
            model_name="boutiquemagasin",
            name="prix_location_mensuel",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Prix de location mensuel (FCFA).",
                max_digits=12,
            ),
        ),
    ]
