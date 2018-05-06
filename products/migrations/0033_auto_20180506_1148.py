# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def generate_personal_card_text(apps, schema_editor):
    CardText = apps.get_model('products', 'CardText')
    card_text = CardText.objects.get(pk=1)
    card_text.pk = None
    card_text.text_type = 2
    card_text.save()



class Migration(migrations.Migration):

    dependencies = [
        ('products', '0032_training_for_personals'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardtext',
            name='text_type',
            field=models.SmallIntegerField(unique=True, choices=[(1, '\u043a\u043b\u0443\u0431\u043d\u0430\u044f \u043a\u0430\u0440\u0442\u0430'), (2, '\u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u0430\u044f \u043a\u0430\u0440\u0442\u0430')]),
        ),
        migrations.RunPython(generate_personal_card_text),
    ]
