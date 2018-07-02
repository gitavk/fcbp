# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import timedelta, datetime

from django.utils.translation import ugettext as _

from reports import styles
from finance.models import Payment
from clients.models import ClientClubCard
from products.models import Period, ClubCard, Discount
from .base import ReportTemplate, Report


class TotalClubCard(ReportTemplate):

    file_name = 'total_club_cards'
    sheet_name = 'total_club_cards'
    tpl_path = 'xls_tpl/total_cards.xls'
    tpl_start_row = 3

    table_headers = [
        (_('total'), 4000),
        (_('club card'), 10000), ]

    table_styles = {
        1: styles.style_c,
        3: styles.style_c,
        5: styles.style_c,
    }

    def initial(self, request, *args, **kwargs):
        super(TotalClubCard, self).initial(request, *args, **kwargs)
        self.total = 0
        self.total_limit = 0
        self.total_full = 0
        self.periods = {}

    def get_title(self, **kwargs):
        return _('total club cards')

    def write_title(self):
        super(TotalClubCard, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        self.ws.write_merge(1, 1, 0, 5, msg, styles.styleh)

    def club_card_list(self):
        cards = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        payments = Payment.objects.filter(
            date__range=(fdate, tdate)
        ).exclude(club_card__isnull=True)
        for p in payments:
            if p.club_card.first_payment == p:
                cards.append(p.club_card.pk)
        return cards

    def get_data(self):
        rows = []
        cards = self.club_card_list()
        data = ClientClubCard.objects.filter(pk__in=cards)
        data = data.order_by('club_card__short_name')
        data = data.values_list('club_card__pk', flat=True).distinct()
        for row in range(0, len(data)/3 + 1):
            line = []
            for cc in data[row * 3: (row + 1) * 3]:
                club_card = ClubCard.objects.get(pk=cc)
                line.append(club_card.short_name)
                cnt = ClientClubCard.objects.filter(
                    pk__in=cards, club_card=club_card).count()
                line.append(cnt)
                self.total += cnt
                if club_card.is_full_time:
                    self.total_full += cnt
                if club_card.max_visit < 99999:
                    self.total_limit += cnt
                if club_card.period.pk not in self.periods:
                    self.periods[club_card.period.pk] = cnt
                else:
                    self.periods[club_card.period.pk] += cnt
            rows.append(line)
        return rows

    def write_heads(self):
        pass

    def write_bottom(self):
        self.ws.write(self.row_num, 0, _('total'))
        self.ws.write(self.row_num, 1, self.total, styles.styleh)
        self.row_num += 1
        self.ws.write(self.row_num, 0, _('including:'))
        self.row_num += 1
        self.ws.write(self.row_num, 0, _('limited'), styles.styleth)
        self.ws.write(self.row_num, 1, self.total_limit, styles.styleth)
        self.ws.write(self.row_num, 3, _('UBV'), styles.style)
        ubv_cnt = self.total - self.total_full
        self.ws.write(self.row_num, 4, ubv_cnt, styles.style_c)
        self.row_num += 1
        periods = Period.objects.filter(
            pk__in=self.periods).order_by('is_month', 'value')
        if periods:
            period = periods[0]
            self.ws.write(self.row_num, 0, period.name, styles.styleth)
            self.ws.write(
                self.row_num, 1, self.periods[period.pk], styles.styleth)
        self.ws.write(self.row_num, 3, _('P'), styles.style)
        self.ws.write(self.row_num, 4, self.total_full, styles.style_c)
        for period in periods[1:]:
            self.row_num += 1
            self.ws.write(self.row_num, 0, period.name, styles.styleth)
            self.ws.write(
                self.row_num, 1, self.periods[period.pk], styles.styleth)


class TotalActiveClubCard(TotalClubCard):

    file_name = 'total_active_club_cards'
    sheet_name = 'total_active_club_cards'
    tpl_path = 'xls_tpl/total_active_cards.xls'

    def get_title(self, **kwargs):
        return _('total active club cards')

    def write_title(self):
        super(TotalClubCard, self).write_title()
        date = datetime.now().strftime('%d.%m.%Y')
        self.ws.write(1, 1, date, styles.styleh)

    def club_card_list(self):
        cards = ClientClubCard.objects.filter(status=1)
        return cards.values_list('pk', flat=True)


class RepDiscount(Report):

    file_name = 'club_cards_discounts'
    sheet_name = 'club_cards_discounts'

    table_headers = [
        (_('client'), 10000),
        (_('# uid'), 6000),
        (_('tariff'), 6000),
        (_('paid date'), 6000),
        (_('discount type'), 4000),
        (_('discount'), 6000),
    ]

    table_styles = {
        1: styles.style_c,
        2: styles.style_c,
        3: styles.styled,
        4: styles.style_c,
        5: styles.style_c,
    }

    def initial(self, request, *args, **kwargs):
        super(Discount, self).initial(request, *args, **kwargs)
        self.total = {}

    def get_title(self, **kwargs):
        return _('club cards discounts')

    def write_title(self):
        super(Discount, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        heads_ln = len(self.table_headers)
        self.ws.write_merge(1, 1, 0, heads_ln, msg, styles.styleh)

    def get_data(self):
        rows = []
        cards = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        pqs = Payment.objects.filter(date__range=(fdate, tdate)
            ).order_by('date')
        payments = pqs.exclude(club_card__isnull=True)
        payments |= pqs.exclude(personal__isnull=True)
        for p in payments:
            product = p.first_goods
            discount = product.discount_amount or product.bonus_amount
            if product.first_payment != p or not discount:
                continue
            line = []
            line.append(product.client.full_name)
            line.append(product.client.uid)
            line.append(product.product.short_name)
            line.append(product.first_payment.date)
            line.append(product.discount_short)
            if product.discount_short not in self.total:
                self.total[product.discount_short] = 1
            else:
                self.total[product.discount_short] += 1
            discount_value = product.discount_value
            if discount_value <= 100:
                discount_value = ('{value} %').format(value=discount_value)
            line.append(discount_value)
            rows.append(line)
        return rows

    def write_bottom(self):
        self.ws.write(self.row_num, 0, _('total'))
        for row in sorted(self.total.items(), key=lambda t: t[0]):
            self.ws.write(self.row_num, 1, row[0], styles.style_c)
            self.ws.write(self.row_num, 2, row[1], styles.style_c)
            self.row_num += 1


class ClubCardDisabled(Report):

    file_name = 'club_cards_disabled'
    sheet_name = 'club_cards_disabled'

    table_headers = [
        (_('create date'), 4000),
        (_('client'), 8000),
        (_('# uid'), 4000),
        (_('club card period'), 6000),
        (_('tariff'), 4000),
        (_('reason for blocking'), 6000),
    ]

    table_styles = {
        0: styles.styled,
        2: styles.style_c,
        3: styles.style_c,
    }

    def initial(self, request, *args, **kwargs):
        super(ClubCardDisabled, self).initial(request, *args, **kwargs)
        self.total = 0

    def get_title(self, **kwargs):
        return _('blocked cards during the period')

    def write_title(self):
        super(ClubCardDisabled, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        heads_ln = len(self.table_headers)
        self.ws.write_merge(1, 1, 0, heads_ln, msg, styles.styleh)

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        data = ClientClubCard.objects.filter(
            date_end__range=(fdate, tdate), status=0,
            block_comment__isnull=False
        ).exclude(block_comment='').order_by('date')
        for row in data:
            line = []
            line.append(row.date)
            line.append(row.client.full_name)
            line.append(row.client.uid)
            period_data = {
                'bdate': row.date_begin.strftime('%d.%m.%Y'),
                'edate': row.date_end.strftime('%d.%m.%Y')
            }
            period = '{bdate}-{edate}'.format(**period_data)
            line.append(period)
            line.append(row.club_card.short_name)
            line.append(row.block_comment)
            rows.append(line)
        self.total = len(rows)
        return rows

    def write_bottom(self):
        self.ws.write(self.row_num, 0, _('total'), styles.styleh)
        self.ws.write(self.row_num, 1, _('all locked cards'), styles.styleh)
        self.ws.write(self.row_num, 2, self.total, styles.styleh)


class ClubCardProspect(Report):

    file_name = 'club_cards_prospect'
    sheet_name = 'club_cards_prospect'

    table_headers = [
        (_('paid date'), 4000),
        (_('client'), 8000),
        (_('# uid'), 4000),
        (_('club card num'), 4000),
        (_('tariff'), 4000),
    ]

    table_styles = {
        0: styles.styled,
        1: styles.style_c,
        2: styles.style_c,
        3: styles.style_c,
    }

    def initial(self, request, *args, **kwargs):
        super(ClubCardProspect, self).initial(request, *args, **kwargs)
        self.total = 0

    def get_title(self, **kwargs):
        msg = _('not activated the card to date')
        msg += _(' created at: {date}.')
        tdate = self.get_fdate().strftime('%d.%m.%Y %H:%M')
        return msg.format(date=tdate)

    def get_fdate(self):
        return datetime.now()

    def get_data(self):
        rows = []
        data = ClientClubCard.objects.filter(
            date_begin__isnull=True, status__gt=0).order_by('-date')
        for row in data:
            line = []
            line.append(row.first_payment.date)
            line.append(row.client.full_name)
            line.append(row.client.uid)
            line.append(row.client.card)
            line.append(row.club_card.short_name)
            rows.append(line)
        self.total = len(rows)
        return rows

    def write_bottom(self):
        self.ws.write(self.row_num, 0, _('total'), styles.styleh)
        self.ws.write(self.row_num, 1, _('all inactive cards'), styles.styleh)
        self.ws.write(self.row_num, 2, self.total, styles.styleh)


class BestLoyalty(Report):

    file_name = 'club_cards_best_loyalty'
    sheet_name = 'club_cards_best_loyalty'

    table_headers = [
        (_('client'), 8000),
        (_('# uid'), 4000),
        (_('previous tariff'), 4000),
        (_('new tariff'), 4000),
        (_('previous date end'), 4000),
        (_('new date end'), 4000),
        (_('previous discount'), 4000),
        (_('new discount'), 4000),
        (_('new paid date'), 4000),
    ]

    table_styles = {
        1: styles.style_c,
        2: styles.style_c,
        3: styles.style_c,
        6: styles.style_c,
        7: styles.style_c,
    }

    def initial(self, request, *args, **kwargs):
        super(BestLoyalty, self).initial(request, *args, **kwargs)
        self.total = 0
        self.discounts = defaultdict(int)
        self.red_font = styles.style_red_font
        self.red_font.borders = styles.borders
        self.red_font.alignment = styles.alignment_c

    def get_title(self, **kwargs):
        return _('sales at best loyalty')

    def write_title(self):
        super(BestLoyalty, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        heads_ln = len(self.table_headers)
        self.ws.write_merge(1, 1, 0, heads_ln, msg, styles.styleh)

    def get_data(self):
        rows = []
        bl_discounts = Discount.objects.filter(is_best_loyalty=True)
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        data = ClientClubCard.objects.filter(
            discount_type__in=bl_discounts, date__range=(fdate, tdate)
        ).order_by('date')
        for row in data:
            line = []
            previous_card = row.previous_card(exclude_single=True)
            line.append(row.client.full_name)
            line.append(row.client.uid)
            if previous_card:
                line.append(previous_card.club_card.short_name)
            else:
                line.append('')
            line.append(row.club_card.short_name)
            if previous_card:
                line.append(previous_card.date_end)
            else:
                line.append('')
            line.append(row.date_begin)
            if previous_card:
                pval = 0
                if previous_card.discount_value:
                    pval = int(previous_card.discount_value)
                line.append('{val}%'.format(val=pval))
            else:
                line.append('')
            val = int(row.discount_value) if row.discount_value else 0
            self.discounts[val] += 1
            line.append('{val}%'.format(val=val))
            if row.first_payment:
                line.append(row.first_payment.date)
            else:
                line.append('')
            rows.append(line)
        self.total = len(rows)
        return rows

    def write_data(self):
        for row in self.get_data():
            row_step = 0
            red = False
            prev_end = row[4]
            cur_begin = row[5]
            if prev_end and cur_begin:
                if (cur_begin - prev_end).days > 1:
                    red = True
            prev_discount = row[6]
            cur_discount = row[7]
            not_prev = not prev_discount or int(prev_discount[:-1]) == 0
            if not_prev and int(cur_discount[:-1]) > 5:
                red = True
            elif prev_discount and cur_discount:
                prev_discount = int(prev_discount[:-1])
                cur_discount = int(cur_discount[:-1])
                if prev_discount > 9 and cur_discount - prev_discount > 0:
                    red = True
                elif cur_discount - prev_discount > 1 and prev_discount != 0:
                    red = True
            for i, cell in enumerate(row):
                if red:
                    style = self.red_font
                else:
                    style = self.table_styles.get(i, styles.style)
                if cell and i in [4, 5, 8]:
                    cell = cell.strftime('%d.%m.%Y') if cell else ''
                self.ws.write(self.row_num, i, cell, style)
            self.row_num += (1 + row_step)

    def write_bottom(self):
        self.ws.write(self.row_num, 0, _('total'), styles.styleth)
        self.ws.write(self.row_num + 1, 0, self.total, styles.styleth)
        self.ws.write(self.row_num, 2, _('including:'), styles.styleth)
        for i, discount in enumerate(self.discounts):
            discount_h = '{val}%'.format(val=discount)
            col = 3 + i
            cnt = self.discounts.get(discount)
            self.ws.write(self.row_num, col, discount_h, styles.styleth)
            self.ws.write(self.row_num + 1, col, cnt, styles.styleth)


class PeriodSales(Report):

    file_name = 'report_administrator_on_the_sales_cards_for_the_day'
    sheet_name = 'report'

    table_headers = [
        (_('paid date'), 3000),
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
        0: styles.styled,
        1: styles.stylet,
        6: styles.stylef,
        9: styles.stylef,
    }

    def initial(self, request, *args, **kwargs):
        super(PeriodSales, self).initial(request, *args, **kwargs)
        payment_types = dict.fromkeys(Payment.payment_types.keys(), 0)
        self.total_payments = {
            'card': payment_types.copy(),
            'personal': payment_types.copy(),
        }

    def get_title(self, **kwargs):
        msg = _(
            'report on the sales cards for the period.')
        msg += _(' created at: {date}.')
        date = datetime.now().strftime('%d.%m.%Y %H:%M')
        return msg.format(date=date)

    def write_title(self):
        super(PeriodSales, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        heads_ln = len(self.table_headers)
        self.ws.write_merge(1, 1, 0, heads_ln, msg, styles.styleh)

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        end_date = self.get_tdate() + timedelta(1)
        qs = Payment.objects.filter(
            date__range=(fdate, end_date)
        ).exclude(payment_type=3)
        data = qs.exclude(club_card__isnull=True)
        data |= qs.exclude(personal__isnull=True)
        for row in data:
            line = []
            card = row.club_card or row.personal
            line.append(row.date)
            line.append(row.date.strftime('%H:%M'))
            line.append(row.client.full_name)
            line.append(row.client.uid)
            line.append(row.client.card)
            line.append(row.first_goods.short_name)
            if not row.extra_uid:
                line.append(card.price())
                line.append(card.discount_value)
                line.append(card.discount_short)
            else:
                line.append('')
                line.append('')
                line.append('')
            line.append(row.amount)
            ptype = Payment.payment_types.get(row.payment_type)
            line.append(ptype)
            if row.club_card:
                self.total_payments['card'][row.payment_type] += row.amount
            else:
                self.total_payments['personal'][row.payment_type] += row.amount
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

    def _bottom_details(self, details):
        self.ws.write(self.row_num, 4, sum(details.values()))
        self.row_num += 1
        for x in (1, 2, 0):
            self.ws.write(self.row_num, 2, Payment.payment_types[x])
            self.ws.write(self.row_num, 4, details[x])
            self.row_num += 1

    def write_bottom(self):
        self.ws.write(self.row_num, 2, _('all card sales'))
        self._bottom_details(self.total_payments.get('card', {}))
        self.row_num += 1
        self.ws.write(self.row_num, 2, _('all personal sales'))
        self._bottom_details(self.total_payments.get('personal', {}))
