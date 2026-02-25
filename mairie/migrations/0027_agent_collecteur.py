# Generated manually for AgentCollecteur

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("mairie", "0026_contribuables_marche"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AgentCollecteur",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("matricule", models.CharField(help_text="Matricule unique de l'agent (ex: AGT-2025-001).", max_length=50, unique=True)),
                ("nom", models.CharField(help_text="Nom de famille.", max_length=100)),
                ("prenom", models.CharField(help_text="Prénom(s).", max_length=150)),
                ("telephone", models.CharField(help_text="Numéro de téléphone de l'agent.", max_length=30)),
                ("email", models.EmailField(blank=True, help_text="Adresse email (si différente de celle du compte utilisateur).", max_length=254)),
                ("statut", models.CharField(choices=[("actif", "Actif"), ("inactif", "Inactif"), ("suspendu", "Suspendu")], default="actif", help_text="Statut de l'agent.", max_length=20)),
                ("date_embauche", models.DateField(blank=True, help_text="Date d'embauche de l'agent.", null=True)),
                ("notes", models.TextField(blank=True, help_text="Notes administratives sur l'agent (formations, observations, etc.).")),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("date_modification", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        help_text="Compte utilisateur de l'agent (pour connexion et authentification).",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="agent_collecteur",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Agent collecteur",
                "verbose_name_plural": "Agents collecteurs",
                "ordering": ["matricule", "nom", "prenom"],
            },
        ),
        migrations.AddField(
            model_name="agentcollecteur",
            name="emplacements_assignes",
            field=models.ManyToManyField(
                blank=True,
                help_text="Emplacements (marchés/places) assignés à cet agent pour la collecte.",
                related_name="agents_collecteurs",
                to="mairie.emplacementmarche",
            ),
        ),
        migrations.AddField(
            model_name="paiementcotisation",
            name="encaisse_par_agent",
            field=models.ForeignKey(
                blank=True,
                help_text="Agent collecteur ayant encaissé ce paiement.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="paiements_cotisations_encaisses",
                to="mairie.agentcollecteur",
            ),
        ),
        migrations.AddField(
            model_name="ticketmarche",
            name="encaisse_par_agent",
            field=models.ForeignKey(
                blank=True,
                help_text="Agent collecteur ayant vendu ce ticket.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tickets_marche_encaisses",
                to="mairie.agentcollecteur",
            ),
        ),
    ]
