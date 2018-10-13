"""
Models for database views.
"""
from datetime import date
from django.db import models
from django.db.models import Sum

from products.models import ClubCard, AquaAerobics, Ticket, Personal, Timing
from .models import Client


class ClientClubCardActive(models.Model):
    """
    The clients club card,
    history and status.

    Date start - the date for the start period of activation.
    Date begin - is start of using the card.

    """
    date = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField()
    date_begin = models.DateField()
    date_end = models.DateField()
    client = models.ForeignKey(Client, )
    club_card = models.ForeignKey(ClubCard, )
    status = models.SmallIntegerField(default=2, blank=True, )
    """
    status valid data:
    0 - disabled
    1 - active
    2 - prospect
    """

    class Meta:
        db_table = 'v_client_club_card_active'
        managed = False

    @property
    def name(self):
        return self.club_card.name

    @property
    def rest_days(self):
        rest_days = (self.date_end - date.today()).days
        if rest_days < 1:
            return 0
        return rest_days

    @property
    def rest_visits(self):
        if self.club_card.max_visit == 99999:
            return '-'
        used = UseClientClubCard.objects.filter(client_club_card=self).count()
        return self.club_card.max_visit - used


class ClientAquaAerobics(models.Model):
    """
    The clients Aqua Aerobics card,
    history and status.

    Date start - the date for the start period of activation.
    Date begin - is start of using the card.

    """
    date = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField()
    date_begin = models.DateField()
    date_end = models.DateField()
    client = models.ForeignKey(Client, )
    aqua_aerobics = models.ForeignKey(AquaAerobics, )
    status = models.SmallIntegerField(default=2, blank=True, )
    """
    status valid data:
    0 - disabled
    1 - active
    2 - prospect
    """

    @property
    def name(self):
        return self.aqua_aerobics.name

    @property
    def rest_days(self):
        rest_days = (self.date_end - date.today()).days
        if rest_days < 1:
            return 0
        return rest_days

    @property
    def rest_visits(self):
        if self.aqua_aerobics.max_visit == 99999:
            return '-'
        used = UseClientAquaAerobics.objects.filter(client_aqua_aerobics=self)\
                                            .count()
        return self.aqua_aerobics.max_visit - used


class ClientTicket(models.Model):
    """
    The clients tickets,
    history and status.

    Date start - the date for the start period of activation.
    Date begin - is start of using the card.

    """
    date = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField()
    date_begin = models.DateField()
    date_end = models.DateField()
    client = models.ForeignKey(Client, )
    ticket = models.ForeignKey(Ticket, )
    status = models.SmallIntegerField(default=2, blank=True, )
    """
    status valid data:
    0 - disabled
    1 - active
    2 - prospect
    """

    @property
    def name(self):
        return self.ticket.name

    @property
    def rest_days(self):
        rest_days = (self.date_end - date.today()).days
        if rest_days < 1:
            return 0
        return rest_days

    @property
    def rest_visits(self):
        if self.ticket.max_visit == 99999:
            return '-'
        used = UseClientTicket.objects.filter(client_ticket=self).count()
        return self.ticket.max_visit - used


class ClientPersonal(models.Model):
    """
    The clients personals,
    history and status.

    Date start - the date for the start period of activation.
    Date begin - is start of using the card.

    """
    date = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField()
    date_begin = models.DateField()
    date_end = models.DateField()
    client = models.ForeignKey(Client, )
    personal = models.ForeignKey(Personal, )
    status = models.SmallIntegerField(default=2, blank=True, )
    """
    status valid data:
    0 - disabled
    1 - active
    2 - prospect
    """

    @property
    def name(self):
        return self.personal.name

    @property
    def rest_days(self):
        rest_days = (self.date_end - date.today()).days
        if rest_days < 1:
            return 0
        return rest_days

    @property
    def rest_visits(self):
        if self.personal.max_visit == 99999:
            return '-'
        used = UseClientPersonal.objects.filter(client_personal=self).count()
        return self.personal.max_visit - used


class ClientTiming(models.Model):
    """
    The clients timings,
    history and status.

    Date start - the date for the start period of activation.
    Date begin - is start of using the card.

    """
    date = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField()
    date_begin = models.DateField()
    date_end = models.DateField()
    client = models.ForeignKey(Client, )
    timing = models.ForeignKey(Timing, )
    status = models.SmallIntegerField(default=2, blank=True, )
    """
    status valid data:
    0 - disabled
    1 - active
    2 - prospect
    """

    @property
    def name(self):
        return self.timing.name

    @property
    def rest_days(self):
        rest_days = (self.date_end - date.today()).days
        if rest_days < 1:
            return 0
        return rest_days

    @property
    def rest_minutes(self):
        used = UseClientTiming.objects.filter(client_timing=self)\
                                      .aggregate(sum=Sum('minutes'))
        if used['sum']:
            return self.timing.minutes - used['sum']
        return self.timing.minutes
