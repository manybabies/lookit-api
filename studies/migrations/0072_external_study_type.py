# Generated by Django 3.0.14 on 2021-07-12 19:04

from django.db import migrations


def set_study_types(apps, schema_editor):
    StudyType = apps.get_model("studies.StudyType")
    StudyType.objects.create(
        name="External",
        configuration={
            "metadata": {
                "fields": [
                    {
                        "name": "url",
                        "value": "",
                        "input_type": "url",
                    },
                    {
                        "name": "scheduled",
                        "value": False,
                        "input_type": "checkbox",
                    },
                ]
            }
        },
    )


def unset_study_types(apps, schema_editor):
    StudyType = apps.get_model("studies.StudyType")
    StudyType.objects.filter(name="External").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("studies", "0071_remove_ordering_from_response"),
    ]

    operations = [migrations.RunPython(set_study_types, reverse_code=unset_study_types)]
