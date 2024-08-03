"""
Neok-Budget: A Django-based web application for budgeting.
Copyright (C) 2024  David Botton, Arnaud Mahieu

Developed for Jurinet and its branch Neok-Budget.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
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