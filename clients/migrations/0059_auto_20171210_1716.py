# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0058_clientpersonal_block_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useclientpersonal',
            name='instructor',
            field=models.ForeignKey(related_name=b'personals', blank=True, to='employees.Employee', null=True),
        ),
    ]
