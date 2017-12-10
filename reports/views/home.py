# -*- coding: utf-8 -*-
from django.views.generic import View
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _

from clients.models import ClientClubCard, ClientPersonal
from employees.models import Employee


class Home(View, ):
    template_name = 'reports/menu.html'

    def get(self, request, *args, **kwargs):
        cc = ClientClubCard.objects.filter(status=1)
        cc_options = cc.values(
            'club_card__name', 'club_card__pk'
        ).order_by('club_card__name').distinct()
        pc = ClientPersonal.objects.filter(status=1)
        pc_options = pc.values(
            'personal__name', 'personal__pk'
        ).order_by('personal__name').distinct()
        trainers = Employee.objects.filter(personals__isnull=False
            ).distinct().order_by('last_name')
        cont = dict(
            request=request, title=_('Reports'),
            cc_options=cc_options, pc_options=pc_options,
            trainers=trainers,
        )
        return render_to_response(self.template_name, cont)


class Reception(View, ):
    template_name = 'reports/reception_menu.html'

    def get(self, request, *args, **kwargs):
        cont = dict(request=request, title=_('Reports'))
        return render_to_response(self.template_name, cont)
