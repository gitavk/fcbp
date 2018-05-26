# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import timedelta, datetime

from django.utils.translation import ugettext as _
from django.db.models import Sum

from .base import Report
from reports import styles
from clients.models import (
    ClientClubCard, UseClientClubCard, Client, UseClientPersonal)
from employees.models import Employee
from finance.models import Payment
from products.models import Training


class Sales(Report):

    file_name = 'report_administrator_on_the_sales_cards_for_the_day'
    sheet_name = 'report'

    table_headers = [
        (_('time'), 2000),
        (_('client'), 8000),
        (_('co number'), 4000),
        (_('card number'), 2000),
        (_('tariff'), 6000),
        (_('full price'), 4000),
        (_('discount'), 4000),
        (_('discount type'), 4000),
        (_('paid'), 4000),
        (_('paid type'), 4000),
        (_('schedule payments'), 8000),
        (_('seller'), 6000),
    ]

    table_styles = {
        0: styles.stylet,
        5: styles.stylef,
        8: styles.stylef,
    }

    def get_fdate(self):
        return datetime.now()

    def get_title(self, **kwargs):
        msg = _(
            'report administrator on the sales cards for the day.')
        msg += _(' created at: {date}.')
        date = self.get_fdate().strftime('%d.%m.%Y %H:%M')
        return msg.format(date=date)

    def get_data(self):
        self.total_payments = dict.fromkeys(Payment.payment_types.keys(), 0)
        rows = []
        fdate = self.get_fdate().date()
        end_date = fdate + timedelta(1)
        data = Payment.objects.filter(
            date__range=(fdate, end_date)
        ).exclude(club_card__isnull=True).exclude(payment_type=3)
        for row in data:
            line = []
            card = row.club_card
            line.append(row.date.strftime('%H:%M'))
            line.append(row.client.full_name)
            line.append(row.client.uid)
            line.append(row.client.card)
            line.append(row.goods_short_name())
            if not row.extra_uid:
                line.append(card.club_card.price)
                line.append(card.discount_value)
                line.append(card.discount_short)
            else:
                line.append('')
                line.append('')
                line.append('')
            line.append(row.amount)
            ptype = Payment.payment_types.get(row.payment_type)
            line.append(ptype)
            self.total_payments[row.payment_type] += row.amount
            schedule = []
            for p in card.schedule_payments():
                if p[0] <= row.date:
                    continue
                pdate = p[0].strftime('%d.%m.%Y')
                pamount = "{:,}".format(p[1]).replace(',', ' ')
                schedule.append("%s %s" % (pdate, pamount))
            line.append(", ".join(schedule))
            employee = card.employee.full_name if card.employee else ''
            line.append(employee)
            rows.append(line)
        return rows

    def write_bottom(self):
        self.ws.write(self.row_num, 5, _('annotation'))
        self.row_num += 1
        self.ws.write(self.row_num, 2, _('all card sales'))
        self.ws.write(self.row_num, 4, sum(self.total_payments.values()))
        self.row_num += 1
        for x in (1, 2, 0):
            self.ws.write(self.row_num, 2, Payment.payment_types[x])
            self.ws.write(self.row_num, 4, self.total_payments[x])
            self.row_num += 1
        self.row_num += 1
        self.ws.write(self.row_num, 2, _('Administrator'))


class Visits(Report):
    file_name = 'visiting_the_club_for_the_day'
    sheet_name = 'report'

    table_headers = [
        (_('card number'), 4000,),
        (_('client'), 8000),
        (_('time in'), 4000),
        (_('time out'), 4000),
        (_('tariff'), 5000),
        (_('occupation'), 6000, 3),
    ]

    def get_title(self, **kwargs):
        msg = _(
            'Visiting the club for the day. data: {date}')
        date = self.get_fdate().strftime('%d.%m.%Y')
        return msg.format(date=date)

    def get_data(self):
        self.total_trains = []
        rows = []
        fdate = self.get_fdate()
        end_date = fdate + timedelta(1)
        data = UseClientClubCard.objects.filter(date__range=(fdate, end_date))
        for row in data:
            line = []
            line.append(row.client_club_card.client.card)
            line.append(row.client_club_card.client.full_name)
            line.append(row.date.strftime('%H:%M'))
            if row.end:
                line.append(row.end.strftime('%H:%M'))
            else:
                line.append('')
            line.append(row.client_club_card.short_name)
            trains = row.clubcardtrains_set.all()
            for train in trains:
                line.append(train.name())
                self.total_trains.append(train.name())
            empty_trains = [''] * (4 - len(trains))
            line.extend(empty_trains)
            rows.append(line)
        return rows

    def order_trains(self):
        set_trains = set(self.total_trains)
        trains = Training.objects.filter(name__in=set_trains)
        return trains.order_by('order_num', 'name')

    def write_bottom(self):
        self.ws.write(self.row_num, 1, _('total of day'))
        self.ws.write(self.row_num, 2, len(self.total_trains), styles.style)
        self.row_num += 1
        self.ws.write(self.row_num, 1, _('including:'))
        self.row_num += 1
        for train in self.order_trains().values_list('name', flat=True):
            cnt = self.total_trains.count(train)
            self.ws.write(self.row_num, 1, train)
            self.ws.write(self.row_num, 2, cnt, styles.style)
            self.row_num += 1
        self.row_num += 1
        self.ws.write(self.row_num, 1, _('Administrator'))


class Birthdays(Report):
    file_name = 'birthdays_for_the_period'
    sheet_name = 'report'

    table_headers = [
        (_('birthday'), 4000,),
        (_('client'), 8000),
        (_('mobile'), 6000),
        (_('note'), 6000),
    ]
    table_styles = {
        0: styles.styled
    }

    def get_title(self, **kwargs):
        msg = _(
            'birthdays for the period. from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        return msg.format(fdate=fdate, tdate=tdate)

    def date_range(self):
        fdate = self.get_fdate()
        tdate = self.get_tdate()
        if fdate.month <= tdate.month:
            fdate = fdate.replace(year=2000)
            tdate = tdate.replace(year=2000)
        else:
            fdate = fdate.replace(year=2000)
            tdate = tdate.replace(year=2001)
        numdays = (tdate - fdate).days
        return [fdate + timedelta(x) for x in xrange(numdays + 1)]

    @staticmethod
    def format_mobile(value):
        if not value:
            return ''
        value = str(value)
        return '+7 (%s) %s - %s' % (value[0:3], value[3:6], value[6:10])

    def get_data(self):
        rows = []
        for day in self.date_range():
            for born in Client.objects.filter(
                    born__day=day.day, born__month=day.month):
                line = []
                line.append(born.born)
                line.append(born.full_name)
                line.append(Birthdays.format_mobile(born.mobile))
                line.append(born.note)
                rows.append(line)
        return rows

    def write_bottom(self):
        pass


class UsePersonals(Report):
    """Personals visits by dates with employee info"""

    file_name = 'trainers_personal'
    sheet_name = 'report'
    tpl_start_row = 7

    table_headers = [
        (_('date'), 3000),
        (_('time'), 3000),
        (_('card number'), 2000),
        (_('client'), 6000),
        (_('tariff'), 6000),
        (_('coach'), 5000),
    ]

    table_styles = {
        0: styles.styled,
        1: styles.stylet,
    }

    def get_fdate(self):
        return datetime.today().replace(hour=0, minute=0)

    def get_tdate(self):
        return self.get_fdate()

    def initial(self, request, *args, **kwargs):
        super(UsePersonals, self).initial(request, *args, **kwargs)
        self.products = defaultdict(int)
        fdate = self.get_fdate()
        tdate = self.get_tdate() + timedelta(1)
        tdate = tdate.replace(hour=0, minute=0, second=0)
        self.data = UseClientPersonal.objects.filter(
            date__range=(fdate, tdate))

    def get_title(self, **kwargs):
        msg = _('use personals by trainers')
        msg += _(' created at: {date}.')
        date = datetime.now().strftime('%d.%m.%Y %H:%M')
        return msg.format(date=date)

    def write_title(self):
        super(UsePersonals, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        ln_head = len(self.table_headers) - 1
        self.ws.write_merge(1, 1, 0, ln_head, msg, styles.styleh)

    def get_data(self):
        rows = []
        data = self.data.filter(instructor=self.instructor).order_by('date')
        for row in data:
            client = row.client_personal.client.full_name
            tariff = row.client_personal.product.short_name
            self.products[tariff] += 1
            instructor = row.instructor.initials if row.instructor else ''
            rows.append((
                row.date, row.date.strftime('%H:%M'), row.client_personal.pk,
                client, tariff, instructor
            ))
        return rows

    def write_heads(self):
        self.ws.write_merge(
            self.row_num, self.row_num, 0, 2, _('coach'), styles.styleh)
        self.ws.write_merge(
            self.row_num, self.row_num, 3, 6,
            self.instructor.initials, styles.styleh)
        self.row_num += 2
        super(UsePersonals, self).write_heads()

    def write_bottom(self):
        self.ws.write_merge(
            self.row_num, self.row_num, 0, 3,
            _('total use personals by period'))
        self.ws.write(self.row_num, 4,
                      sum(self.products.values()), styles.styleh)
        self.row_num += 1
        self.ws.write_merge(
            self.row_num, self.row_num, 0, 3, _('total by tariff'))

        for row_num, product in enumerate(self.products, self.row_num + 1):
            self.ws.write_merge(row_num, row_num, 0, 1, product)
            self.ws.write(
                row_num, 2, self.products.get(product), styles.styleh)
        self.row_num = row_num + 3
        # reset products
        self.products = defaultdict(int)

    def write_sheet(self):
        self.row_num = 2
        ipks = self.data.values_list('instructor', flat=True)
        for emp in Employee.objects.filter(pk__in=ipks).order_by('last_name'):
            self.instructor = emp
            self.write_heads()
            self.row_num += 1
            self.write_data()
            self.row_num += 1
            self.write_bottom()
