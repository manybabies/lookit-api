# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-05 18:27
from __future__ import unicode_literals

import localflavor.us.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("accounts", "0014_auto_20170726_1403")]

    operations = [
        migrations.AlterField(
            model_name="demographicdata",
            name="state",
            field=localflavor.us.models.USStateField(blank=True, max_length=2),
        )
    ]
