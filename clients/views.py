import json
from datetime import datetime, timedelta

from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route
from rest_framework.pagination import PageNumberPagination

from django.views.generic.base import TemplateResponseMixin
from django.utils.translation import ugettext as _
from django.conf import settings

from .models import *
from .forms import *
from .serializers import *
from .serializers_light import ClientClubCardSerial
from .use_serializers import *
from products.models import CardText
from products.serializers import *
from finance.forms import FormCredit


class ClientResultsSetPagination(PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class ClientViewSet(TemplateResponseMixin, viewsets.ModelViewSet):

    serializer_class = ClientSerializer
    pagination_class = ClientResultsSetPagination

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_serializer_class(self):
        serializer_class = super(ClientViewSet, self).get_serializer_class()
        if self.action == 'list':
            return ClientListSerializer
        return serializer_class

    def get_queryset(self):
        """
        Optionally restricts the returned clients,
        by filtering against a `letter` query parameter in the URL.
        """
        queryset = Client.objects.order_by(
            'last_name', 'first_name', 'patronymic')

        letter = self.request.query_params.get('letter', None)
        if letter is not None:
            queryset = queryset.filter(last_name__istartswith=letter)

        return queryset

    @detail_route(methods=['get'], )
    def personal(self, request, pk):
        """
        Print personal client card.
        """
        client = self.get_object()
        cont = {'client': client}
        self.template_name = 'client_personal.html'
        return TemplateResponseMixin.render_to_response(self, cont)

    @list_route(methods=['get'], )
    def online(self, request):
        """
        List clients inside the club.
        """
        clients = ClientOnline.objects.all().order_by('date')
        serializer = ClientOnlineSerializer(clients, many=True)
        return Response(serializer.data)

    @list_route(methods=['post'], )
    def search(self, request):
        """
        Search clients by carb or uid or istartswith last_name.
        """
        search = request.data['search'][settings.CARD_SET]
        try:
            search = int(search)
            queryset = Client.objects.filter(card=search)
            queryset = queryset | Client.objects.filter(uid=search)
        except:
            queryset = Client.objects.filter(last_name__istartswith=search)
        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['post'], )
    def full_search(self, request):
        """
        Search clients istartswith last_name, first_name and patronymic.
        """
        queryset = Client.objects.filter(pk=-1)
        last_name = request.data.get('last_name', None)
        if last_name:
            queryset = queryset | Client.objects.filter(
                last_name__istartswith=last_name)
        first_name = request.data.get('first_name', None)
        if first_name:
            queryset = queryset | Client.objects.filter(
                first_name__istartswith=first_name)
        patronymic = request.data.get('patronymic', None)
        if patronymic:
            queryset = queryset | Client.objects.filter(
                patronymic__istartswith=patronymic)

        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['post'], )
    def exact_search(self, request):
        """
        Search clients iexact of last_name, first_name and patronymic.
        """
        last_name = request.data.get('last_name', None)
        if last_name:
            queryset = Client.objects.filter(last_name__iexact=last_name)
        first_name = request.data.get('first_name', None)
        if first_name:
            if last_name:
                queryset = queryset.filter(first_name__iexact=first_name)
            else:
                queryset = Client.objects.filter(last_name__iexact=first_name)
        patronymic = request.data.get('patronymic', None)
        if patronymic:
            if last_name or first_name:
                queryset = queryset.filter(patronymic__iexact=patronymic)
            else:
                queryset = Client.objects.filter(last_name__iexact=patronymic)
        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post'], )
    def introductory(self, request, pk):
        """
        Set introductory for the user.
        """
        client = self.get_object()
        form = FormClientIntro(request.data, instance=client)
        if form.is_valid():
            form.save()
        else:
            print form.errors
        return Response({'status': 'ok'}, status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['get'], )
    def last_clubcard(self, request, pk):
        """
        Set introductory for the user.
        """
        client = self.get_object()
        queryset = ClientClubCard.objects.filter(client=client)\
                                         .order_by('-date')[:5]
        first = queryset[0]
        last = queryset[1:5]
        serializer_first = ClientClubCardSerial(first)
        serializer_last = ClientClubCardSerial(last, many=True)
        return Response({'first': serializer_first.data,
                         'last': serializer_last.data},
                        status=status.HTTP_202_ACCEPTED)


class GenericProduct(object):

    """ Generic options for client's products."""
    @detail_route(methods=['post'], )
    def activation(self, request, pk):
        data = request.data.copy()
        obj = self.get_object()
        date_begin = data.get('date_begin', datetime.now())
        obj.activate(date_begin=date_begin)
        return Response({'status': 'ok'})

    @detail_route(methods=['post'], )
    def freeze(self, request, pk):
        """
        freeze the card and update the date_end of the card.
        """
        data = request.data.copy()
        obj = self.get_object()
        data[self.freeze_obj] = obj.pk
        data['client'] = obj.client.pk
        serializer = self.serializer_freeze(data=data)
        if serializer.is_valid():
            serializer.save()
            date_end = obj.date_end + timedelta(serializer.data['days'])
            obj.date_end = date_end
            obj.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    @detail_route(methods=['get'], )
    def similar(self, request, pk):
        obj = self.get_object()
        data = obj.similar_products()
        serializer = self.serializer_similar(data, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post'], )
    def new_type(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        amount = request.data.get('amount')
        if amount:
            data = {}
            data['amount'] = amount
            data['schedule'] = request.data.get('date')
            data['discount'] = 0
            data['count'] = 1
            data['client'] = instance.client.pk
            data[self.finance_obj] = instance.pk
            form = FormCredit(data)
            if form.is_valid():
                form.save()
            else:
                print form.errors
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        is_paid_activate = request.data.get('is_paid_activate')
        if is_paid_activate:
            payment_type = request.data.pop('payment_type',)
            instance.amount = request.data.get('paid_activate_amount')
            instance.add_payment(payment_type,  force=True)
        return Response(serializer.data)


class FreezeClubCardViewSet(viewsets.ModelViewSet):
    queryset = FreezeClubCard.objects.all()
    serializer_class = FreezeClubCardSerializer


class OwnersClubCardViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = OwnersClubCard.objects.all()
    serializer_class = OwnersClubCardSerializer


class OwnersPersonalViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = OwnersClientPersonal.objects.all()
    serializer_class = OwnersPersonalSerializer


class ClientClubCardViewSet(
        GenericProduct, viewsets.ModelViewSet, TemplateResponseMixin):
    queryset = ClientClubCard.objects.order_by('-date')
    serializer_class = ClientClubCardSerializer
    serializer_freeze = FreezeClubCardSerializer
    serializer_similar = ClubCardSerializer
    freeze_obj = 'client_club_card'
    finance_obj = 'club_card'

    @detail_route(methods=['get'], )
    def card(self, request, pk):
        """
        Print form of the card.
        """
        card = self.get_object()
        pre_payments = []
        for p in card.payment_set.all().order_by('date'):
            pre_payments.append((p.date, p.amount))
        for cr in card.credit_set.all().order_by('schedule'):
            pre_payments.append((cr.schedule, cr.amount))
        # rebuild payments to four elements
        payments = []
        for k, v in map(None, pre_payments, '*'*4):
            if k is not None:
                payments.append(k)
            else:
                payments.append((None, None))
        text = CardText.objects.get(pk=1)
        cont = {'card': card, 'payments': payments, 'text': text}
        card.printed = True
        card.save()
        self.template_name = 'card/clubcard.html'
        return TemplateResponseMixin.render_to_response(self, cont)

    @detail_route(methods=['post'], )
    def guest(self, request, pk):
        """
        use free guest visit
        """
        data = request.data.copy()
        data['client_club_card'] = self.get_object().pk
        serializer = GuestClubCardSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_406_NOT_ACCEPTABLE)


class FitnessClubCardViewSet(viewsets.ModelViewSet):
    queryset = FitnessClubCard.objects.order_by('-date')
    serializer_class = FitnessClubCardSerializer


class PersonalClubCardViewSet(viewsets.ModelViewSet):
    queryset = PersonalClubCard.objects.order_by('-date')
    serializer_class = PersonalClubCardSerializer


class ProlongationTicketViewSet(viewsets.ModelViewSet):
    queryset = ProlongationTicket.objects.order_by('-date')
    serializer_class = ProlongationTicketSerializer


class ProlongationAquaViewSet(viewsets.ModelViewSet):
    queryset = ProlongationAqua.objects.order_by('-date')
    serializer_class = ProlongationAquaSerializer


class ProlongationClubCardViewSet(viewsets.ModelViewSet):
    queryset = ProlongationClubCard.objects.order_by('-date')
    serializer_class = ProlongationClubCardSerializer


class ProlongationPersonalViewSet(viewsets.ModelViewSet):
    queryset = ProlongationPersonal.objects.order_by('-date')
    serializer_class = ProlongationPersonalSerializer


class ClientAquaAerobicsViewSet(
        GenericProduct, viewsets.ModelViewSet, TemplateResponseMixin):
    queryset = ClientAquaAerobics.objects.order_by('-date')
    serializer_class = ClientAquaAerobicsSerializer
    serializer_freeze = FreezeAquaSerializer
    freeze_obj = 'client_aqua'

    @detail_route(methods=['get'], )
    def card(self, request, pk):
        """
        Print form of the card.
        """
        aqua = self.get_object()
        pre_payments = []
        for p in aqua.payment_set.all().order_by('date'):
            pre_payments.append((p.date, p.amount))
        for cr in aqua.credit_set.all().order_by('schedule'):
            pre_payments.append((cr.schedule, cr.amount))
        # rebuild payments to four elements
        payments = []
        for k, v in map(None, pre_payments, '*'*4):
            if k is not None:
                payments.append(k)
            else:
                payments.append((None, None))
        cont = {'aqua': aqua, 'payments': payments}
        self.template_name = 'card/aqua.html'
        return TemplateResponseMixin.render_to_response(self, cont)


class ClientTicketViewSet(
        GenericProduct, viewsets.ModelViewSet, TemplateResponseMixin):
    queryset = ClientTicket.objects.order_by('-date')
    serializer_class = ClientTicketSerializer
    serializer_freeze = FreezeTicketSerializer
    freeze_obj = 'client_ticket'

    @detail_route(methods=['get'], )
    def card(self, request, pk):
        """
        Print form of the card.
        """
        ticket = self.get_object()
        pre_payments = []
        for p in ticket.payment_set.all().order_by('date'):
            pre_payments.append((p.date, p.amount))
        for cr in ticket.credit_set.all().order_by('schedule'):
            pre_payments.append((cr.schedule, cr.amount))
        # rebuild payments to four elements
        payments = []
        for k, v in map(None, pre_payments, '*'*4):
            if k is not None:
                payments.append(k)
            else:
                payments.append((None, None))
        cont = {'ticket': ticket, 'payments': payments}
        self.template_name = 'card/ticket.html'
        return TemplateResponseMixin.render_to_response(self, cont)


class ClientPersonalViewSet(viewsets.ModelViewSet):
    queryset = ClientPersonal.objects.order_by('-date')
    serializer_class = ClientPersonalSerializer
    serializer_similar = PersonalSerializer
    finance_obj = 'personal'

    @detail_route(methods=['post'], )
    def add_extra(self, request, pk):
        obj = self.get_object()
        extra_client = self.request.data.get('extra_client')
        PersonalClients.objects.get_or_create(
            client_id=extra_client, personal=obj)
        return Response({})

    @detail_route(methods=['get'], )
    def similar(self, request, pk):
        obj = self.get_object()
        data = obj.similar_products().filter(
            max_visit__gte=obj.product.max_visit)
        serializer = self.serializer_similar(data, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post'], )
    def new_type(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        amount = request.data.get('amount')
        if amount:
            data = {}
            data['amount'] = amount
            data['schedule'] = request.data.get('date')
            data['discount'] = 0
            data['count'] = 1
            data['client'] = instance.client.pk
            data[self.finance_obj] = instance.pk
            form = FormCredit(data)
            if form.is_valid():
                form.save()
            else:
                print form.errors
        return Response(serializer.data)


class ClientTimingViewSet(viewsets.ModelViewSet):
    queryset = ClientTiming.objects.order_by('-date')
    serializer_class = ClientTimingSerializer


class UseClientClubCardViewSet(viewsets.ModelViewSet):
    queryset = UseClientClubCard.objects.order_by('-date')
    serializer_class = UseClientClubCardSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        serializer = UseClientClubCardSerializer(instance, data=data)
        if serializer.is_valid():
            serializer.save()
        trainings = data.get('clubcardtrains_set', [])
        if len(trainings) < 1:
            return Response({'error': _('Empty trainings')})
        rest_trains = len(
            trainings) - instance.clubcardtrains_set.all().count()
        card = instance.client_club_card
        if rest_trains > card.rest_visits_int:
            return Response({'error': _('Too many trainings')})
        if instance.clubcardtrains_set.all():
            instance.clubcardtrains_set.all().delete()
        for tr in trainings:
            ClubCardTrains.objects.create(
                visit_id=instance.pk, training_id=tr['training'])
        return Response(serializer.data)

    def create(self, request):
        """
        Comming client to the club and escape existing freeze.
        """
        data = request.data.copy()
        trainings = data.get('trainings', [])
        if len(trainings) < 1:
            return Response({'error': _('Empty trainings')})
        card_id = int(request.data['client_club_card'])
        card = ClientClubCard.objects.get(pk=card_id)
        if card.status == 0:
            return Response({'error': _('Card is disabled')})
        if len(trainings) > card.rest_visits_int:
            return Response({'error': _('Too many trainings')})
        serializer = UseClientClubCardSerializer(data=data)
        if serializer.is_valid():
            obj = serializer.save()
            # save trainings
            for tr in trainings:
                ClubCardTrains.objects.create(visit_id=obj.pk,
                                              training_id=tr['id'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    @list_route(methods=['post'], )
    def exit(self, request):
        card_id = request.data['client_club_card']
        exits = UseClientClubCard.objects.filter(
            client_club_card=card_id, end=None)
        for e in exits:
            e.end = datetime.now()
            e.save()
        return Response({'status': 'ok'}, status=status.HTTP_202_ACCEPTED)


class UseClientAquaAerobicsViewSet(viewsets.ModelViewSet):
    queryset = UseClientAquaAerobics.objects.order_by('-date')
    serializer_class = UseClientAquaAerobicsSerializer

    @list_route(methods=['post'], )
    def exit(self, request):
        aqua_id = request.data['client_aqua_aerobics']
        exit = UseClientAquaAerobics.objects\
                                    .filter(client_aqua_aerobics=aqua_id,
                                            end=None)\
                                    .update(end=datetime.now())
        return Response({'status': 'ok'}, status=status.HTTP_202_ACCEPTED)


class UseClientTicketViewSet(viewsets.ModelViewSet):
    queryset = UseClientTicket.objects.order_by('-date')
    serializer_class = UseClientTicketSerializer

    @list_route(methods=['post'], )
    def exit(self, request):
        ticket_id = request.data['client_ticket']
        exit = UseClientTicket.objects\
                              .filter(client_ticket=ticket_id,
                                      end=None)\
                              .update(end=datetime.now())
        return Response({'status': 'ok'}, status=status.HTTP_202_ACCEPTED)


class UseClientPersonalViewSet(viewsets.ModelViewSet):
    queryset = UseClientPersonal.objects.order_by('-date')
    serializer_class = UseClientPersonalSerializer

    @list_route(methods=['post'], )
    def exit(self, request):
        personal_id = request.data['client_personal']
        exits = UseClientPersonal.objects.filter(
            client_personal=personal_id, end=None)
        for e in exits:
            e.end = datetime.now()
            e.save()
        return Response({'status': 'ok'}, status=status.HTTP_202_ACCEPTED)


class UseClientTimingViewSet(viewsets.ModelViewSet):
    queryset = UseClientTiming.objects.order_by('-date')
    serializer_class = UseClientTimingSerializer
