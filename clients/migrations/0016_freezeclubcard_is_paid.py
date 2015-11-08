# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0015_auto_20151103_0137'),
    ]

    operations = [
        migrations.AddField(
            model_name='freezeclubcard',
            name='is_paid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
