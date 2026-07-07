# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import FederationPeer, FederationRealm
from .serializers import FederationPeerSerializer, FederationRealmSerializer


class FederationRealmViewSet(NetBoxModelViewSet):
    queryset = FederationRealm.objects.prefetch_related("service_instance", "tags")
    serializer_class = FederationRealmSerializer
    filterset_class = filtersets.FederationRealmFilterSet


class FederationPeerViewSet(NetBoxModelViewSet):
    queryset = FederationPeer.objects.prefetch_related("realm", "tags")
    serializer_class = FederationPeerSerializer
    filterset_class = filtersets.FederationPeerFilterSet
