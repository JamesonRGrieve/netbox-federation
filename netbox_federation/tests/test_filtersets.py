# SPDX-License-Identifier: AGPL-3.0-or-later
"""FilterSet tests against a real DB (no mocks): FK-id scoping, choice filters, and search()."""
from django.test import TestCase
from netbox_federation.choices import (
    FederationDirectionChoices, FederationProtocolChoices, TrustLevelChoices,
)
from netbox_federation.filtersets import FederationPeerFilterSet, FederationRealmFilterSet
from netbox_federation.models import FederationPeer, FederationRealm


def _realm(name, protocol=FederationProtocolChoices.MATRIX_S2S):
    return FederationRealm.objects.create(name=name, protocol=protocol, server_name=f"{name}.example.org")


class FederationRealmFilterSetTest(TestCase):
    queryset = FederationRealm.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.r1 = _realm("matrix1", FederationProtocolChoices.MATRIX_S2S)
        cls.r2 = _realm("idp1", FederationProtocolChoices.SAML)

    def test_protocol(self):
        self.assertEqual(FederationRealmFilterSet({"protocol": ["saml"]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(FederationRealmFilterSet({"q": "idp1"}, self.queryset).qs.count(), 1)

    def test_search_by_server_name(self):
        self.assertEqual(FederationRealmFilterSet({"q": "matrix1.example.org"}, self.queryset).qs.count(), 1)


class FederationPeerFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.r1 = _realm("nc1", FederationProtocolChoices.NEXTCLOUD_FEDERATED_SHARING)
        cls.r2 = _realm("nc2", FederationProtocolChoices.NEXTCLOUD_FEDERATED_SHARING)
        FederationPeer.objects.bulk_create([
            FederationPeer(realm=cls.r1, peer_domain="alpha.example.net", direction=FederationDirectionChoices.INBOUND, trust_level=TrustLevelChoices.FULL),
            FederationPeer(realm=cls.r1, peer_domain="beta.example.net", direction=FederationDirectionChoices.OUTBOUND, trust_level=TrustLevelChoices.BLOCKED),
            FederationPeer(realm=cls.r2, peer_domain="gamma.example.net", direction=FederationDirectionChoices.BIDIRECTIONAL, trust_level=TrustLevelChoices.LIMITED),
        ])

    def test_realm_scope(self):
        self.assertEqual(FederationPeerFilterSet({"realm_id": [self.r1.pk]}, FederationPeer.objects.all()).qs.count(), 2)

    def test_direction(self):
        self.assertEqual(
            FederationPeerFilterSet({"direction": [FederationDirectionChoices.INBOUND]}, FederationPeer.objects.all()).qs.count(), 1
        )

    def test_trust_level(self):
        self.assertEqual(
            FederationPeerFilterSet({"trust_level": [TrustLevelChoices.BLOCKED]}, FederationPeer.objects.all()).qs.count(), 1
        )

    def test_search(self):
        self.assertEqual(FederationPeerFilterSet({"q": "gamma"}, FederationPeer.objects.all()).qs.count(), 1)
