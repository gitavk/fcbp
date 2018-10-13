"""
Statistic of the client Personals.
"""
# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from collections import defaultdict

from django.db.models import Sum
from django.utils.translation import ugettext as _

from employees.models import Employee
from clients.models import ClientPersonal, UseClientPersonal
from products.models import Personal
from reports import styles
from .base import Report


class ActivePersonal(Report):

    file_name = 'list_active_personal'
    sheet_name = 'report'
    tpl_start_row = 7

    table_headers = [
        (_('client'), 6000),
        (_('# uid'), 2000),
        (_('card number'), 2000),
        (_('phone'), 4000),
        (_('tariff'), 6000),
        (_('attribute'), 2000),
        (_('amount'), 2000),
        (_('date begin'), 4000),
        (_('date end'), 4000),
        (_('used'), 2000),
        (_('last visit'), 3000),
        (_('prolongation'), 2000),
        (_('tariff club card'), 2000),
        (_('club card period'), 6000),
        (_('schedule s'), 6000),
        (_('extra clients'), 6000),
        (_('coach'), 4000),
    ]

    table_styles = {
        7: styles.styled,
        8: styles.styled,
        10: styles.styled,
        14: styles.style_cw
    }

    def initial(self, request, *args, **kwargs):
        super(ActivePersonal, self).initial(request, *args, **kwargs)
        self.total_main_rows = 0
        self.products = defaultdict(int)
        self.row_heiht = 26*20
        try:
            personal_id = int(self.request.query_params.get('pc'))
            self.personal = Personal.objects.get(pk=personal_id)
        except (ValueError, Personal.DoesNotExist):
            self.personal = 'all'

    def get_fdate(self):
        return datetime.now()

    def get_title(self, **kwargs):
        msg = _('list active club cards')
        msg += _(' created at: {date}.')
        tdate = self.get_fdate().strftime('%d.%m.%Y %H:%M')
        return msg.format(date=tdate)

    def get_data(self):
        rows = []
        data = ClientPersonal.objects.filter(status=1).order_by('date_end')
        if self.personal != 'all':
            data = data.filter(personal=self.personal)
        for row in data:
            fname = row.client.full_name
            uid = row.client.uid
            card = row.client.card
            phone = row.client.mobile or row.client.phone or ''
            tariff = row.personal.short_name
            amount = row.summ_amount
            date_begin = row.date_begin.strftime('%d.%m.%Y')
            date_end = row.date_end.strftime('%d.%m.%Y')
            # last visits info
            visits = row.visits.all()
            if visits:
                last_visit = visits.last().date.strftime('%d.%m.%Y')
            else:
                last_visit = ''
            prolongation = row.prolongation.aggregate(
                days=Sum('days')).get('days', '')
            # club card data if need for current personalcard
            cc_name = ''
            cc_period = ''
            if row.product.club_card_only and row.client.active_cc_first:
                club_card = row.client.active_cc_first
                cc_name = club_card.short_name
                dbegin = club_card.date_begin.strftime('%d.%m.%Y')
                dend = club_card.date_end.strftime('%d.%m.%Y')
                cc_period = "{}-{}".format(dbegin, dend)
            # generate credits shedule
            schedule = []
            for payment in row.schedule_payments():
                if payment[0] <= self.get_fdate():
                    continue
                pdate = payment[0].strftime('%d.%m.%Y')
                pamount = "{:,}".format(payment[1]).replace(',', ' ')
                schedule.append("%s - %s" % (pamount, pdate))
            schedule = "; \n".join(schedule)
            # extra clients info
            extra_clients = row.get_extra_clients
            main_ecs = ", ".join([ec.initials for ec in extra_clients])
            instructor = row.instructor.initials if row.instructor else ''
            # line for main client
            self.total_main_rows += 1
            self.products[tariff] += 1
            rows.append((
                fname, uid, card, phone, tariff, 1, amount,
                date_begin, date_end, len(visits), last_visit,
                prolongation, cc_name, cc_period,
                schedule, main_ecs, instructor
            ))
            # lines for extra xlients
            for curr_ec in extra_clients:
                fname = curr_ec.full_name
                uid = curr_ec.uid
                phone = curr_ec.mobile or curr_ec.phone or ''
                # club card data if need for current personalcard
                cc_name = ''
                cc_period = ''
                if row.product.club_card_only and curr_ec.active_cc_first:
                    club_card = row.curr_ec.active_cc_first
                    cc_name = club_card.short_name
                    dbegin = club_card.date_begin.strftime('%d.%m.%Y')
                    dend = club_card.date_end.strftime('%d.%m.%Y')
                    cc_period = "{}-{}".format(dbegin, dend)
                slave_ecs = [ec for ec in extra_clients if ec != curr_ec]
                slave_ecs += [row.client]
                slave_ecs = ",".join([ec.initials for ec in slave_ecs])
                self.products[tariff] += 1
                rows.append((
                    fname, uid, phone, tariff, 0, amount, date_begin, date_end,
                    len(visits), last_visit, prolongation, cc_name, cc_period,
                    schedule, slave_ecs, instructor
                ))
        return rows

    def write_heads(self):
        self.ws.write_merge(
            self.row_num, self.row_num, 3, 5, _('tariff'), styles.styleh)
        if self.personal == 'all':
            self.ws.write(self.row_num, 6, _('all'), styles.styleh)
        else:
            self.ws.write_merge(
                self.row_num, self.row_num, 6, 9,
                self.personal.name, styles.styleh)
        self.row_num += 2
        super(ActivePersonal, self).write_heads()

    def write_bottom(self):
        self.ws.write_merge(
            self.row_num, self.row_num, 0, 1, _('total cards'))
        self.ws.write(self.row_num, 2, self.total_main_rows, styles.styleh)
        for row_num, product in enumerate(self.products, self.row_num + 1):
            self.ws.write_merge(row_num, row_num, 0, 1, product)
            self.ws.write(
                row_num, 2, self.products.get(product), styles.styleh)


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

    def initial(self, request, *args, **kwargs):
        super(UsePersonals, self).initial(request, *args, **kwargs)
        self.products = defaultdict(int)
        try:
            personal_id = int(self.request.query_params.get('c'))
            self.instructor = Employee.objects.get(pk=personal_id)
        except (ValueError, Employee.DoesNotExist):
            self.instructor = 'all'

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
        fdate = self.get_fdate()
        tdate = self.get_tdate() + timedelta(1)
        tdate = tdate.replace(hour=0, minute=0, second=0)
        data = UseClientPersonal.objects.filter(
            date__range=(fdate, tdate)).order_by('date')
        if self.instructor != 'all':
            data = data.filter(instructor=self.instructor)
        for row in data:
            client = row.client_personal.client.full_name
            card = row.client_personal.client.card
            tariff = row.client_personal.product.short_name
            self.products[tariff] += 1
            instructor = row.instructor.initials if row.instructor else ''
            rows.append((
                row.date, row.date.strftime('%H:%M'), card,
                client, tariff, instructor
            ))
        return rows

    def write_heads(self):
        self.ws.write_merge(
            self.row_num, self.row_num, 0, 2, _('coach'), styles.styleh)
        if self.instructor == 'all':
            self.ws.write(self.row_num, 3, _('all'), styles.styleh)
        else:
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


class TotalPersonals(Report):

    file_name = 'total_personals'
    sheet_name = 'total_personals'
    tpl_start_row = 5

    table_headers = [
        (_('tariff'), 10000),
        (_('total'), 4000),
    ]

    def get_title(self, **kwargs):
        return _('total personals')

    def write_title(self):
        super(TotalPersonals, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        ln_head = len(self.table_headers) - 1
        self.ws.write_merge(1, 1, 0, ln_head, msg, styles.styleh)

    def personals_list(self):
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        personals = ClientPersonal.objects.filter(payment__date__range=(fdate, tdate))
        # generate filter to get only first payment
        filter_pk = []
        for personal in personals:
            if personal.first_payment.date.date() >= fdate:
                filter_pk.append(personal.pk)
        return personals.filter(pk__in=filter_pk)

    def get_data(self):
        rows = []
        personals = self.personals_list()
        data_pks = personals.values('personal__pk')
        data = Personal.objects.filter(
            pk__in=data_pks).order_by('max_visit', 'short_name')
        total = 0
        for row in data:
            line = []
            line.append(row.short_name)
            cnt = personals.filter(personal=row).count()
            line.append(cnt)
            total += cnt
            rows.append(line)
        rows.append((_('total'), total))
        return rows

    def write_bottom(self):
        pass
