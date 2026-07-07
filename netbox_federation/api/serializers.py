# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.serializers import NetBoxModelSerializer
from netbox_services.api.serializers import ServiceInstanceSerializer
from rest_framework import serializers
from ..models import FederationPeer, FederationRealm


class FederationRealmSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_federation-api:federationrealm-detail")
    service_instance = ServiceInstanceSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = FederationRealm
        fields = [
            "id", "url", "display", "name", "protocol", "server_name", "service_instance",
            "well_known_url", "entity_id", "signing_key_ref", "open_federation",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "protocol", "server_name"]


class FederationPeerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_federation-api:federationpeer-detail")
    realm = FederationRealmSerializer(nested=True)

    class Meta:
        model = FederationPeer
        fields = [
            "id", "url", "display", "realm", "peer_domain", "peer_endpoint", "direction",
            "trust_level", "shared_secret_ref", "metadata_url",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "realm", "peer_domain"]
