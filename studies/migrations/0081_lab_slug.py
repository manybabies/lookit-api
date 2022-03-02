# Generated by Django 3.2.11 on 2022-03-01 17:35

import re

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    LabModel = apps.get_model("studies", "Lab")
    db_alias = schema_editor.connection.alias
    labs = LabModel.objects.using(db_alias).only("name").all()
    for lab in labs:
        slug = lab.name.lower()
        slug = re.sub(r"[^a-z\s\.]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        lab.slug = slug
        lab.save()


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("studies", "0080_study_preview_summary"),
    ]

    operations = [
        migrations.AddField(
            model_name="lab",
            name="slug",
            field=models.SlugField(
                default=None,
                help_text="A unique URL (slug) that will show discoverable, active studies for "
                "this lab only, e.g. https://lookit.mit.edu/studies/my-lab-name",
                max_length=255,
                null=True,
                unique=True,
                verbose_name="Custom URL",
            ),
        ),
        migrations.AlterField(
            model_name="lab",
            name="contact_email",
            field=models.EmailField(
                help_text="This will be the reply-to address when you contact participants, so "
                "make sure it is a monitored address or list that lab members can access.",
                max_length=254,
                unique=True,
                verbose_name="Contact Email",
            ),
        ),
        migrations.AlterField(
            model_name="lab",
            name="lab_website",
            field=models.URLField(
                blank=True,
                help_text="A link to an external website, such as your university lab page",
                verbose_name="Lab Website",
            ),
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]
