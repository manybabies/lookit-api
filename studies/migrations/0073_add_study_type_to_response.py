# Generated by Django 3.0.14 on 2021-07-12 19:52

import django.db.models.deletion
from django.db import migrations, models

import studies.models


class Migration(migrations.Migration):

    dependencies = [
        ("studies", "0072_external_study_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="response",
            name="study_type",
            field=models.ForeignKey(
                default=studies.models.StudyType.default_pk,
                on_delete=django.db.models.deletion.PROTECT,
                to="studies.StudyType",
            ),
        ),
    ]
