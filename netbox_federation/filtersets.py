# SPDX-License-Identifier: AGPL-3.0-or-later
import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from .choices import FederationDirectionChoices, FederationProtocolChoices, TrustLevelChoices
from .models import FederationPeer, FederationRealm

# Explicit FK filters: django-filter does NOT derive `<fk>_id` from a bare FK in Meta.fields, so
# `?realm_id=` would be silently ignored. NetBox convention is `<fk>_id` (by PK) + `<fk>` (name).


class FederationRealmFilterSet(NetBoxModelFilterSet):
    protocol = django_filters.MultipleChoiceFilter(choices=FederationProtocolChoices)

    class Meta:
        model = FederationRealm
        fields = ["id", "name", "server_name", "entity_id", "well_known_url", "signing_key_ref",
                  "open_federation", "service_instance_id"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(server_name__icontains=value)
            | Q(entity_id__icontains=value)
        )


class FederationPeerFilterSet(NetBoxModelFilterSet):
    realm_id = django_filters.ModelMultipleChoiceFilter(
        field_name="realm", queryset=FederationRealm.objects.all(), label="Realm (ID)"
    )
    realm = django_filters.ModelMultipleChoiceFilter(
        field_name="realm__name", to_field_name="name", queryset=FederationRealm.objects.all(),
        label="Realm (name)",
    )
    direction = django_filters.MultipleChoiceFilter(choices=FederationDirectionChoices)
    trust_level = django_filters.MultipleChoiceFilter(choices=TrustLevelChoices)

    class Meta:
        model = FederationPeer
        fields = ["id", "peer_domain", "peer_endpoint", "shared_secret_ref", "metadata_url"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(peer_domain__icontains=value) | Q(peer_endpoint__icontains=value)
            | Q(realm__name__icontains=value)
        )
