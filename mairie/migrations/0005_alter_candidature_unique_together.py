from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mairie', '0004_candidature'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='candidature',
            unique_together=set(),
        ),
    ]

