# -*- coding: utf-8 -*-
import uuid
from datetime import datetime, date, timedelta

from django.db.models.loading import get_model
from django.db.models import Sum, Q


class WritePayment(object):

    def add_payment(self, payment_type, force=False):
        payment_model = get_model('finance', 'Payment')
        if (not self.pk or force) and self.is_paid:
            if hasattr(self, 'parent'):
                client = self.parent.client
                goods = self.parent
            else:
                client = self.client
                goods = self
            p_data = {
                'date': datetime.now(),
                'payment_type': payment_type,
                'amount': self.amount,
                'count': 1,
                'extra_uid': uuid.uuid4(),
                'extra_text': self.paid_text,
                'client': client,
                self.payment_goods: goods
            }
            payment_model.objects.create(**p_data)


class Prolongation(object):

    def parent_upd(self, *args, **kwargs):
        days = self.days
        parent = self.parent
        is_delete = kwargs.get('is_delete')
        if is_delete:
            parent.date_end = parent.date_end - timedelta(days)
        else:
            parent.date_end = parent.date_end + timedelta(days)
        parent.save()


class Property(object):

    """ Generic property need for all services """
    @property
    def client_mobile(self):
        return self.client.mobile

    @property
    def client_uid(self):
        return self.client.uid

    @property
    def client_name(self):
        return self.client.full_name

    @property
    def client_card(self):
        return self.client.card

    @property
    def name(self):
        return self.product.name

    @property
    def first_payment(self):
        all_payment = self.payment_set.all()
        return all_payment.order_by('date').first()

    @property
    def short_name(self):
        return self.product.short_name

    @property
    def has_overdue_debt(self):
        now = datetime.now()
        return self.credit_set.filter(schedule__lte=now).exists()

    @property
    def summ_amount(self):
        amount = 0
        q_filter = Q(extra_uid__exact='') | Q(extra_uid__isnull=True)
        psum = self.payment_set.filter(q_filter).aggregate(sum=Sum('amount'))
        if psum.get('sum', 0):
            amount += psum.get('sum', 0)
        csum = self.credit_set.all().aggregate(sum=Sum('amount'))
        if csum.get('sum', 0):
            amount += csum.get('sum', 0)
        return amount

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

    def full_name(self):
        return self.product.full_name

    def first_visit(self):
        return self.visits.all().order_by('date').first()

    def is_full_time(self):
        return self.product.is_full_time

    def schedule_payments(self):
        pre_payments = []
        schedule_start = self.date + timedelta(1)
        payments = self.payment_set.filter(
            date__gt=schedule_start, extra_uid__isnull=True)
        for p in payments.order_by('date'):
            pre_payments.append((p.date, p.amount))
        for cr in self.credit_set.all().order_by('schedule'):
            pdate = datetime.combine(cr.schedule, datetime.min.time())
            pre_payments.append((pdate, cr.amount))
        return pre_payments

    def similar_products(self):
        model = self.product._meta.model
        period = self.product.period
        products = model.objects.filter(is_active=True, period=period)
        return products.exclude(pk=self.product.pk)

    def escape_frozen(self):
        freeze_model = get_model('clients', self.freeze_class)
        filtr = {freeze_model.product: self, 'fdate__lte': date.today()}
        freezes = freeze_model.objects.filter(**filtr)
        for f in freezes:
            if f.tdate >= date.today():
                days_freeze = (date.today() - f.fdate).days
                days_back = (f.tdate - date.today()).days + 1
                self.date_end = self.date_end - timedelta(days_back)
                self.save()
                f.days = days_freeze
                f.save()

    def price(self):
        return self.product.price
