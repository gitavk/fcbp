# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0033_auto_20180506_1148'),
        ('employees', '0005_auto_20170828_2044'),
        ('clients', '0061_clientpersonal_printed'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientpersonal',
            name='bonus_amount',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clientpersonal',
            name='bonus_type',
            field=models.ForeignKey(related_name=b'personals_bonus_type', blank=True, to='products.Discount', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clientpersonal',
            name='discount_amount',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clientpersonal',
            name='discount_type',
            field=models.ForeignKey(related_name=b'personals', blank=True, to='products.Discount', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clientpersonal',
            name='employee',
            field=models.ForeignKey(related_name=b'personals_emp', blank=True, to='employees.Employee', null=True),
            preserve_default=True,
        ),
    ]
