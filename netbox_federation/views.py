# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.views import generic
from . import filtersets, forms, models, tables


class FederationRealmView(generic.ObjectView):
    queryset = models.FederationRealm.objects.all()


class FederationRealmListView(generic.ObjectListView):
    queryset = models.FederationRealm.objects.all()
    table = tables.FederationRealmTable
    filterset = filtersets.FederationRealmFilterSet
    filterset_form = forms.FederationRealmFilterForm


class FederationRealmEditView(generic.ObjectEditView):
    queryset = models.FederationRealm.objects.all()
    form = forms.FederationRealmForm


class FederationRealmDeleteView(generic.ObjectDeleteView):
    queryset = models.FederationRealm.objects.all()


class FederationRealmBulkDeleteView(generic.BulkDeleteView):
    queryset = models.FederationRealm.objects.all()
    table = tables.FederationRealmTable


class FederationPeerView(generic.ObjectView):
    queryset = models.FederationPeer.objects.all()


class FederationPeerListView(generic.ObjectListView):
    queryset = models.FederationPeer.objects.all()
    table = tables.FederationPeerTable
    filterset = filtersets.FederationPeerFilterSet
    filterset_form = forms.FederationPeerFilterForm


class FederationPeerEditView(generic.ObjectEditView):
    queryset = models.FederationPeer.objects.all()
    form = forms.FederationPeerForm


class FederationPeerDeleteView(generic.ObjectDeleteView):
    queryset = models.FederationPeer.objects.all()


class FederationPeerBulkDeleteView(generic.BulkDeleteView):
    queryset = models.FederationPeer.objects.all()
    table = tables.FederationPeerTable
