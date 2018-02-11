from django.db.models import Q

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from .models import *
from .serializers_archive import *


class GenericArhiveProduct(object):

    """ Generic options for client's arhive products."""
    @detail_route(methods=['post'], )
    def reopen(self, request, pk):
        obj = self.get_object()
        obj.status = 1
        obj.save()
        return Response({'status': 'ok'})

    @detail_route(methods=['post'], )
    def purge_credits(self, request, pk):
        obj = self.get_object()
        obj.credit_set.all().delete()
        return Response({'status': 'ok'})


class ClientClubCardViewSet(
        GenericArhiveProduct,
        viewsets.ReadOnlyModelViewSet):

    queryset = ClientClubCard.objects.order_by('-date')
    serializer_class = ClientClubCardSerializer

    @detail_route(methods=['get'], )
    def client(self, request, pk):
        """
        Get list archive club card for the client.
        """
        client = Client.objects.get(pk=pk)
        queryset = ClientClubCard.objects.filter(client=client)\
                                         .order_by('-date')
        serializer = ClientClubCardSerializer(queryset, many=True)
        return Response(serializer.data,
                        status=status.HTTP_202_ACCEPTED)


class ClientPersonalViewSet(
        GenericArhiveProduct,
        viewsets.ReadOnlyModelViewSet):

    queryset = ClientPersonal.objects.order_by('-date')
    serializer_class = ClientPersonalSerializer

    @detail_route(methods=['get'], )
    def client(self, request, pk):
        """
        Get list archive Client Personal for the client.
        """
        client = Client.objects.get(pk=pk)
        extra_personals = client.extra_personals.values('personal')
        qf = Q(pk__in=extra_personals) | Q(client=client)
        qs = ClientPersonal.objects.filter(qf).order_by('-date')
        serializer = ClientPersonalSerializer(qs, many=True)
        return Response(serializer.data,
                        status=status.HTTP_202_ACCEPTED)


class ClientAquaAerobicsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClientAquaAerobics.objects.order_by('-date')
    serializer_class = ClientAquaAerobicsSerializer

    @detail_route(methods=['get'], )
    def client(self, request, pk):
        """
        Get list archive aqua for the client.
        """
        client = Client.objects.get(pk=pk)
        queryset = ClientAquaAerobics.objects.filter(client=client)\
                                             .order_by('-date')
        serializer = ClientAquaAerobicsSerializer(queryset, many=True)
        return Response(serializer.data,
                        status=status.HTTP_202_ACCEPTED)


class ClientAquaAerobicsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClientAquaAerobics.objects.order_by('-date')
    serializer_class = ClientAquaAerobicsSerializer

    @detail_route(methods=['get'], )
    def client(self, request, pk):
        """
        Get list archive aqua for the client.
        """
        client = Client.objects.get(pk=pk)
        queryset = ClientAquaAerobics.objects.filter(client=client)\
                                             .order_by('-date')
        serializer = ClientAquaAerobicsSerializer(queryset, many=True)
        return Response(serializer.data,
                        status=status.HTTP_202_ACCEPTED)


class ClientTicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClientTicket.objects.order_by('-date')
    serializer_class = ClientTicketSerializer

    @detail_route(methods=['get'], )
    def client(self, request, pk):
        """
        Get list archive aqua for the client.
        """
        client = Client.objects.get(pk=pk)
        queryset = ClientTicket.objects.filter(
            client=client).order_by('-date')
        serializer = ClientTicketSerializer(queryset, many=True)
        return Response(serializer.data,
                        status=status.HTTP_202_ACCEPTED)
