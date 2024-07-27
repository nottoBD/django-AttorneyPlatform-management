import uuid

import django.db.models.deletion
from django.db import migrations, models

from neok import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvocatCase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('avocat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_parents', to=settings.AUTH_USER_MODEL)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_lawyers', to='payments.Case')),
            ],
            options={
                'unique_together': {('avocat', 'case')},
            },
        ),
        migrations.CreateModel(
            name='JugeCase',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_judges', to='payments.Case')),
                ('juge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_parents_judge', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('juge', 'case')},
            },
        ),
    ]
