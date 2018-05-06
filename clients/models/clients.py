# -*- coding: utf-8 -*-
import os
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import Sum, Q
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver

from products.models import (
    ClubCard, AquaAerobics, Ticket, Personal, Timing, Discount, Training)
from employees.models import Employee
from .generic import Property, Prolongation, WritePayment


class Client(models.Model):

    """
    Clients data.
    """
    date = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30)
    born = models.DateField()
    uid = models.IntegerField(default=0)
    card = models.BigIntegerField(blank=True, null=True)

    mobile = models.BigIntegerField(null=True, blank=True)
    gender = models.SmallIntegerField(default=0, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    passport_number = models.TextField(null=True, blank=True)
    passport_date = models.DateField(null=True, blank=True)
    passport_issued = models.TextField(null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatar/", null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    introductory_date = models.DateTimeField(blank=True, null=True)
    introductory_employee = models.ForeignKey(Employee, blank=True, null=True)

    @property
    def passport(self):
        return '%s %s %s' % (
            self.passport_number, self.passport_date, self.passport_issued)

    @property
    def full_name(self,):
        return "%s %s %s" % (self.last_name, self.first_name, self.patronymic)

    @property
    def initials(self,):
        return "%s %s. %s." % (
            self.last_name, self.first_name[:1], self.patronymic[:1])

    @property
    def online_clubcard(self,):
        return ClientOnline.objects.filter(client=self, product='clubcard')\
                           .exists()

    @property
    def introductory_employee_name(self,):
        return self.introductory_employee.initials

    @property
    def online_aqua(self,):
        return ClientOnline.objects.filter(client=self, product='aqua')\
                           .exists()

    @property
    def online_ticket(self,):
        return ClientOnline.objects.filter(client=self, product='ticket')\
                           .exists()

    @property
    def online_personal(self,):
        return ClientOnline.objects.filter(client=self, product='personal')\
                           .exists()

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return ""

    @property
    def has_clientclubcard(self):
        return self.clientclubcard_set.filter(status__gt=0).exists()

    @property
    def has_clientaquaaerobics(self):
        return self.clientaquaaerobics_set.filter(status__gt=0).exists()

    @property
    def has_clientticket(self):
        return self.clientticket_set.filter(status__gt=0).exists()

    @property
    def has_clientpersonal(self):
        if self.clientpersonal_set.filter(status__gt=0).exists():
            return True
        else:
            return self.extra_personals.filter(personal__status__gt=0).exists()

    @property
    def has_clienttiming(self):
        return self.clienttiming_set.filter(status__gt=0).exists()

    @property
    def active_cc(self):
        """Client's active club cards"""
        return self.clientclubcard_set.filter(status__gt=0)

    @property
    def active_cc_first(self):
        """Client's active club cards"""
        return self.active_cc.first()

    @property
    def initial_purchase(self):
        initial_card = self.clientclubcard_set.order_by('date').first()
        initial_personal = self.clientpersonal_set.order_by('date').first()
        if not initial_personal:
            # look by extra personals
            extra_p = self.extra_personals.order_by('personal__date').first()
            if extra_p:
                initial_personal = extra_p.personal
        if initial_card and initial_personal:
            if initial_card.date < initial_personal.date:
                return initial_card
            else:
                return initial_personal
        return initial_card or initial_personal

    def save(self, *args, **kwargs):
        if not self.uid:
            mon = date.today() + timedelta(days=-date.today().weekday())
            week_clients = Client.objects.filter(date__gte=mon).count()
            year = (date.today().year - 2000) * 10000
            week = date.today().isocalendar()[1] * 100
            cnt = week_clients + 1
            self.uid = year + week + cnt
            self.first_name = self.first_name.strip()
            self.last_name = self.last_name.strip()
            self.patronymic = self.patronymic.strip()
        super(Client, self).save(*args, **kwargs)


@receiver(pre_save, sender=Client)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Client` object is changed.
    """
    if not instance.pk:
        return False
    try:
        old_file = Client.objects.get(pk=instance.pk).avatar
    except Client.DoesNotExist:
        return False

    new_file = instance.avatar
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class ClientClubCard(Property, WritePayment, models.Model):

    """
    The clients club card,
    history and status.

    Date start - the date for the start period of activation.
    Date begin - is start of using the card.

    """
    date = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField(blank=True)
    date_begin = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    client = models.ForeignKey(Client, )
    club_card = models.ForeignKey(ClubCard, )
    is_paid_activate = models.BooleanField(default=False)
    paid_activate_amount = models.IntegerField(blank=True, null=True)
    discount_type = models.ForeignKey(Discount, blank=True, null=True)
    discount_amount = models.FloatField(blank=True, null=True)
    bonus_type = models.ForeignKey(Discount, blank=True, null=True,
                                   related_name="club_card_bonus_type")
    bonus_amount = models.FloatField(blank=True, null=True)
    block_comment = models.CharField(max_length=150, blank=True, null=True)
    status = models.SmallIntegerField(default=2, blank=True, )
    employee = models.ForeignKey(Employee, blank=True, null=True)
    printed = models.BooleanField(default=False)
    """
    status valid data:
    0 - disabled
    1 - active
    2 - prospect
    """

    freeze_class = 'FreezeClubCard'
    paid_text = 'paid activate'
    payment_goods = 'club_card'

    def save(self, *args, **kwargs):
        if self.status == 0:
            if not self.date_begin:
                self.date_begin = date.today()
                self.date_end = date.today()
            else:
                self.date_end = date.today()
        if self.pk:
            old_date_begin = ClientClubCard.objects.get(pk=self.pk).date_begin
            if old_date_begin:
                delta_begin = self.date_begin - old_date_begin
                if delta_begin:
                    self.date_end = date_end(self.date_begin, self.club_card)
        super(ClientClubCard, self).save(*args, **kwargs)

    def activate(self, date_begin=None):
        self.date_begin = date_begin if date_begin else date.today()
        self.date_end = date_end(self.date_begin, self.club_card)
        self.status = 1
        self.save()

    def deactivate(self, ):
        self.status = 0
        self.save()

    def previous_card(self, **kwargs):
        exclude_single = kwargs.get('exclude_single')
        ccc = ClientClubCard.objects.filter(
            date__lt=self.date, client=self.client)
        if exclude_single:
            ccc = ccc.exclude(club_card__max_visit=1)
        return ccc.order_by('-date').first()

    @property
    def infuture(self):
        if self.date_begin:
            return self.date_begin > date.today()
        return False

    @property
    def is_paid(self):
        return self.is_paid_activate

    @property
    def product(self):
        return self.club_card

    @property
    def discount_name(self):
        if self.discount_type:
            return '%s %s' % (self.discount_type.description,
                              self.discount_amount)
        else:
            return ''

    @property
    def discount_value(self):
        if self.discount_type:
            return self.discount_amount
        elif self.bonus_type:
            return self.bonus_amount
        else:
            return ''

    @property
    def discount_short(self):
        if self.discount_type:
            return self.discount_type.short
        elif self.bonus_type:
            return self.bonus_type.short
        else:
            return ''

    @property
    def discount_description(self):
        if self.discount_type:
            return self.discount_type.description
        elif self.bonus_type:
            return self.bonus_type.description
        else:
            return ''

    @property
    def period(self):
        if self.club_card.period.is_month:
            return u'%s месяцев' % self.club_card.period.value
        else:
            return u'%s дней' % self.club_card.period.value

    @property
    def personal_training(self):
        if self.club_card.personal_training:
            return 1
        else:
            return 0

    @property
    def rest_days(self):
        if not self.date_end:
            return None
        rest_days = (self.date_end - date.today()).days
        if rest_days < 1:
            return 0
        return rest_days

    @property
    def rest_visits(self):
        # return string if max
        if self.club_card.max_visit == 99999:
            return '-'
        visits = UseClientClubCard.objects.filter(client_club_card=self)
        used = ClubCardTrains.objects.filter(visit__in=visits).count()
        return self.club_card.max_visit - used

    @property
    def rest_visits_int(self):
        # return number if max
        if self.club_card.max_visit == 99999:
            return 99999
        visits = UseClientClubCard.objects.filter(client_club_card=self)
        used = ClubCardTrains.objects.filter(visit__in=visits).count()
        return self.club_card.max_visit - used

    @property
    def is_online(self):
        return UseClientClubCard.objects.filter(client_club_card=self,
                                                end__isnull=True).count()

    @property
    def rest_guest(self):
        guests = GuestClubCard.objects\
                              .filter(client_club_card=self).count()
        return self.club_card.guest_training - guests

    @property
    def rest_prolongation(self):
        prolongation = ProlongationClubCard.objects\
            .filter(client_club_card=self, is_extra=False)\
            .aggregate(sum=Sum('days'))
        if prolongation['sum']:
            return self.club_card.period_prolongation - prolongation['sum']
        return self.club_card.period_prolongation

    @property
    def rest_freeze(self):
        freeze = FreezeClubCard.objects\
                               .filter(client_club_card=self, is_extra=False)\
                               .aggregate(sum=Sum('days'))
        if freeze['sum']:
            return self.club_card.period_freeze - freeze['sum']
        return self.club_card.period_freeze

    @property
    def rest_freeze_times(self):
        times = FreezeClubCard.objects.filter(
            client_club_card=self, is_extra=False).count()
        return self.club_card.freeze_times - times

    @property
    def guest_training(self):
        return self.club_card.guest_training

    @property
    def fitness_testing_discount(self):
        if FitnessClubCard.objects.filter(client_club_card=self).exists():
            return False
        return self.club_card.fitness_testing_discount

    @property
    def personal_training(self):
        if PersonalClubCard.objects.filter(client_club_card=self).exists():
            return False
        return self.club_card.personal_training

    @property
    def is_frozen(self):
        freezes = FreezeClubCard.objects\
                                .filter(client_club_card=self,
                                        fdate__lte=date.today())
        for f in freezes:
            if f.tdate >= date.today():
                return True
        return False

    def ext_prolongation(self):
        result = []
        paid = self.prolongation.filter(is_paid=True).order_by('date')
        paid = paid.values('date', 'amount', 'days')
        extra = self.prolongation.filter(is_extra=True).order_by('date')
        extra = extra.values('days', 'note')
        l1_len = len(paid)
        l2_len = len(extra)
        for i in range(max(l1_len, l2_len)):
            list_len = i + 1
            if l1_len >= list_len and l2_len >= list_len:
                p = paid[i]
                e = extra[i]
                join_l = (
                    p.get('date').strftime('%d.%m.%Y'),
                    p.get('amount'), p.get('days'),
                    e.get('days'), e.get('note'))
            elif l2_len >= list_len:
                e = extra[i]
                join_l = (
                    '', '', '',
                    e.get('days'), e.get('note'))
            else:
                p = paid[i]
                join_l = (
                    p.get('date').strftime('%d.%m.%Y'),
                    p.get('amount'), p.get('days'),
                    '', '')
            result.append(join_l)
        return result

    def freeze_stat(self):
        result = []
        free_total = self.club_card.period_freeze
        free = self.freeze.filter(
            is_paid=False, is_extra=False).order_by('date')
        paid = self.freeze.filter(is_paid=True).order_by('date')
        extra = self.freeze.filter(is_extra=True).order_by('date')
        l0_len = len(free)
        l1_len = len(paid)
        l2_len = len(extra)
        for i in range(max(l0_len, l1_len, l2_len)):
            list_len = i + 1
            free_in = l0_len >= list_len
            paid_in = l1_len >= list_len
            extra_in = l2_len >= list_len
            if free_in and paid_in and extra_in:
                f = free[i]
                free_total -= f.days
                p = paid[i]
                e = extra[i]
                join_l = (
                    f.fdate.strftime('%d.%m.%Y'),
                    f.tdate.strftime('%d.%m.%Y'),
                    f.days, free_total,
                    p.date.strftime('%d.%m.%Y'), p.amount, p.days,
                    p.fdate.strftime('%d.%m.%Y'),
                    p.tdate.strftime('%d.%m.%Y'),
                    e.days,
                    e.fdate.strftime('%d.%m.%Y'),
                    e.tdate.strftime('%d.%m.%Y'),
                    e.note)
            elif free_in and paid_in:
                f = free[i]
                free_total -= f.days
                p = paid[i]
                join_l = (
                    f.fdate.strftime('%d.%m.%Y'),
                    f.tdate.strftime('%d.%m.%Y'),
                    f.days, free_total,
                    p.date.strftime('%d.%m.%Y'), p.amount, p.days,
                    p.fdate.strftime('%d.%m.%Y'),
                    p.tdate.strftime('%d.%m.%Y'),
                    '', '', '', '')
            elif free_in and extra_in:
                f = free[i]
                free_total -= f.days
                e = extra[i]
                join_l = (
                    f.fdate.strftime('%d.%m.%Y'),
                    f.tdate.strftime('%d.%m.%Y'),
                    f.days, free_total,
                    '', '', '', '', '',
                    e.days,
                    e.fdate.strftime('%d.%m.%Y'),
                    e.tdate.strftime('%d.%m.%Y'),
                    e.note)
            elif paid_in and extra_in:
                p = paid[i]
                e = extra[i]
                join_l = (
                    '', '', '', '',
                    p.date.strftime('%d.%m.%Y'), p.amount, p.days,
                    p.fdate.strftime('%d.%m.%Y'),
                    p.tdate.strftime('%d.%m.%Y'),
                    e.days,
                    e.fdate.strftime('%d.%m.%Y'),
                    e.tdate.strftime('%d.%m.%Y'),
                    e.note)
            elif free_in:
                f = free[i]
                free_total -= f.days
                join_l = (
                    f.fdate.strftime('%d.%m.%Y'),
                    f.tdate.strftime('%d.%m.%Y'),
                    f.days, free_total,
                    '', '', '', '', '',
                    '', '', '', '')
            elif paid_in:
                p = paid[i]
                join_l = (
                    '', '', '', '',
                    p.date.strftime('%d.%m.%Y'), p.amount, p.days,
                    p.fdate.strftime('%d.%m.%Y'),
                    p.tdate.strftime('%d.%m.%Y'),
                    '', '', '', '')
            else:
                e = extra[i]
                join_l = (
                    '', '', '', '',
                    '', '', '', '', '',
                    e.days,
                    e.fdate.strftime('%d.%m.%Y'),
                    e.tdate.strftime('%d.%m.%Y'),
                    e.note)
            result.append(join_l)
        return result


class ProlongationClubCard(Prolongation, WritePayment, models.Model):

    """
    Prolongation for the Client Club Card.
    """
    paid_text = 'paid prolongation'
    payment_goods = 'club_card'

    date = models.DateTimeField()
    client_club_card = models.ForeignKey(ClientClubCard,
                                         related_name='prolongation')
    days = models.SmallIntegerField()
    amount = models.DecimalField(max_digits=15, decimal_places=2,)
    is_paid = models.BooleanField(default=False)
    is_extra = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)

    @property
    def parent(self):
        return self.client_club_card

    def save(self, *args, **kwargs):
        payment_type = kwargs.pop('payment_type', 1)
        self.add_payment(payment_type)
        if not self.pk:
            self.parent_upd(self,)
        super(ProlongationClubCard, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.parent_upd(self, is_delete=True)
        super(ProlongationClubCard, self).delete(*args, **kwargs)


class GuestClubCard(models.Model):

    """
    Guest training for the Client Club Card.
    """
    date = models.DateTimeField(auto_now_add=True)
    client_club_card = models.ForeignKey(ClientClubCard)
    guest = models.CharField(max_length=60)
    phone = models.BigIntegerField()
    born = models.DateField(null=True, blank=True)
    passport = models.TextField(null=True, blank=True)


class FitnessClubCard(models.Model):

    """
    Fitness  testing discount for the Client Club Card.
    """
    date = models.DateTimeField()
    client_club_card = models.ForeignKey(ClientClubCard)
    personal = models.ForeignKey(Employee, )

    def save(self, *args, **kwargs):
        if not self.pk:
            card = self.client_club_card
            if not card.date_begin:
                card.date_begin = date.today()
                card.date_end = date_end(date.today(), card.club_card)
                card.save()
        super(FitnessClubCard, self).save(*args, **kwargs)

    @property
    def employee(self):
        return self.personal.initials


class PersonalClubCard(models.Model):

    """
    Personal training discount for the Client Club Card.
    """
    date = models.DateTimeField()
    client_club_card = models.ForeignKey(ClientClubCard)
    personal = models.ForeignKey(Employee)

    @property
    def employee(self):
        return self.personal.initials


class FreezeClubCard(WritePayment, models.Model):

    """
    Freeze club card.
    """
    product = 'client_club_card'
    paid_text = 'paid freeze'
    payment_goods = 'club_card'

    date = models.DateTimeField(auto_now_add=True)
    client_club_card = models.ForeignKey(ClientClubCard,
                                         related_name='freeze')
    fdate = models.DateField()
    days = models.SmallIntegerField()
    is_paid = models.BooleanField(default=False)
    amount = models.IntegerField(blank=True, null=True)
    is_extra = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)

    @property
    def tdate(self):
        return self.fdate + timedelta(days=(self.days-1))

    @property
    def parent(self):
        return self.client_club_card

    def save(self, *args, **kwargs):
        payment_type = kwargs.pop('payment_type', 1)
        self.add_payment(payment_type)
        super(FreezeClubCard, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        cc = self.client_club_card
        cc.date_end = cc.date_end - timedelta(days=self.days)
        cc.save()
        super(FreezeClubCard, self).delete(*args, **kwargs)


class ClientAquaAerobics(Property, models.Model):

    """
    The clients Aqua Aerobics card,
    history and status.

    Date start - the date for the start period of activation.
    Date begin - is start of using the card.

    """

    freeze_class = 'FreezeAqua'

    date = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField(blank=True)
    date_begin = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    client = models.ForeignKey(Client, )
    aqua_aerobics = models.ForeignKey(AquaAerobics, )
    discount_type = models.ForeignKey(Discount, blank=True, null=True)
    discount_amount = models.FloatField(blank=True, null=True)
    bonus_type = models.ForeignKey(Discount, blank=True, null=True,
                                   related_name="aqua_bonus_type")
    bonus_amount = models.FloatField(blank=True, null=True)
    employee = models.ForeignKey(Employee, blank=True, null=True)
    printed = models.BooleanField(default=False)
    is_paid_activate = models.BooleanField(default=False)
    paid_activate_amount = models.IntegerField(blank=True, null=True)
    block_comment = models.CharField(max_length=150, blank=True, null=True)
    status = models.SmallIntegerField(default=2, blank=True, )
    """
    status valid data:
    0 - disabled
    1 - active
    2 - prospect
    """

    @property
    def product(self):
        return self.aqua_aerobics

    @property
    def extra_client(self):
        clients = self.aquaaerobicsclients_set.all().values('client')
        return Client.objects.filter(pk__in=clients)

    @property
    def rest_days(self):
        if not self.date_end:
            return None
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

    @property
    def is_online(self):
        return UseClientAquaAerobics.objects.filter(client_aqua_aerobics=self,
                                                    end__isnull=True).count()

    @property
    def is_frozen(self):
        freezes = FreezeAqua.objects\
                            .filter(client_aqua=self,
                                    fdate__lte=date.today())
        for f in freezes:
            if f.tdate >= date.today():
                return True
        return False


class FreezeAqua(models.Model):

    """Freeze aqua aerobics."""
    product = 'client_aqua'

    date = models.DateTimeField(auto_now_add=True)
    client_aqua = models.ForeignKey(ClientAquaAerobics)
    fdate = models.DateField()
    days = models.SmallIntegerField()
    is_paid = models.BooleanField(default=False)
    amount = models.IntegerField(blank=True, null=True)

    @property
    def tdate(self):
        return self.fdate + timedelta(days=(self.days-1))


class ProlongationAqua(Prolongation, models.Model):

    """
    Prolongation for the Client Club Card.
    """
    date = models.DateTimeField()
    client_aqua = models.ForeignKey(ClientAquaAerobics)
    days = models.SmallIntegerField()
    amount = models.DecimalField(max_digits=15, decimal_places=2,)
    is_paid = models.BooleanField(default=False)

    @property
    def parent(self):
        return self.client_aqua

    def save(self, *args, **kwargs):
        if not self.pk:
            self.parent_upd(self,)
        super(ProlongationAqua, self).save(*args, **kwargs)


class AquaAerobicsClients(models.Model):

    """
    External clients for the ClientAquaAerobics.
    """
    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, )
    client_aqua = models.ForeignKey(ClientAquaAerobics,)

    class Meta:
        unique_together = ('client', 'client_aqua')


class ClientAquaAerobicsFull(models.Model):

    """
    The clients Aqua Aerobics card FULL JOIN
    with Aqua Aerobics Clients (External clients for the ClientAquaAerobics),
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

    class Meta:
        db_table = 'v_external_aqua'
        managed = False

    @property
    def name(self):
        return self.aqua_aerobics.name

    @property
    def rest_days(self):
        if not self.date_end:
            return None
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

    @property
    def is_online(self):
        return UseClientAquaAerobics.objects.filter(client_aqua_aerobics=self,
                                                    end__isnull=True).count()

    @property
    def is_frozen(self):
        freezes = FreezeAqua.objects\
                            .filter(client_aqua=self,
                                    fdate__lte=date.today())
        for f in freezes:
            if f.tdate >= date.today():
                return True
        return False


class ClientTicket(Property, models.Model):

    """
    The clients tickets,
    history and status.

    Date start - the date for the start period of activation.
    Date begin - is start of using the card.
    """

    freeze_class = 'FreezeTicket'

    date = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField(blank=True)
    date_begin = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    client = models.ForeignKey(Client, )
    ticket = models.ForeignKey(Ticket, )
    discount_type = models.ForeignKey(Discount, blank=True, null=True)
    discount_amount = models.FloatField(blank=True, null=True)
    bonus_type = models.ForeignKey(Discount, blank=True, null=True,
                                   related_name="ticket_bonus_type")
    bonus_amount = models.FloatField(blank=True, null=True)
    status = models.SmallIntegerField(default=2, blank=True, )
    printed = models.BooleanField(default=False)
    block_comment = models.CharField(max_length=150, blank=True, null=True)
    """
    status valid data:
    0 - disabled
    1 - active
    2 - prospect
    """

    @property
    def client_name(self):
        return self.client.full_name

    @property
    def name(self):
        return self.ticket.name

    @property
    def is_frozen(self):
        freezes = FreezeTicket.objects\
            .filter(client_ticket=self,
                    fdate__lte=date.today())
        for f in freezes:
            if f.tdate >= date.today():
                return True
        return False

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

    @property
    def is_online(self):
        return UseClientTicket.objects.filter(client_ticket=self,
                                              end__isnull=True).count()


class FreezeTicket(models.Model):

    """Freeze ticket."""
    product = 'client_ticket'

    date = models.DateTimeField(auto_now_add=True)
    client_ticket = models.ForeignKey(ClientTicket)
    fdate = models.DateField()
    days = models.SmallIntegerField()
    is_paid = models.BooleanField(default=False)
    amount = models.IntegerField(blank=True, null=True)

    @property
    def tdate(self):
        return self.fdate + timedelta(days=(self.days-1))


class ProlongationTicket(Prolongation, models.Model):

    """
    Prolongation for the Client Ticket.
    """
    date = models.DateTimeField()
    client_ticket = models.ForeignKey(ClientTicket)
    days = models.SmallIntegerField()
    amount = models.DecimalField(max_digits=15, decimal_places=2,)
    is_paid = models.BooleanField(default=False)

    @property
    def parent(self):
        return self.client_ticket

    def save(self, *args, **kwargs):
        if not self.pk:
            self.parent_upd(self,)
        super(ProlongationTicket, self).save(*args, **kwargs)


class ClientPersonal(Property, models.Model):

    """
    The clients personals,
    history and status.

    Date start - the date for the start period of activation.
    Date begin - is start of using the card.

    """

    date = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField(blank=True)
    date_begin = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)
    client = models.ForeignKey(Client, )
    personal = models.ForeignKey(Personal, )
    instructor = models.ForeignKey(Employee, blank=True, null=True)
    block_comment = models.CharField(max_length=150, blank=True, null=True)
    status = models.SmallIntegerField(default=2, blank=True, )
    printed = models.BooleanField(default=False)
    """
    status valid data:
    0 - disabled
    1 - active
    2 - prospect
    """

    @property
    def product(self):
        return self.personal

    @property
    def client_name(self):
        return self.client.full_name

    @property
    def name(self):
        return self.personal.name

    @property
    def get_extra_clients(self):
        clients = self.extra_clients.values('client')
        return Client.objects.filter(pk__in=clients)

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

    @property
    def is_online(self):
        return UseClientPersonal.objects.filter(client_personal=self,
                                                end__isnull=True).count()

    @property
    def rest_prolongation(self):
        prolongation = ProlongationPersonal.objects\
            .filter(personal=self, is_extra=False, is_paid=False)\
            .aggregate(sum=Sum('days'))
        if prolongation['sum']:
            return self.personal.period_prolongation - prolongation['sum']
        return self.personal.period_prolongation

    @property
    def positions(self):
        return self.personal.positions_pks

    @property
    def all_first_client_cc(self):
        if not self.client.active_cc_first:
            return False
        for e_client in self.extra_clients.all():
            if not e_client.client.active_cc_first:
                return False
        return True

    def activate(self, date_begin=None):
        self.date_begin = date_begin if date_begin else date.today()
        self.date_end = date_end(self.date_begin, self.personal)
        self.status = 1
        self.save()

    def deactivate(self, ):
        self.status = 0
        self.save()

    def save(self, *args, **kwargs):
        if self.pk:
            old_date_begin = ClientPersonal.objects.get(pk=self.pk).date_begin
            if old_date_begin:
                delta_begin = self.date_begin - old_date_begin
                if delta_begin:
                    self.date_end = date_end(self.date_begin, self.personal)
        super(ClientPersonal, self).save(*args, **kwargs)


class PersonalClients(models.Model):

    """
    External clients for the ClientPersonal.
    """
    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, related_name='extra_personals')
    personal = models.ForeignKey(ClientPersonal, related_name='extra_clients')

    class Meta:
        unique_together = ('client', 'personal')


class ProlongationPersonal(Prolongation, WritePayment, models.Model):

    """
    Prolongation for the Client Personal.
    """
    paid_text = 'paid prolongation'
    payment_goods = 'personal'

    date = models.DateTimeField()
    personal = models.ForeignKey(ClientPersonal, related_name='prolongation')
    days = models.SmallIntegerField()
    amount = models.DecimalField(max_digits=15, decimal_places=2,)
    is_paid = models.BooleanField(default=False)
    is_extra = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)

    @property
    def parent(self):
        return self.personal

    def save(self, *args, **kwargs):
        payment_type = kwargs.pop('payment_type', 1)
        self.add_payment(payment_type)
        if not self.pk:
            self.parent_upd(self,)
        super(ProlongationPersonal, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.parent_upd(self, is_delete=True)
        super(ProlongationPersonal, self).delete(*args, **kwargs)


class ClientTiming(models.Model):

    """
    The clients timings,
    history and status.

    Date start - the date for the start period of activation.
    Date begin - is start of using the card.

    """
    date = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField(blank=True)
    date_begin = models.DateField(blank=True)
    date_end = models.DateField(blank=True)
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
    def client_name(self):
        return self.client.full_name

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


class UseClientClubCard(models.Model):

    """
    Log information about use the Client Club Card.
    """
    date = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    client_club_card = models.ForeignKey(ClientClubCard, related_name='visits')

    class Meta:
        ordering = ['date']

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = datetime.now()
        if not self.pk:
            is_first = UseClientClubCard.objects\
                .filter(client_club_card=self.client_club_card)\
                .count()
            if is_first == 0 and self.client_club_card.status == 2:
                self.client_club_card.activate()
            if self.client_club_card.is_frozen:
                self.client_club_card.escape_frozen()
        if self.end and self.client_club_card.rest_visits < 1:
            # set status not activate
            self.client_club_card.deactivate()
        super(UseClientClubCard, self).save(*args, **kwargs)


class ClubCardTrains(models.Model):

    """
    The list of trainings of the visit by club card.
    """
    visit = models.ForeignKey(UseClientClubCard)
    training = models.ForeignKey(Training)

    def name(self):
        return self.training.name


class UseClientAquaAerobics(models.Model):

    """
    Log information about use the Client AquaAerobics.
    """
    date = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(blank=True, null=True)
    client_aqua_aerobics = models.ForeignKey(ClientAquaAerobics)

    def save(self, *args, **kwargs):
        if not self.pk:
            is_first = UseClientAquaAerobics.objects.filter(
                client_aqua_aerobics=self.client_aqua_aerobics).count()
            if is_first == 0:
                aqua = self.client_aqua_aerobics
                aqua.date_begin = date.today()
                aqua.date_end = date_end(date.today(), aqua.aqua_aerobics)
                aqua.save()
            if self.client_aqua_aerobics.is_frozen:
                self.client_aqua_aerobics.escape_frozen()
        super(UseClientAquaAerobics, self).save(*args, **kwargs)


class UseClientTicket(models.Model):

    """
    Log information about use the Client Ticket.
    """
    date = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(blank=True, null=True)
    client_ticket = models.ForeignKey(ClientTicket)

    def save(self, *args, **kwargs):
        if not self.pk:
            is_first = UseClientTicket.objects.filter(
                client_ticket=self.client_ticket).count()
            if is_first == 0:
                ticket = self.client_ticket
                ticket.date_begin = date.today()
                ticket.date_end = date_end(date.today(), ticket.ticket)
                ticket.save()
            if self.client_ticket.is_frozen:
                self.client_ticket.escape_frozen()
        super(UseClientTicket, self).save(*args, **kwargs)


class UseClientPersonal(models.Model):

    """
    Log information about use the Client Personal.
    """
    date = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    client_personal = models.ForeignKey(
        ClientPersonal, related_name='visits')
    instructor = models.ForeignKey(
        Employee, blank=True, null=True, related_name='personals')
    club_card_visit = models.ForeignKey(UseClientClubCard,
                                        blank=True, null=True)

    class Meta:
        ordering = ['date']

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = datetime.now()
        if not self.pk:
            is_first = UseClientPersonal.objects\
                .filter(client_personal=self.client_personal)\
                .count()
            if is_first == 0 and self.client_personal.status == 2:
                self.client_personal.activate()
            # Auto create visit for personal with club card
            if self.client_personal.personal.club_card_only:
                client = self.client_personal.client
                cc = client.active_cc_first
                ucc = UseClientClubCard.objects.create(
                    client_club_card=cc
                )
                self.club_card_visit = ucc
                train = Training.objects.filter(for_personals=True).first()
                ClubCardTrains.objects.create(visit=ucc, training=train)
        if self.end and self.client_personal.personal.club_card_only:
            ucc = self.club_card_visit
            ucc.end = self.end
            ucc.save()
            print(ucc)

        if self.end and self.client_personal.rest_visits < 1:
            # set status not activate
            self.client_personal.deactivate()
        super(UseClientPersonal, self).save(*args, **kwargs)


class UseClientTiming(models.Model):

    """
    Log information about use the Client Timing.
    """
    date = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(blank=True, null=True)
    client_timing = models.ForeignKey(ClientTiming)
    minutes = models.IntegerField(default=1, blank=True)


class ExtClientClubCard(models.Model):

    """
    Extended clients for the Client Club Card
    where clients_count > 1.
    """
    client_club_card = models.ForeignKey(ClientClubCard)
    client = models.ForeignKey(Client, )


class ClientOnline(models.Model):

    """
    Clients who has not end date in the use tables.
    """
    client = models.ForeignKey(Client, )
    date = models.DateTimeField(auto_now_add=True)
    product = models.CharField(max_length=50)
    is_full_time = models.BooleanField(default=False)

    class Meta:
        db_table = 'v_client_online'
        managed = False

    @property
    def client_data(self):
        return self.client


class OwnersClubCard(WritePayment, models.Model):

    """
    Owners list for the Client Club Card.
    """
    paid_text = 'paid owner'
    payment_goods = 'club_card'

    date = models.DateTimeField(auto_now_add=True, blank=True)
    club_card = models.ForeignKey(ClientClubCard, related_name='owners')
    client = models.ForeignKey(Client, related_name='+')


class OwnersClientPersonal(WritePayment, models.Model):

    """
    Owners list for the Client Personal.
    """
    paid_text = 'paid owner'
    payment_goods = 'personal'

    date = models.DateTimeField(auto_now_add=True, blank=True)
    personal = models.ForeignKey(ClientPersonal, related_name='owners')
    client = models.ForeignKey(Client, related_name='+')


def date_end(date_begin, obj):
    """
    Return date end for the obj
    """
    # the first day used
    if isinstance(date_begin, basestring):
        date_begin = datetime.strptime(date_begin, '%Y-%m-%d')
    if obj.period.is_month:
        months = obj.period.value
        date_to = date_begin + relativedelta(months=months)
    else:
        days = obj.period.value
        date_to = date_begin + timedelta(days=days)
    return date_to - timedelta(days=1)
