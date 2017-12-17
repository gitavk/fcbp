from rest_framework import serializers

from .models import (UseClientClubCard, UseClientAquaAerobics,
                     UseClientTicket, UseClientPersonal, UseClientTiming,
                     ClubCardTrains)


class ClubCardTrainsSerializer(serializers.ModelSerializer):

    name = serializers.CharField(read_only=True)

    class Meta:
        model = ClubCardTrains


class UseClientClubCardSerializer(serializers.ModelSerializer):

    clubcardtrains_set = ClubCardTrainsSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = UseClientClubCard


class UseClientAquaAerobicsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UseClientAquaAerobics


class UseClientTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = UseClientTicket


class UseClientPersonalSerializer(serializers.ModelSerializer):
    instructor = serializers.ReadOnlyField(source='instructor.initials')
    instructor_id = serializers.ReadOnlyField(source='instructor.pk')
    positions = serializers.ListField(
        source='client_personal.positions', read_only=True)

    class Meta:
        model = UseClientPersonal

    def create(self, validated_data):
        instance = super(UseClientPersonalSerializer,
                         self).create(validated_data)
        # save read only field instructor
        instructor = self.context['request'].data.get('instructor')
        instance.instructor_id = instructor
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance = super(UseClientPersonalSerializer,
                         self).update(instance, validated_data)
        # save read only field instructor
        instructor = self.context['request'].data.get('instructor_id')
        instance.instructor_id = instructor
        instance.save()
        return instance


class UseClientTimingSerializer(serializers.ModelSerializer):

    class Meta:
        model = UseClientTiming
