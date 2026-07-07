# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests against a real DB + real API client (no mocks).

Composes the explicit CRUD mixins (no GraphQL type shipped yet). FederationPeer create rows target
a shared realm; realm create rows are self-contained (no required host FK)."""
from utilities.testing import APIViewTestCases
from netbox_federation.choices import FederationProtocolChoices
from netbox_federation.models import FederationPeer, FederationRealm


class _CRUD(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    pass


def _realm(name, protocol=FederationProtocolChoices.MATRIX_S2S):
    return FederationRealm.objects.create(name=name, protocol=protocol, server_name=f"{name}.example.org")


class FederationRealmAPITest(_CRUD):
    model = FederationRealm
    brief_fields = ["display", "id", "name", "protocol", "server_name", "url"]
    bulk_update_data = {"open_federation": True}

    @classmethod
    def setUpTestData(cls):
        for i in range(3):
            _realm(f"exist-{i}")
        cls.create_data = [
            {"name": "realm-a", "protocol": "matrix_s2s", "server_name": "matrix.example.org"},
            {"name": "realm-b", "protocol": "saml", "server_name": "idp.example.org",
             "entity_id": "https://idp.example.org/metadata", "signing_key_ref": "federation/idp/key"},
            {"name": "realm-c", "protocol": "activitypub", "server_name": "social.example.org", "open_federation": True},
        ]


class FederationPeerAPITest(_CRUD):
    model = FederationPeer
    brief_fields = ["display", "id", "peer_domain", "realm", "url"]
    bulk_update_data = {"trust_level": "limited"}

    @classmethod
    def setUpTestData(cls):
        realm = _realm("peer-host", FederationProtocolChoices.NEXTCLOUD_FEDERATED_SHARING)
        FederationPeer.objects.bulk_create([
            FederationPeer(realm=realm, peer_domain="e0.example.net"),
            FederationPeer(realm=realm, peer_domain="e1.example.net", trust_level="limited"),
            FederationPeer(realm=realm, peer_domain="e2.example.net", direction="inbound"),
        ])
        cls.create_data = [
            {"realm": realm.pk, "peer_domain": "k1.example.net", "direction": "outbound", "trust_level": "full"},
            {"realm": realm.pk, "peer_domain": "k2.example.net", "shared_secret_ref": "federation/nc/k2",
             "peer_endpoint": "https://k2.example.net/ocm"},
            {"realm": realm.pk, "peer_domain": "k3.example.net", "trust_level": "blocked",
             "metadata_url": "https://k3.example.net/metadata"},
        ]
