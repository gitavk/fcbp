import uuid
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta

from django.utils.translation import ugettext as _
from django.db.models.loading import get_model
from rest_framework import serializers

from .models import *
from .forms import *
from .use_serializers import *
from .owners_serializers import (
    OwnersClubCardSerializer, OwnersPersonalSerializer)
from products.models import *
from finance.serializers import *
from finance.forms import *


class Base64ImageField(serializers.ImageField):

    """
    A Django REST framework field for handling image-uploads through
    raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import uuid

        # Check if this is a base64 string
        if isinstance(data, basestring):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            # 12 characters are more than enough.
            file_name = str(uuid.uuid4())[:12]
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class GuestClubCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = GuestClubCard


class FreezeClubCardSerializer(serializers.ModelSerializer):
    tdate = serializers.DateTimeField(read_only=True)
    payment_type = serializers.IntegerField(write_only=True)

    class Meta:
        model = FreezeClubCard

    def create(self, validated_data):
        payment_type = validated_data.pop('payment_type')
        obj = FreezeClubCard(**validated_data)
        obj.save(payment_type=payment_type)
        return obj


class FitnessClubCardSerializer(serializers.ModelSerializer):
    employee = serializers.CharField(read_only=True)

    class Meta:
        model = FitnessClubCard


class PersonalClubCardSerializer(serializers.ModelSerializer):
    employee = serializers.CharField(read_only=True)

    class Meta:
        model = PersonalClubCard


class ProlongationClubCardSerializer(serializers.ModelSerializer):
    payment_type = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProlongationClubCard

    def create(self, validated_data):
        payment_type = validated_data.pop('payment_type')
        obj = ProlongationClubCard(**validated_data)
        obj.save(payment_type=payment_type)
        return obj


class ActiveListSerializer(serializers.ListSerializer):

    """
    Exclude archive/disabled objects.
    """

    def to_representation(self, data):
        data = data.exclude(status=0)
        return super(ActiveListSerializer, self).to_representation(data)


class ArchiveListSerializer(serializers.ListSerializer):

    """
    Archive/disabled objects.
    """

    def to_representation(self, data):
        data = data.filter(status=False)
        return super(ArchiveListSerializer, self).to_representation(data)


class ClientClubCardSerializer(serializers.ModelSerializer):

    visits = UseClientClubCardSerializer(many=True, read_only=True)
    owners = OwnersClubCardSerializer(many=True, read_only=True)
    guestclubcard_set = GuestClubCardSerializer(many=True, read_only=True)
    client_name = serializers.CharField(read_only=True)
    discount_description = serializers.CharField(read_only=True)
    client_mobile = serializers.IntegerField(read_only=True)
    client_uid = serializers.IntegerField(read_only=True)
    client_card = serializers.IntegerField(read_only=True)
    personalclubcard_set = PersonalClubCardSerializer(many=True,
                                                      read_only=True)
    fitnessclubcard_set = FitnessClubCardSerializer(many=True,
                                                    read_only=True)
    freeze = FreezeClubCardSerializer(many=True, read_only=True)
    prolongation = ProlongationClubCardSerializer(many=True, read_only=True)
    credit_set = CreditSerializer(many=True, read_only=True)
    payment_set = PaymentSerializer(many=True, read_only=True)

    class Meta:
        list_serializer_class = ActiveListSerializer
        model = ClientClubCard
        fields = ('id', 'club_card', 'status', 'date', 'date_start',
                  'date_begin', 'date_end', 'name', 'client', 'is_online',
                  'rest_days', 'rest_visits', 'visits', 'printed',
                  'rest_guest', 'guest_training', 'guestclubcard_set',
                  'fitness_testing_discount', 'personal_training',
                  'personalclubcard_set', 'fitnessclubcard_set',
                  'rest_freeze', 'rest_freeze_times', 'is_frozen', 'freeze',
                  'prolongation', 'client_name', 'credit_set', 'payment_set',
                  'client_card', 'client_mobile', 'is_paid_activate',
                  'paid_activate_amount', 'discount_amount', 'bonus_amount',
                  'client_uid', 'block_comment', 'employee', 'owners',
                  'discount_description', 'infuture', 'rest_prolongation',
                  'is_full_time', 'price', 'has_overdue_debt')
        read_only_fields = ('id', )

    def create(self, validated_data,):
        data = self.context['request'].data.copy()
        data['count'] = 1
        data['status'] = 2
        data['date_start'] = date.today()
        fclub_card = FormClientClubCard(data)
        if fclub_card.is_valid():
            club_card = fclub_card.save()
            data['club_card'] = club_card.pk
            finance(data)
            if club_card.is_paid_activate:
                payment_type = data.pop('payment_type',)
                club_card.amount = club_card.paid_activate_amount
                club_card.add_payment(payment_type,  force=True)
        else:
            print fclub_card.errors
        return club_card

    def validate_date_begin(self, value):
        if self.instance and self.instance.first_visit():
            if self.instance.first_visit().date.date() < value:
                raise serializers.ValidationError(_('date less first visit'))
        return value


class FreezeAquaSerializer(serializers.ModelSerializer):
    tdate = serializers.DateTimeField(read_only=True)

    class Meta:
        model = FreezeAqua


class ProlongationAquaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProlongationAqua


class ClientExtraSerializer(serializers.ModelSerializer):

    """
    Serializer for saving or update data for multi-client's products.
    """
    active_cc_first = ClientClubCardSerializer(read_only=True)

    class Meta:
        model = Client
        fields = (
            'id', 'first_name', 'last_name', 'patronymic', 'born', 'uid',
            'mobile', 'card', 'initials', 'full_name', 'active_cc_first')
        read_only_fields = (
            'id', 'uid', 'mobile', 'card', 'initials', 'active_cc_first')


class ClientAquaAerobicsSerializer(serializers.ModelSerializer):
    useclientaquaaerobics_set = UseClientAquaAerobicsSerializer(many=True,
                                                                read_only=True)
    rest_visits = serializers.IntegerField(read_only=True)
    is_online = serializers.IntegerField(read_only=True)
    is_frozen = serializers.BooleanField(read_only=True)
    name = serializers.CharField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    rest_days = serializers.IntegerField(read_only=True)
    client_uid = serializers.IntegerField(read_only=True)
    client_card = serializers.IntegerField(read_only=True)
    client_mobile = serializers.IntegerField(read_only=True)
    credit_set = CreditSerializer(many=True, read_only=True)
    payment_set = PaymentSerializer(many=True, read_only=True)
    freezeaqua_set = FreezeAquaSerializer(many=True, read_only=True)
    prolongationaqua_set = ProlongationAquaSerializer(
        many=True, read_only=True)
    extra_client = ClientExtraSerializer(many=True, read_only=True)

    class Meta:
        list_serializer_class = ActiveListSerializer
        model = ClientAquaAerobics

    def create(self, validated_data,):
        data = self.context['request'].data.copy()
        data['count'] = 1
        data['status'] = 2
        data['date_start'] = date.today()
        faqua_aerobics = FormClientAquaAerobics(data)
        if faqua_aerobics.is_valid():
            aqua_aerobics = faqua_aerobics.save()
            for ex in data['extraclients']:
                born = ex['born']
                born = datetime.strptime(ex['born'], '%Y-%m-%d').date()
                ex['born'] = born
                cl = ClientExtraSerializer(data=ex)
                if cl.is_valid():
                    cl = Client.objects\
                               .get_or_create(first_name=ex['first_name'],
                                              last_name=ex['last_name'],
                                              patronymic=ex['patronymic'],
                                              born=born)[0]
                    ex_aqua = {}
                    ex_aqua['client'] = cl.pk
                    ex_aqua['client_aqua'] = aqua_aerobics.pk
                    faqua_aerobics = FormAquaAerobicsClients(ex_aqua)
                    if faqua_aerobics.is_valid():
                        faqua_aerobics.save()
                    else:
                        print 'aqua_ex: %s' % faqua_aerobics.errors
                else:
                    print 'client_ex: %s' % cl.errors
            data['aqua_aerobics'] = aqua_aerobics.pk
            finance(data)
        else:
            print faqua_aerobics.errors
        return aqua_aerobics


class ClientAquaAerobicsFullSerializer(serializers.ModelSerializer):
    useclientaquaaerobics_set = UseClientAquaAerobicsSerializer(many=True,
                                                                read_only=True)

    class Meta:
        list_serializer_class = ActiveListSerializer
        model = ClientAquaAerobicsFull
        fields = ('id', 'aqua_aerobics', 'status', 'date', 'date_start',
                  'date_begin', 'date_end', 'useclientaquaaerobics_set',
                  'rest_days', 'name', 'client', 'rest_visits', 'is_online',
                  'is_frozen')


class FreezeTicketSerializer(serializers.ModelSerializer):
    tdate = serializers.DateTimeField(read_only=True)

    class Meta:
        model = FreezeTicket


class ProlongationTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProlongationTicket


class ClientTicketSerializer(serializers.ModelSerializer):
    useclientticket_set = UseClientTicketSerializer(many=True,
                                                    read_only=True)
    client_name = serializers.CharField(read_only=True)
    client_mobile = serializers.IntegerField(read_only=True)
    client_uid = serializers.IntegerField(read_only=True)
    client_card = serializers.IntegerField(read_only=True)
    is_frozen = serializers.BooleanField(read_only=True)
    is_online = serializers.IntegerField(read_only=True)
    rest_visits = serializers.IntegerField(read_only=True)
    credit_set = CreditSerializer(many=True, read_only=True)
    payment_set = PaymentSerializer(many=True, read_only=True)
    name = serializers.CharField(read_only=True)
    freezeticket_set = FreezeTicketSerializer(many=True, read_only=True)
    prolongationticket_set = ProlongationTicketSerializer(
        many=True, read_only=True)

    class Meta:
        list_serializer_class = ActiveListSerializer
        model = ClientTicket

    def create(self, validated_data,):
        data = self.context['request'].data.copy()
        data['count'] = 1
        data['status'] = 2
        data['date_start'] = date.today()
        obj = Ticket.objects.get(pk=data['ticket'])
        fticket = FormClientTicket(data)
        if fticket.is_valid():
            ticket = fticket.save()
            data['ticket'] = ticket.pk
            finance(data)
        else:
            print fticket.errors
        return ticket


class ProlongationPersonalSerializer(serializers.ModelSerializer):
    payment_type = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProlongationPersonal

    def create(self, validated_data):
        payment_type = validated_data.pop('payment_type')
        obj = ProlongationPersonal(**validated_data)
        obj.save(payment_type=payment_type)
        return obj


class ClientPersonalSerializer(serializers.ModelSerializer):
    visits = UseClientPersonalSerializer(many=True, read_only=True)
    owners = OwnersPersonalSerializer(many=True, read_only=True)
    instructor_name = serializers.CharField(
        source='instructor.initials', read_only=True)
    name = serializers.CharField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    client_mobile = serializers.IntegerField(
        source='client.mobile', read_only=True)
    client_uid = serializers.IntegerField(
        source='client.uid', read_only=True)
    client_card = serializers.IntegerField(
        source='client.card', read_only=True)
    rest_visits = serializers.CharField(read_only=True)
    credit_set = CreditSerializer(many=True, read_only=True)
    payment_set = PaymentSerializer(many=True, read_only=True)
    discount_description = serializers.CharField(read_only=True)
    discount_amount = serializers.FloatField(read_only=True)
    bonus_amount = serializers.FloatField(read_only=True)
    prolongation = ProlongationPersonalSerializer(many=True, read_only=True)
    rest_prolongation = serializers.IntegerField(read_only=True)
    is_online = serializers.IntegerField(read_only=True)
    positions = serializers.ListField(read_only=True)
    has_overdue_debt = serializers.BooleanField(read_only=True)
    is_club_card_only = serializers.BooleanField(
        source='personal.club_card_only', read_only=True)
    total_cients = serializers.IntegerField(
        source='personal.clients_count', read_only=True)
    extra_clients = ClientExtraSerializer(
        source='get_extra_clients', many=True, read_only=True)
    first_client_cc = ClientClubCardSerializer(
        source='client.active_cc_first', read_only=True)
    all_first_client_cc = serializers.BooleanField(read_only=True)

    class Meta:
        model = ClientPersonal

    def create(self, validated_data,):
        data = self.context['request'].data.copy()
        data['count'] = 1
        data['status'] = 2
        data['date_start'] = date.today()
        fpersonal = FormClientPersonal(data)
        if fpersonal.is_valid():
            personal = fpersonal.save()
            data['personal'] = personal.pk
            finance(data)
        else:
            print fpersonal.errors
        return personal


class ClientTimingSerializer(serializers.ModelSerializer):
    useclienttiming_set = UseClientTimingSerializer(many=True, read_only=True)
    client_name = serializers.CharField(read_only=True)

    class Meta:
        model = ClientTiming
        fields = ('id', 'timing', 'status', 'date', 'date_start', 'client',
                  'date_begin', 'date_end', 'name', 'useclienttiming_set',
                  'rest_days', 'rest_minutes', 'client_name')

    def create(self, validated_data,):
        data = self.context['request'].data.copy()
        data['count'] = 1
        data['status'] = 2
        data['date_start'] = date.today()
        data['date_begin'] = date.today()
        obj = Timing.objects.get(pk=data['timing'])
        data['date_end'] = date_end(data['date_begin'], obj)
        ftiming = FormClientTiming(data)
        if ftiming.is_valid():
            timing = ftiming.save()
            data['timing'] = timing.pk
            finance(data)
        else:
            print ftiming.errors
        return timing


class ClientSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(max_length=None, use_url=True)
    clientclubcard_set = ClientClubCardSerializer(
        many=True, read_only=True)
    clientaquaaerobicsfull_set = ClientAquaAerobicsFullSerializer(
        many=True,
        read_only=True)
    clientticket_set = ClientTicketSerializer(many=True, read_only=True)
    clienttiming_set = ClientTimingSerializer(many=True, read_only=True)
    credit_set = CreditSerializer(many=True, read_only=True)
    debt_set = DebtSerializer(many=True, read_only=True)
    debtupcoming_set = DebtUpcomingSerializer(many=True, read_only=True)
    online_clubcard = serializers.BooleanField(read_only=True)
    online_aqua = serializers.BooleanField(read_only=True)
    online_ticket = serializers.BooleanField(read_only=True)
    online_personal = serializers.BooleanField(read_only=True)
    introductory_employee_name = serializers.CharField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    passport = serializers.CharField(read_only=True)
    clientpersonal_set = serializers.SerializerMethodField()

    class Meta:
        model = Client
        read_only_fields = (
            'id', 'full_name', 'avatar_url', 'date')

    def get_clientpersonal_set(self, obj):
        qs = obj.clientpersonal_set.filter(status__gt=0)
        extra_qs = obj.extra_personals.filter(personal__status__gt=0)
        qs |= ClientPersonal.objects.filter(pk__in=extra_qs.values('personal'))
        serializer = ClientPersonalSerializer(qs, many=True)
        return serializer.data


class ClientSerializerLight(serializers.ModelSerializer):
    debt_set = DebtSerializer(many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Client


class ClientListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    has_clientclubcard = serializers.BooleanField(read_only=True)
    has_clientaquaaerobics = serializers.BooleanField(read_only=True)
    has_clientticket = serializers.BooleanField(read_only=True)
    has_clientpersonal = serializers.BooleanField(read_only=True)
    has_clienttiming = serializers.BooleanField(read_only=True)

    class Meta:
        model = Client


class ClientOnlineSerializer(serializers.ModelSerializer):
    client_data = ClientSerializerLight(read_only=True)

    class Meta:
        model = ClientOnline
        # fields = ('date', 'client_data')


def finance(data):
    """
    Finance records for the service of the client.
    """
    # Add Payment
    fpayment = FormPayment(data)
    if fpayment.is_valid():
        fpayment.save()
    else:
        print fpayment.errors
    # Create credit schedule
    for credit in data['credits']:
        data['amount'] = credit['amount']
        data['schedule'] = credit['date']
        form = FormCredit(data)
        if form.is_valid():
            form.save()
        else:
            print form.errors
