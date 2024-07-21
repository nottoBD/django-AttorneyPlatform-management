from django.db import migrations

def set_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    site_id = 1
    domain = 'neok-budget.be'
    name = 'Neok - Plateforme de Gestion des frais de Jurinet'

    Site.objects.update_or_create(
        id=site_id,
        defaults={
            'domain': domain,
            'name': name,
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(set_site),
    ]