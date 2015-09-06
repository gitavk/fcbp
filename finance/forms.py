# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms

from .models import Credit
from clients.models import ClientClubCard, ClientAquaAerobics
from clients.models import ClientTicket, ClientPersonal, ClientTiming


class FormCredit(ModelForm):
	class Meta:
		model = Credit
		exclude = ['date', ]


class FormClientClubCard(ModelForm):
    class Meta:
        model = ClientClubCard
        exclude = ['date', ]


class FormClientAquaAerobics(ModelForm):
    class Meta:
        model = ClientAquaAerobics
        exclude = ['date', ]


class FormClientTicket(ModelForm):
    class Meta:
        model = ClientTicket
        exclude = ['date', ]


class FormClientPersonal(ModelForm):
    class Meta:
        model = ClientPersonal
        exclude = ['date', ]


class FormClientTiming(ModelForm):
    class Meta:
        model = ClientTiming
        exclude = ['date', ]