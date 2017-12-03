# -*- coding: utf-8 -*-
from datetime import timedelta, datetime, date
from collections import defaultdict

from django.db.models import Sum
from django.utils.translation import ugettext as _

from .base import Report
from reports import styles
from clients.models import ClientPersonal
from products.models import Personal


class ActivePersonal(Report):

    file_name = 'list_active_personal'
    sheet_name = 'report'
    tpl_start_row = 7

    table_headers = [
        (_('client'), 6000),
        (_('# uid'), 2000),
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
        (_('schedule payments'), 6000),
        (_('extra clients'), 6000),
        (_('coach'), 4000),
    ]

    table_styles = {
        6: styles.styled,
        7: styles.styled,
        9: styles.styled,
        13: styles.style_cw
    }

    def initial(self, request, *args, **kwargs):
        super(ActivePersonal, self).initial(request, *args, **kwargs)
        self.total_main_rows = 0
        self.products = defaultdict(int)
        self.row_heiht = 26*20
        try:
            personal_id = int(self.request.query_params.get('pc'))
            self.personal = Personal.objects.get(pk=personal_id)
        except:
            self.personal = 'all'

    def get_fdate(self):
        return datetime.now()

    def write_title(self):
        super(ActivePersonal, self).write_title()

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
                cc = row.client.active_cc_first
                cc_name = cc.short_name
                dbegin = cc.date_begin.strftime('%d.%m.%Y')
                dend = cc.date_end.strftime('%d.%m.%Y')
                cc_period = "{}-{}".format(dbegin, dend)
            # generate credits shedule
            schedule = []
            for p in row.schedule_payments():
                if p[0] <= self.get_fdate():
                    continue
                pdate = p[0].strftime('%d.%m.%Y')
                pamount = "{:,}".format(p[1]).replace(',', ' ')
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
                fname, uid, phone, tariff, 1, amount, date_begin, date_end,
                len(visits), last_visit, prolongation, cc_name, cc_period,
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
                    cc = row.curr_ec.active_cc_first
                    cc_name = cc.short_name
                    dbegin = cc.date_begin.strftime('%d.%m.%Y')
                    dend = cc.date_end.strftime('%d.%m.%Y')
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
