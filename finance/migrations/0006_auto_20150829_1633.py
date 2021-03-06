# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_timing'),
        ('clients', '0003_auto_20150812_1736'),
        ('finance', '0005_payments_payment_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('payment_type', models.SmallIntegerField(default=1)),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('count', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)])),
                ('discount', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('aqua_aerobics', models.ForeignKey(blank=True, to='products.AquaAerobics', null=True)),
                ('client', models.ForeignKey(blank=True, to='clients.Client', null=True)),
                ('club_card', models.ForeignKey(blank=True, to='products.ClubCard', null=True)),
                ('credit', models.ForeignKey(blank=True, to='finance.Credit', null=True)),
                ('personal', models.ForeignKey(blank=True, to='products.Personal', null=True)),
                ('ticket', models.ForeignKey(blank=True, to='products.Ticket', null=True)),
                ('timing', models.ForeignKey(blank=True, to='products.Timing', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='payments',
            name='aqua_aerobics',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='client',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='club_card',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='credit',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='personal',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='ticket',
        ),
        migrations.RemoveField(
            model_name='payments',
            name='timing',
        ),
        migrations.DeleteModel(
            name='Payments',
        ),
    ]
