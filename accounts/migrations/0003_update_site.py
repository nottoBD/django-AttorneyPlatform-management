from django.db import migrations

def update_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    site, created = Site.objects.get_or_create(
        id=1,
        defaults={
            'domain': 'app.neok-budget.eu',
            'name': 'app.neok-budget.eu',
        }
    )
    if not created:
        site.domain = 'app.neok-budget.eu'
        site.name = 'app.neok-budget.eu'
        site.save()

class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('accounts', '0002_add_foreign_keys'),
    ]

    operations = [
        migrations.RunPython(update_site),
    ]
