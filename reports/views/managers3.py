# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from django.utils.translation import ugettext as _

from reports import styles
from clients.models import (
    ProlongationClubCard, UseClientClubCard, ClubCardTrains, ClientClubCard,
    FreezeClubCard, UseClientPersonal, ProlongationPersonal, ClientPersonal)
from finance.models import Payment
from products.models import Training
from .base import ReportTemplate, Report


class ExtrProlongation(ReportTemplate):
    file_name = 'prolongation_cards_for_the_period'
    sheet_name = 'report'
    tpl_path = 'xls_tpl/prolongation.xls'
    tpl_start_row = 4

    table_headers = [
        (_('client'), 8000),
        (_('club card period'), 6000),
        (_('tariff'), 3000),
        (_('paid date'), 4000),
        (_('paid'), 4000),
        (_('p_days'), 3000),
        (_('p_days'), 3000),
        (_('note'), 8000),
    ]

    def get_title(self, **kwargs):
        msg = _('prolongation card for period.')
        msg += _(' created at: {date}.')
        date = datetime.now().strftime('%d.%m.%Y %H:%M')
        return msg.format(date=date)

    def write_title(self):
        super(ExtrProlongation, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        ln_head = len(self.table_headers) - 1
        self.ws.write_merge(1, 1, 0, ln_head, msg, styles.styleh)

    @staticmethod
    def _data_line(product):
        line = []
        ext_prolongation = product.ext_prolongation()
        if not ext_prolongation:
            return line
        line.append(product.client.full_name)
        period_data = {
            'bdate': product.date_begin.strftime('%d.%m.%Y'),
            'edate': product.date_end.strftime('%d.%m.%Y')
        }
        period = '{bdate}-{edate}'.format(**period_data)
        line.append(period)
        line.append(product.short_name)
        line.append(ext_prolongation)
        return line

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        club_cards = ProlongationClubCard.objects.filter(
            date__range=(fdate, tdate)).values('client_club_card')
        data = ClientClubCard.objects.filter(pk__in=club_cards)
        for row in data.order_by('date_end'):
            line = self._data_line(row)
            if not line:
                continue
            rows.append(line)
        personals = ProlongationPersonal.objects.filter(
            date__range=(fdate, tdate)).values('personal')
        data = ClientPersonal.objects.filter(pk__in=personals)
        for row in data.order_by('date_end'):
            line = self._data_line(row)
            if not line:
                continue
            rows.append(line)
        return rows

    def write_data(self):
        for row in self.get_data():
            row_step = len(row[3]) - 1
            for i, cell in enumerate(row[:3]):
                style = self.table_styles.get(i, styles.style_c)
                bottom_row = self.row_num + row_step
                self.ws.write_merge(
                    self.row_num, bottom_row, i, i,
                    cell, style)
                for si, sub_row in enumerate(row[3]):
                    for y, sub_cell in enumerate(sub_row):
                        rnum = self.row_num + si
                        cnum = y + 3
                        self.ws.write(rnum, cnum, sub_cell, style)
            self.row_num += (1 + row_step)

    def write_bottom(self):
        pass


class VisitsPeriod(Report):
    file_name = 'club_card_visits'
    sheet_name = 'report'

    default_headers = [
        (_('date'), 4000),
    ]
    table_headers = [(_('date'), 4000), ]

    def initial(self, request, *args, **kwargs):
        super(VisitsPeriod, self).initial(request, *args, **kwargs)
        qs = Training.objects.filter(is_active=True)
        headers = []
        for t in qs.values('order_num').distinct().order_by('order_num'):
            order_num = t.get('order_num')
            tr = qs.filter(order_num=order_num)
            if tr.count() == 1:
                name = tr[0].name
            else:
                name = _('group #: %s') % order_num
            headers.append((name, 6000))
        self.table_headers = self.default_headers + headers
        self.groups = qs.values_list(
            'order_num', flat=True).distinct().order_by('order_num')

    def get_title(self, **kwargs):
        return _("Attendance on club cards for the period").capitalize()

    def write_title(self):
        super(VisitsPeriod, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        self.ws.write_merge(1, 1, 0, 3, msg, styles.styleh)

    def get_data(self):
        rows = []
        self.groups_cnt = [0] * len(self.groups)
        days = (self.get_tdate() - self.get_fdate()).days + 1
        for d in (self.get_fdate() + timedelta(n) for n in range(days)):
            line = []
            df = d.replace(hour=0, minute=0, second=0)
            dt = d.replace(hour=23, minute=59, second=59)
            line.append(d.strftime('%d.%m.%Y'))
            d_visits = UseClientClubCard.objects.filter(date__range=(df, dt))
            workout = ClubCardTrains.objects.filter(visit__in=d_visits)
            for ind, g in enumerate(self.groups):
                cnt = workout.filter(training__order_num=g).count()
                if ind == 0:
                    # Personals visits add to first groups
                    p_visits_cnt = UseClientPersonal.objects.filter(
                        date__range=(df, dt),
                        client_personal__personal__club_card_only=False
                        ).count()
                    cnt += p_visits_cnt
                self.groups_cnt[ind] += cnt
                line.append(cnt)
            rows.append(line)
        line = [_("total")] + self.groups_cnt
        rows.append(line)
        return rows

    def write_bottom(self):
        total = sum(self.groups_cnt)
        self.ws.write(self.row_num, 0, _('total for period'))
        self.ws.write(self.row_num, 1, total, styles.styleh)


class OtherPayments(Report):
    """docstring for OtherPayments"""
    file_name = 'club_card_otherpayments'
    sheet_name = 'report'

    table_headers = [
        (_('client'), 8000),
        (_('paid date'), 3000),
        (_('co number'), 4000),
        (_('club card num'), 4000),
        (_('tariff'), 6000),
        (_('total paid'), 4000),
        (_('other paid'), 4000),
        (_('seller'), 6000),
        (_('document for other paid'), 6000),
    ]

    table_styles = {
        1: styles.styled,
    }

    def get_title(self, **kwargs):
        return _("other paid report").capitalize()

    def write_title(self):
        super(OtherPayments, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        ln_head = len(self.table_headers) - 1
        self.ws.write_merge(1, 1, 0, ln_head, msg, styles.styleh)

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        end_date = self.get_tdate() + timedelta(1)
        qs = Payment.objects.filter(
            date__range=(fdate, end_date)
        ).filter(payment_type=0)
        data = qs.exclude(club_card__isnull=True)
        data |= qs.exclude(personal__isnull=True)
        for row in data:
            product = row.first_goods
            if row.extra_uid:
                continue
            line = []
            line.append(row.client.full_name)
            line.append(row.date)
            line.append(row.client.uid)
            line.append(row.client.card)
            line.append(product.short_name)
            line.append(product.price())
            line.append(row.amount)
            employee = product.employee.full_name if product.employee else ''
            line.append(employee)
            line.append(row.extra_text)
            rows.append(line)
        return rows

    def write_bottom(self):
        pass


class Freeze(ReportTemplate):
    file_name = 'freeze_cards_for_the_period'
    sheet_name = 'report'
    tpl_path = 'xls_tpl/freeze.xls'
    tpl_start_row = 4

    table_headers = [
        (_('client'), 8000),
        (_('club card period'), 6000),
        (_('tariff'), 3000),
        (_('freeze days'), 2000),
        (_('freeze times'), 2000),
        (_('from date'), 3000),
        (_('to date'), 3000),
        (_('use free'), 2000),
        (_('rest free'), 2000),
        (_('paid'), 3000),
        (_('amount'), 3000),
        (_('use day'), 2000),
        (_('from date'), 3000),
        (_('to date'), 3000),
        (_('use day'), 2000),
        (_('from date'), 3000),
        (_('to date'), 3000),
        (_('note'), 8000),
    ]

    def get_title(self, **kwargs):
        msg = _('freeze card for period.')
        msg += _(' created at: {date}.')
        date = datetime.now().strftime('%d.%m.%Y %H:%M')
        return msg.format(date=date)

    def write_title(self):
        super(Freeze, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        ln_head = len(self.table_headers) - 1
        self.ws.write_merge(1, 1, 0, ln_head, msg, styles.styleh)

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        club_cards = FreezeClubCard.objects.filter(
            date__range=(fdate, tdate)).values('client_club_card')
        data = ClientClubCard.objects.filter(pk__in=club_cards)
        for row in data.order_by('date_end'):
            line = []
            card = row
            freeze_stat = card.freeze_stat()
            if not freeze_stat:
                continue
            line.append(card.client.full_name)
            period_data = {
                'bdate': card.date_begin.strftime('%d.%m.%Y'),
                'edate': card.date_end.strftime('%d.%m.%Y')
            }
            period = '{bdate}-{edate}'.format(**period_data)
            line.append(period)
            line.append(card.short_name)
            line.append(card.club_card.period_freeze)
            line.append(card.club_card.freeze_times)
            line.append(freeze_stat)
            rows.append(line)
        return rows

    def write_data(self):
        for row in self.get_data():
            row_step = len(row[5]) - 1
            for i, cell in enumerate(row[:5]):
                style = self.table_styles.get(i, styles.style_c)
                bottom_row = self.row_num + row_step
                self.ws.write_merge(
                    self.row_num, bottom_row, i, i,
                    cell, style)
                for si, sub_row in enumerate(row[5]):
                    for y, sub_cell in enumerate(sub_row):
                        rnum = self.row_num + si
                        cnum = y + 5
                        self.ws.write(rnum, cnum, sub_cell, style)
            self.row_num += (1 + row_step)

    def write_bottom(self):
        pass
