# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-07 17:33
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import project.fields.datetime_aware_jsonfield


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Response",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "results",
                    project.fields.datetime_aware_jsonfield.DateTimeAwareJSONField(
                        default=dict
                    ),
                ),
                (
                    "demographic_snapshot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="accounts.DemographicData",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="accounts.Profile",
                    ),
                ),
            ],
            options={"permissions": (("view_response", "View Response"),)},
        ),
        migrations.CreateModel(
            name="ResponseLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("action", models.CharField(max_length=128)),
                (
                    "response",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="studies.Response",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Study",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("uuid", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("short_description", models.TextField()),
                ("long_description", models.TextField()),
                ("criteria", models.TextField()),
                ("duration", models.TextField()),
                ("contact_info", models.TextField()),
                ("image", models.ImageField(null=True, upload_to="")),
                (
                    "blocks",
                    project.fields.datetime_aware_jsonfield.DateTimeAwareJSONField(
                        default=dict
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("submitted", "Submitted"),
                            ("rejected", "Rejected"),
                            ("retracted", "Retracted"),
                            ("approved", "Approved"),
                            ("active", "Active"),
                            ("paused", "Paused"),
                            ("deactivated", "Deactivated"),
                        ],
                        default="created",
                        max_length=25,
                    ),
                ),
                ("public", models.BooleanField(default=False)),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="studies",
                        related_query_name="study",
                        to="accounts.Organization",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("can_view", "Can View"),
                    ("can_create", "Can Create"),
                    ("can_edit", "Can Edit"),
                    ("can_remove", "Can Remove"),
                    ("can_activate", "Can Activate"),
                    ("can_deactivate", "Can Deactivate"),
                    ("can_pause", "Can Pause"),
                    ("can_resume", "Can Resume"),
                    ("can_approve", "Can Approve"),
                    ("can_submit", "Can Submit"),
                    ("can_retract", "Can Retract"),
                    ("can_resubmit", "Can Resubmit"),
                    ("can_edit_permissions", "Can Edit Permissions"),
                    ("can_view_permissions", "Can View Permissions"),
                    ("can_view_responses", "Can View Responses"),
                    ("can_view_video_responses", "Can View Video Responses"),
                    ("can_view_demographics", "Can View Demographics"),
                )
            },
        ),
        migrations.CreateModel(
            name="StudyLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("action", models.CharField(max_length=128)),
                (
                    "study",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="logs",
                        related_query_name="logs",
                        to="studies.Study",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.AddField(
            model_name="response",
            name="study",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="responses",
                to="studies.Study",
            ),
        ),
    ]
