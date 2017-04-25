from datetime import date, timedelta, datetime

from rest_framework import serializers

from .models import *
from .use_serializers import *
from products.models import *
from finance.serializers import *


class GuestClubCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestClubCard


class FreezeClubCardSerializer(serializers.ModelSerializer):
    tdate = serializers.DateTimeField(read_only=True)

    class Meta:
        model = FreezeClubCard


class FitnessClubCardSerializer(serializers.ModelSerializer):
    employee = serializers.CharField(read_only=True)

    class Meta:
        model = FitnessClubCard


class PersonalClubCardSerializer(serializers.ModelSerializer):
    employee = serializers.CharField(read_only=True)

    class Meta:
        model = PersonalClubCard


class ProlongationClubCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProlongationClubCard


class ArchiveListSerializer(serializers.ListSerializer):
    """
    Archive/disabled objects.
    """
    def to_representation(self, data):
        data = data.filter(status=0)
        return super(ArchiveListSerializer, self).to_representation(data)


class ClientClubCardSerializer(serializers.ModelSerializer):

    visits = UseClientClubCardSerializer(many=True, read_only=True)
    guestclubcard_set = GuestClubCardSerializer(many=True, read_only=True)
    client_name = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    rest_visits = serializers.CharField(read_only=True)
    client_mobile = serializers.IntegerField(read_only=True)
    client_uid = serializers.IntegerField(read_only=True)
    client_card = serializers.IntegerField(read_only=True)
    personalclubcard_set = PersonalClubCardSerializer(many=True,
                                                      read_only=True)
    fitnessclubcard_set = FitnessClubCardSerializer(many=True,
                                                    read_only=True)
    freezeclubcard_set = FreezeClubCardSerializer(many=True, read_only=True)
    prolongation = ProlongationClubCardSerializer(many=True, read_only=True)
    credit_set = CreditSerializer(many=True, read_only=True)
    payment_set = PaymentSerializer(many=True, read_only=True)

    class Meta:
        list_serializer_class = ArchiveListSerializer
        model = ClientClubCard


class FreezeAquaSerializer(serializers.ModelSerializer):
    tdate = serializers.DateTimeField(read_only=True)

    class Meta:
        model = FreezeAqua


class ProlongationAquaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProlongationAqua


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

    class Meta:
        list_serializer_class = ArchiveListSerializer
        model = ClientAquaAerobics


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
    name = serializers.CharField(read_only=True)
    freezeticket_set = FreezeTicketSerializer(many=True, read_only=True)
    prolongationticket_set = ProlongationTicketSerializer(
        many=True, read_only=True)

    class Meta:
        list_serializer_class = ArchiveListSerializer
        model = ClientTicket
