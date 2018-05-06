# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0060_auto_20180114_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientpersonal',
            name='printed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
