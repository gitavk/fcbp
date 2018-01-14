# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0059_auto_20171210_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useclientpersonal',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
