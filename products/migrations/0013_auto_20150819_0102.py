# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_auto_20150819_0038'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tpersonalposition',
            name='personal',
        ),
        migrations.DeleteModel(
            name='tPersonalPosition',
        ),
        migrations.DeleteModel(
            name='vPersonalPosition',
        ),
    ]
