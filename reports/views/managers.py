# -*- coding: utf-8 -*-
from datetime import timedelta, datetime, date

from django.utils.translation import ugettext as _
from django.db.models import Sum

from .base import ReportTemplate, Report
from reports import styles
from clients.models import (
    ClientClubCard, UseClientClubCard, Client, ClubCardTrains,
    FitnessClubCard, PersonalClubCard, ClientPersonal)
from products.models import ClubCard
from finance.models import Payment, Credit


class ActiveClubCard(ReportTemplate):

    file_name = 'list_active_club_cards'
    sheet_name = 'report'
    tpl_path = 'xls_tpl/active_clubcard.xls'
    tpl_start_row = 7

    table_headers = [
        (_('client'), 4000),
        (_('club card'), 4000),
        (_('tarif'), 10000),
        (_('dates'), 4000),
        (_('use trainings'), 6000),
        (_('last visit'), 4000),
        (_('credits'), 4000),
        (_('freeze/prolongation'), 8000),
        (_('extra options'), 4000),
        (_('guest visit'), 4000),
    ]

    table_styles = {
        3: styles.styled,
    }

    def initial(self, request, *args, **kwargs):
        super(ActiveClubCard, self).initial(request, *args, **kwargs)
        try:
            clubcard_id = self.request.query_params.get('cc')
            self.clubcard = ClubCard.objects.get(pk=clubcard_id)
        except:
            self.clubcard = 'all'

    def get_fdate(self):
        return datetime.now()

    def get_title(self, **kwargs):
        msg = _('list active club cards')
        msg += _(' created at: {date}.')
        tdate = self.get_fdate().strftime('%d.%m.%Y %H:%M')
        return msg.format(date=tdate)

    def get_data(self):
        rows = []
        data = ClientClubCard.objects.filter(status=1).order_by('date_end')
        if self.clubcard != 'all':
            data = data.filter(club_card=self.clubcard)
        for row in data:
            line = []
            fname = row.client.first_name
            pname = row.client.patronymic
            lname = row.client.last_name
            uid = row.client.uid
            line.append((fname, pname, lname, uid))
            line.append(('', '', '', row.client.card))
            phone = row.client.mobile or row.client.phone or ''
            tariff = row.club_card.short_name
            amount = row.summ_amount
            if row.discount_value:
                dtype = '%' if row.discount_value <= 100 else _('rub.')
                discount = u'{txt}/{val} {dtype}'.format(
                    txt=row.discount_short,
                    val=row.discount_value, dtype=dtype)
            else:
                discount = ''
            line.append((phone, tariff, amount, discount))
            date_begin = row.date_begin.strftime('%d.%m.%Y')
            date_end = row.date_end.strftime('%d.%m.%Y')
            line.append((date_begin, date_end, '', ''))
            visits = row.visits.all()
            training = ClubCardTrains.objects.filter(visit__in=visits).count()
            line.append((training, '', ''))
            if visits:
                last_visit = visits.last().date.strftime('%d.%m.%Y')
                line.append((last_visit, '', '', ''))
            else:
                line.append(('', '', '', ''))
            schedule = []
            for p in row.schedule_payments():
                if p[0] <= self.get_fdate():
                    continue
                pdate = p[0].strftime('%d.%m.%Y')
                pamount = "{:,}".format(p[1]).replace(',', ' ')
                schedule.append("%s - %s" % (pamount, pdate))
            schedule.extend([''] * (4 - len(schedule)))
            line.append(schedule)
            freeze = []
            use_freeze = row.freeze.all()
            for f in use_freeze.filter(is_extra=False, is_paid=False):
                freeze.append(f.days)
            use_prol = row.prolongation.all()
            for p in use_prol.filter(is_extra=False, is_paid=False):
                freeze.append(p.days)
            freeze.extend([''] * (4 - len(freeze)))
            line.append(freeze)
            fitness = row.fitnessclubcard_set.first()
            fitness = fitness.date.strftime('%d.%m.%Y') if fitness else ''
            personal = row.personalclubcard_set.first()
            personal = personal.date.strftime('%d.%m.%Y') if personal else ''
            line.append((personal, '', '', fitness))
            guests = []
            for guest in row.guestclubcard_set.all().order_by('date'):
                guests.append(guest.date.strftime('%d.%m.%Y'))
            guests.extend([''] * (4 - len(guests)))
            line.append(guests)
            rows.append(line)
        self.total_rows = len(rows)
        return rows

    def write_heads(self):
        super(ActiveClubCard, self).write_heads()
        if self.clubcard != 'all':
            self.ws.write(2, 2, self.clubcard.name, styles.styleh)

    def write_bottom(self):
        self.ws.write(self.row_num, 1, _('total cards'))
        self.ws.write(self.row_num, 2, self.total_rows, styles.styleh)


class CreditsClubCard(ReportTemplate):

    file_name = 'credits_club_cards'
    sheet_name = 'report'
    tpl_path = 'xls_tpl/credits.xls'
    tpl_start_row = 6

    table_headers = [
        (_('client'), 4000),
        (_('club card'), 10000),
        (_('dates'), 4000),
        (_('credits'), 6000),
        (_('credits dates'), 4000),
    ]

    table_styles = {
        2: styles.style_c,
        3: styles.style_c,
        4: styles.style_c,
    }

    def initial(self, request, *args, **kwargs):
        super(CreditsClubCard, self).initial(request, *args, **kwargs)
        self.red_font = styles.style_red_font
        self.red_font.borders = styles.borders_cmb
        self.red_font.alignment = styles.alignment_c

    def get_fdate(self):
        return datetime.now()

    def get_title(self, **kwargs):
        return _("credits report").capitalize()

    def get_data(self):
        rows = []
        products = []
        qs = Credit.objects.order_by('schedule')
        data = qs.filter(club_card__isnull=False)
        data |= qs.filter(personal__isnull=False)
        for row in data:
            product = row.first_goods
            if product.pk not in products:
                products.append(product.pk)
            else:
                continue
            line = []
            fname = product.client.first_name
            pname = product.client.patronymic
            lname = product.client.last_name
            uid = product.client.uid
            line.append((fname, pname, lname, uid))
            phone = product.client.mobile or product.client.phone or ''
            tariff = product.product.short_name
            amount = product.summ_amount
            if product.discount_value:
                dtype = '%' if product.discount_value <= 100 else _('rub.')
                discount = u'{val} {dtype}'.format(
                    val=product.discount_value, dtype=dtype)
            else:
                discount = ''
            line.append((phone, tariff, amount, discount))
            if product.status < 2:
                date_begin = product.date_begin.strftime('%d.%m.%Y')
                date_end = product.date_end.strftime('%d.%m.%Y')
            else:
                date_begin = _("Product is disabled")
                date_end = ''
            last_visit = product.visits.last()
            if last_visit:
                last_visit = last_visit.date.strftime('%d.%m.%Y')
            else:
                last_visit = ''
            line.append((date_begin, date_end, '', last_visit))
            credits = product.credit_set.all(
            ).order_by('date').values_list('schedule', 'amount')
            amounts = []
            dates = []
            for cr_date, cr_amount in credits:
                amounts.append(cr_amount)
                if cr_date < date(1900, 1, 1):
                    dates.append('')
                else:
                    dates.append(cr_date.strftime('%d.%m.%Y'))
            amounts.extend([''] * (4 - len(amounts)))
            line.append(amounts)
            dates.extend([''] * (4 - len(dates)))
            line.append(dates)
            rows.append(line)
        return rows

    def write_heads(self):
        super(CreditsClubCard, self).write_heads()
        report_date = self.get_fdate().strftime('%d.%m.%Y')
        report_time = self.get_fdate().strftime('%H:%M')
        self.ws.write(1, 2, report_date, styles.styleh)
        self.ws.write(1, 4, report_time, styles.styleh)

    def write_multi_data(self, coll, cell, style):
        row_step = 0
        for j, subcell in enumerate(cell[:-1]):
            if coll == 4:
                self.write_crdate(self.row_num + j, subcell, style)
            else:
                self.ws.write(self.row_num + j, coll, subcell, style)
        # write bottom sub cell row
        old_bord = style.borders
        style.borders = styles.borders_cmb
        j += 1
        if coll == 4:
            self.write_crdate(self.row_num + j, cell[-1], style)
        else:
            self.ws.write(self.row_num + j, coll, cell[-1], style)
        style.borders = old_bord
        row_step = row_step if j < row_step else j
        return row_step

    def write_crdate(self, row_num, subcell, style):
        if subcell:
            sub_data = datetime.strptime(subcell, '%d.%m.%Y').date()
        else:
            sub_data = subcell
        if sub_data and sub_data < date.today():
            self.ws.write(row_num, 4, subcell, self.red_font)
        else:
            self.ws.write(row_num, 4, subcell, style)


class NewUid(Report):
    file_name = 'report_new_uid'
    sheet_name = 'the report of new uids'

    table_headers = [
        (_('# on item'), 2000),
        (_('# uid'), 4000),
        (_('date of conclusion'), 5000),
        (_('client'), 8000),
        (_('tariff'), 6000),
        (_('email'), 6000),
        (_('phone'), 6000),
    ]

    table_styles = {
        1: styles.style_c,
        2: styles.style_c,
        4: styles.style_c,
    }

    def get_title(self, **kwargs):
        msg = _('the report of new uids')
        return msg

    def write_title(self):
        super(NewUid, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        self.ws.write_merge(1, 1, 0, 5, msg, styles.styleh)

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        data = Client.objects.filter(
            date__range=(fdate, tdate), uid__gt=170000).order_by('date')
        for num, row in enumerate(data, 1):
            line = []
            line.append(num)
            line.append(row.uid)
            line.append(row.date.strftime('%d.%m.%Y'))
            line.append(row.full_name)
            card = row.initial_purchase
            if card:
                line.append(card.short_name)
            else:
                line.append('')
            line.append(row.email)
            phone = row.mobile or row.phone or ''
            line.append(phone)
            rows.append(line)
        return rows

    def write_bottom(self):
        pass


class CommonList(Report):
    file_name = 'common_list'
    sheet_name = 'common list'

    table_headers = [
        (_('# on item'), 2000),
        (_('client'), 8000),
        (_('# uid'), 4000),
        (_('birthday'), 4000),
        (_('mobile'), 7000),
        (_('period cards'), 8000),
        (_('email'), 6000),
    ]

    table_styles = {
        3: styles.styled,
    }

    def get_title(self, **kwargs):
        return _('common list')

    @staticmethod
    def format_mobile(value):
        if not value:
            return ''
        value = str(value)
        return '+7 (%s) %s - %s' % (value[0:3], value[3:6], value[6:10])

    def write_title(self):
        super(CommonList, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        self.ws.write_merge(1, 1, 0, 6, msg, styles.styleh)

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        client_cc = ClientClubCard.objects.filter(
            date__range=(fdate, tdate)
            ).values_list('client', flat=True)
        client_p = ClientPersonal.objects.filter(
            date__range=(fdate, tdate)
            ).values_list('client', flat=True)
        cids = set(list(client_cc) + list(client_p))
        data = Client.objects.extra(
            select={'lower_name': 'lower(clients_client.last_name)'}
            ).filter(pk__in=cids).order_by('lower_name')

        for num, row in enumerate(data, 1):
            line = []
            line.append(num)
            line.append(row.full_name)
            line.append(row.uid)
            line.append(row.born.strftime('%d.%m.%Y'))
            line.append(CommonList.format_mobile(row.mobile))
            cards = row.clientclubcard_set.filter(
                date__range=(fdate, tdate)
                ).values_list('club_card__short_name', flat=True)
            personals = row.clientpersonal_set.filter(
                date__range=(fdate, tdate)
                ).values_list('personal__short_name', flat=True)
            plist = list(cards) + list(personals)
            if plist:
                line.append(", ".join(plist))
            else:
                line.append('')
            line.append(row.email)
            rows.append(line)
        return rows

    def write_bottom(self):
        pass


class FullList(CommonList):
    table_headers = [
        (_('# on item'), 2000),
        (_('client'), 8000),
        (_('# uid'), 4000),
        (_('card number'), 2000),
        (_('birthday'), 4000),
        (_('mobile'), 7000),
        (_('period cards'), 12000),
        (_('email'), 6000),
        (_('active club card'), 10000),
    ]

    table_styles = {
        2: styles.style_c,
        3: styles.style_c,
    }

    def get_title(self, **kwargs):
        msg = _('full list')
        msg += _(' created at: {date}.')
        tdate = datetime.now().strftime('%d.%m.%Y %H:%M')
        return msg.format(date=tdate)

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        data = Client.objects.all(
        ).order_by('last_name', 'first_name', 'patronymic')
        for num, row in enumerate(data, 1):
            line = []
            line.append(num)
            line.append(row.full_name)
            line.append(row.uid)
            line.append(row.card)
            try:
                line.append(row.born.strftime('%d.%m.%Y'))
            except Exception as e:
                line.append(_('invalide date'))
            line.append(CommonList.format_mobile(row.mobile))
            cards = row.clientclubcard_set.filter(
                date__range=(fdate, tdate)
                ).order_by('date'
                ).values_list('club_card__short_name', flat=True)
            personals = row.clientpersonal_set.filter(
                date__range=(fdate, tdate)
                ).order_by('date'
                ).values_list('personal__short_name', flat=True)
            plist = list(cards) + list(personals)
            line.append(", ".join(plist))
            line.append(row.email)
            active_cc = row.active_cc.values_list(
                'club_card__name', flat=True)
            active_p = row.active_p.values_list(
                'personal__name', flat=True)
            pactive = list(active_cc) + list(active_p)
            line.append(", ".join(pactive))
            rows.append(line)
        return rows

    def write_title(self):
        self.ws.write_merge(0, 0, 0, len(self.table_headers) - 1,
                            self.title, styles.styleh)

    def get_fdate(self):
        return datetime(2000, 1, 1, 0, 0)

    def get_tdate(self):
        return datetime(2100, 1, 1, 0, 0)


class RepFitnessClubCard(Report):

    file_name = 'list_fitness_club_cards'
    sheet_name = 'list fitness club cards'

    table_headers = [
        (_('fitness test date'), 4000),
        (_('client'), 8000),
        (_('club card num'), 4000),
        (_('club card period'), 6000),
        (_('tariff'), 4000),
        (_('paid date'), 4000),
        (_('paid amount(50)'), 4000),
        (_('instructor'), 6000),
    ]

    table_styles = {
        0: styles.styled,
        5: styles.styled,
    }

    def get_title(self, **kwargs):
        return _('list fitness club cards')

    def write_title(self):
        super(RepFitnessClubCard, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        self.ws.write_merge(1, 1, 0, 7, msg, styles.styleh)

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        data = FitnessClubCard.objects.filter(
            date__range=(fdate, tdate)).order_by('date')
        for row in data:
            line = []
            line.append(row.date.strftime('%d.%m.%Y'))
            card = row.client_club_card
            line.append(card.client.full_name)
            line.append(card.client.card)
            period_data = {
                'bdate': card.date_begin.strftime('%d.%m.%Y'),
                'edate': card.date_end.strftime('%d.%m.%Y')
            }
            period = '{bdate}-{edate}'.format(**period_data)
            line.append(period)
            line.append(card.club_card.short_name)
            line.append('???')
            line.append('???')
            line.append(row.personal.initials)
            rows.append(line)
        self.total_rows = len(rows)
        return rows

    def write_bottom(self):
        self.ws.write(self.row_num, 1, _('total tests'))
        self.ws.write(self.row_num, 2, self.total_rows, styles.styleh)


class RepPersonalClubCard(Report):

    file_name = 'list_trainings_club_cards'
    sheet_name = 'list trainings club cards'

    table_headers = [
        (_('trainings test date'), 4000),
        (_('client'), 8000),
        (_('# uid'), 4000),
        (_('club card period'), 6000),
        (_('tariff'), 4000),
        (_('instructor'), 6000),
    ]

    table_styles = {
        0: styles.styled,
        5: styles.styled,
    }

    def get_title(self, **kwargs):
        return _('list trainings club cards')

    def write_title(self):
        super(RepPersonalClubCard, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        self.ws.write_merge(1, 1, 0, 5, msg, styles.styleh)

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        data = PersonalClubCard.objects.filter(
            date__range=(fdate, tdate)).order_by('date')
        for row in data:
            line = []
            line.append(row.date.strftime('%d.%m.%Y'))
            card = row.client_club_card
            line.append(card.client.full_name)
            line.append(card.client.uid)
            period_data = {
                'bdate': card.date_begin.strftime('%d.%m.%Y'),
                'edate': card.date_end.strftime('%d.%m.%Y')
            }
            period = '{bdate}-{edate}'.format(**period_data)
            line.append(period)
            line.append(card.club_card.short_name)
            line.append(row.personal.initials)
            rows.append(line)
        self.total_rows = len(rows)
        return rows

    def write_bottom(self):
        self.ws.write(self.row_num, 1, _('total trainings'))
        self.ws.write(self.row_num, 2, self.total_rows, styles.styleh)


class RepIntroductory(Report):

    file_name = 'list_introductory'
    sheet_name = 'list introductory'

    table_headers = [
        (_('introductory date'), 4000),
        (_('client'), 8000),
        (_('# uid'), 4000),
        (_('instructor'), 6000),
    ]

    table_styles = {
        0: styles.styled,
        5: styles.styled,
    }

    def get_title(self, **kwargs):
        return _('list introductory')

    def write_title(self):
        super(RepIntroductory, self).write_title()
        msg = _('from: {fdate} to {tdate}')
        fdate = self.get_fdate().strftime('%d.%m.%Y')
        tdate = self.get_tdate().strftime('%d.%m.%Y')
        msg = msg.format(fdate=fdate, tdate=tdate)
        self.ws.write_merge(1, 1, 0, 5, msg, styles.styleh)

    def get_data(self):
        rows = []
        fdate = self.get_fdate().date()
        tdate = self.get_tdate().date() + timedelta(1)
        data = Client.objects.filter(
            introductory_date__range=(fdate, tdate)
        ).order_by('introductory_date')
        for row in data:
            line = []
            line.append(row.introductory_date.strftime('%d.%m.%Y'))
            line.append(row.full_name)
            line.append(row.uid)
            line.append(row.introductory_employee.initials)
            rows.append(line)
        self.total_rows = len(rows)
        return rows

    def write_bottom(self):
        self.ws.write(self.row_num, 1, _('total introductory'))
        self.ws.write(self.row_num, 2, self.total_rows, styles.styleh)
