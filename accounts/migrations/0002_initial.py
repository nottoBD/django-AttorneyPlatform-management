# Generated by Django 5.0.3 on 2024-08-03 09:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='avocatcase',
            name='case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_lawyers', to='payments.case'),
        ),
        migrations.AddField(
            model_name='jugecase',
            name='case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_judges', to='payments.case'),
        ),
        migrations.AddField(
            model_name='jugecase',
            name='juge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_parents_judge', to=settings.AUTH_USER_MODEL),
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
