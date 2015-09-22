from rest_framework import serializers

from .models import Credit, Payment
from .models_views import Debt, DebtUpcoming


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt


class DebtUpcomingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtUpcoming


class CreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credit
        read_only_fields = ('id', )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        read_only_fields = ('id', )
