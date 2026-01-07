from django.db import migrations


def remove_duplicates(apps, schema_editor):
    Candidature = apps.get_model('mairie', 'Candidature')
    from django.db.models import Count
    duplicates = (
        Candidature.objects.values('appel_offre_id', 'candidat_id')
        .annotate(cnt=Count('id'))
        .filter(cnt__gt=1)
    )
    for dup in duplicates:
        qs = Candidature.objects.filter(
            appel_offre_id=dup['appel_offre_id'],
            candidat_id=dup['candidat_id']
        ).order_by('date_soumission')
        ids_to_keep = [qs.first().id] if qs.exists() else []
        Candidature.objects.filter(
            appel_offre_id=dup['appel_offre_id'],
            candidat_id=dup['candidat_id']
        ).exclude(id__in=ids_to_keep).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mairie', '0006_merge_conflicts'),
    ]

    operations = [
        migrations.RunPython(remove_duplicates, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='candidature',
            unique_together={('appel_offre', 'candidat')},
        ),
    ]

