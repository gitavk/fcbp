from datetime import date, timedelta
from django.db import models

from products.models import ClubCard, AquaAerobics, Ticket, Personal, Timing


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

    mobile = models.BigIntegerField(null=True, blank=True)
    gender = models.SmallIntegerField(default=0, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    passport = models.TextField(null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatar/", null=True, blank=True)

    @property
    def full_name(self,):
        return "%s %s %s" % (self.last_name, self.first_name, self.patronymic)

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return ""
    
    def save(self, *args, **kwargs):
        if not self.uid:
            mon = date.today() + timedelta(days=-date.today().weekday())
            week_clients = Client.objects.filter(date__gte=mon).count()
            year = (date.today().year - 2000) * 10000
            week = date.today().isocalendar()[1] * 100
            cnt = week_clients + 1
            self.uid = year + week + cnt
        super(Client, self).save(*args, **kwargs)


class ClientClubCard(models.Model):
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
