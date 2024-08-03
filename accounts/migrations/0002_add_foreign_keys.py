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

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

def get_case_model():
    return 'payments.Case'

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='avocatcase',
            name='avocat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_parents', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='avocatcase',
            name='case',
            field=models.ForeignKey(get_case_model(), on_delete=django.db.models.deletion.CASCADE, related_name='assigned_lawyers'),
        ),
        migrations.AddField(
            model_name='jugecase',
            name='juge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_parents_judge', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='jugecase',
            name='case',
            field=models.ForeignKey(get_case_model(), on_delete=django.db.models.deletion.CASCADE, related_name='assigned_judges'),
        ),
        migrations.AlterUniqueTogether(
            name='avocatcase',
            unique_together={('avocat', 'case')},
        ),
        migrations.AlterUniqueTogether(
            name='jugecase',
            unique_together={('juge', 'case')},
        ),
    ]