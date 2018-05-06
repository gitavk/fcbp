# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core import serializers
from django.utils.translation import ugettext as _

from employees.models import Position


class Discount(models.Model):

    """
    Available discounts.
    """
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=150, unique=True)
    short = models.CharField(max_length=3, unique=True, null=True, blank=True)
    is_best_loyalty = models.BooleanField(default=False)


class Period(models.Model):

    """
    Period for club card types.
    Default values in month, other way in days.
    """
    value = models.SmallIntegerField()
    is_month = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('value', 'is_month')

    @property
    def name(self):
        p_dsc = 'month' if self.is_month else 'day'
        if self.value == 1:
            pname = _(p_dsc)
        elif self.value < 5:
            pname = _('p_{p_dsc}'.format(p_dsc=p_dsc))
        else:
            pname = _('p_{p_dsc}s'.format(p_dsc=p_dsc))
        return '{value} {pname}'.format(value=self.value, pname=pname)


class GenericProduct(object):

    @property
    def full_name(self):
        return '{ptype} {name}'.format(ptype=self.ptype, name=self.name)


class ClubCard(models.Model, GenericProduct):

    """
    Club card types.
    """
    ptype = u'Клубная карта'

    name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(
        max_length=20, blank=True, null=True, default='')
    max_visit = models.IntegerField()
    period = models.ForeignKey(Period, )
    is_full_time = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, blank=True)
    period_freeze = models.IntegerField(default=0, blank=True)
    freeze_times = models.IntegerField(default=0, blank=True)
    period_prolongation = models.IntegerField(default=0, blank=True)
    clients_count = models.IntegerField(default=1, blank=True)
    period_activation = models.IntegerField(default=0, blank=True)
    guest_training = models.SmallIntegerField(default=0, blank=True)
    fitness_testing_discount = models.BooleanField(default=False, blank=True)
    personal_training = models.BooleanField(default=False, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2,)

    @property
    def period_data(self):
        return self.period


class AquaAerobics(models.Model, GenericProduct):

    """
    Aqua Aerobics types.
    """
    ptype = u'Аквааэробика'

    name = models.CharField(max_length=255, unique=True)
    max_visit = models.IntegerField()
    period = models.ForeignKey(Period, )
    is_full_time = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, blank=True)
    clients_count = models.IntegerField(default=1, blank=True)
    period_prolongation = models.IntegerField(default=0, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2,)

    @property
    def period_data(self):
        return self.period


class Sport(models.Model):

    """
    Sports types.
    """
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True, blank=True)


class Training(models.Model):

    """
    Training types.
    """
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True, blank=True)
    order_num = models.IntegerField(default=0)
    for_personals = models.BooleanField(default=False, blank=True)


class Ticket(models.Model):

    """
    Ticket types
    """
    name = models.CharField(max_length=255, unique=True)
    period = models.ForeignKey(Period, )
    sport = models.ForeignKey(Sport, )
    is_full_time = models.BooleanField(default=True, blank=True)
    max_visit = models.IntegerField()
    period_prolongation = models.IntegerField(default=0, blank=True)
    is_active = models.BooleanField(default=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2,)

    @property
    def period_data(self):
        return self.period

    @property
    def sport_data(self):
        return self.sport

    @property
    def sport_name(self):
        return self.sport.name


class Personal(models.Model, GenericProduct):

    """
    Personal training.
    """
    ptype = u'Персональная тренировока'

    name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(
        max_length=20, blank=True, null=True, default='')
    period = models.ForeignKey(Period, )
    max_visit = models.IntegerField()
    clients_count = models.IntegerField(default=1, blank=True)
    is_full_time = models.BooleanField(default=True, blank=True)
    is_active = models.BooleanField(default=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2,)
    period_prolongation = models.IntegerField(default=0, blank=True)
    club_card_only = models.BooleanField(default=False)
    period_activation = models.IntegerField(default=0, blank=True)

    @property
    def period_data(self):
        return self.period

    @property
    def positions_pks(self):
        return self.positions.all().values_list('position__pk', flat=True)


class PersonalPosition(models.Model):

    """
    Trainer position for personal.
    """
    personal = models.ForeignKey(
        Personal, blank=True, null=True, related_name='positions')
    position = models.ForeignKey(Position, blank=True)

    class Meta:
        unique_together = ('personal', 'position')


class Timing(models.Model):

    """
    Products with counting time.
    The time in minutes.
    """
    name = models.CharField(max_length=255, unique=True)
    period = models.ForeignKey(Period, )
    price = models.DecimalField(max_digits=15, decimal_places=2,)
    period_prolongation = models.IntegerField(default=0, blank=True)
    period_freeze = models.IntegerField(default=0, blank=True)
    clients_count = models.IntegerField(default=1, blank=True)
    minutes = models.IntegerField(default=1, blank=True)
    is_active = models.BooleanField(default=True, blank=True)

    @property
    def period_data(self):
        return self.period


class CardText(models.Model):

    """
    Text for print cards.
    """
    text_types = (
        (1, 'клубная карта'),
        (2, 'персональная карта')
    )

    text_type = models.SmallIntegerField(choices=text_types, unique=True)
    header = models.TextField(null=True, blank=True)
    additional_header = models.TextField(null=True, blank=True)
    item1 = models.TextField(null=True, blank=True)
    employee = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    title = models.TextField(null=True, blank=True)

    @property
    def name(self):
        return dict(self.text_types)[self.text_type]

    def update_items(self, cardtextitems):
        """ Update all cardtextitems items """
        for o, item in enumerate(cardtextitems):
            try:
                old_item = CardTextItems.objects.get(
                    card_text=self, order=o+1)
                old_item.item = item['item']
                old_item.save()
            except CardTextItems.DoesNotExist:
                CardTextItems.objects.create(
                    card_text=self, order=o+1, item=item['item'])
        self.cardtextitems_set.filter(order__gt=len(cardtextitems)).delete()


class CardTextItems(models.Model):

    """ Text lines for print card."""
    date = models.DateTimeField(auto_now_add=True)
    card_text = models.ForeignKey(CardText)
    item = models.TextField()
    order = models.SmallIntegerField()
