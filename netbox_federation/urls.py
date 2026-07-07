# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from . import models, views


def _routes(slug, name, model, list_view, edit_view, detail_view, delete_view, bulk_delete_view):
    return [
        path(f"{slug}/", list_view.as_view(), name=f"{name}_list"),
        path(f"{slug}/add/", edit_view.as_view(), name=f"{name}_add"),
        path(f"{slug}/delete/", bulk_delete_view.as_view(), name=f"{name}_bulk_delete"),
        path(f"{slug}/<int:pk>/", detail_view.as_view(), name=name),
        path(f"{slug}/<int:pk>/edit/", edit_view.as_view(), name=f"{name}_edit"),
        path(f"{slug}/<int:pk>/delete/", delete_view.as_view(), name=f"{name}_delete"),
        path(f"{slug}/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name=f"{name}_changelog", kwargs={"model": model}),
        path(f"{slug}/<int:pk>/journal/", ObjectJournalView.as_view(), name=f"{name}_journal", kwargs={"model": model}),
    ]


urlpatterns = [
    *_routes("realms", "federationrealm", models.FederationRealm,
             views.FederationRealmListView, views.FederationRealmEditView, views.FederationRealmView,
             views.FederationRealmDeleteView, views.FederationRealmBulkDeleteView),
    *_routes("peers", "federationpeer", models.FederationPeer,
             views.FederationPeerListView, views.FederationPeerEditView, views.FederationPeerView,
             views.FederationPeerDeleteView, views.FederationPeerBulkDeleteView),
]
