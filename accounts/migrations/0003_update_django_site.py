from django.db import migrations

def update_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')

    Site.objects.update_or_create(
        id=1,
        defaults={
            'domain': 'app.neok-budget.eu',
            'name': 'app.neok-budget.eu',
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(update_site),
    ]
