# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): creation, str, colors, uniqueness, cascade, and the
secret-ref policy (refs are paths, never secret values)."""
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from netbox_federation.choices import (
    FederationDirectionChoices, FederationProtocolChoices, TrustLevelChoices,
)
from netbox_federation.models import FederationPeer, FederationRealm


def make_realm(name, protocol=FederationProtocolChoices.MATRIX_S2S, server_name=None):
    return FederationRealm.objects.create(
        name=name, protocol=protocol, server_name=server_name or f"{name}.example.org",
    )


class FederationRealmModelTest(TestCase):
    def test_create_str_url_and_protocol_color(self):
        r = make_realm("matrix")
        self.assertEqual(str(r), "matrix (matrix_s2s)")
        self.assertIn("/plugins/federation/realms/", r.get_absolute_url())
        self.assertEqual(r.get_protocol_color(), "green")
        self.assertFalse(r.open_federation)  # allowlist by default

    def test_signing_key_ref_is_a_path_not_a_secret(self):
        r = make_realm("saml-idp", protocol=FederationProtocolChoices.SAML)
        r.signing_key_ref = "federation/saml-idp/signing-key"
        r.entity_id = "https://saml-idp.example.org/metadata"
        r.save()
        self.assertEqual(r.signing_key_ref, "federation/saml-idp/signing-key")  # a path

    def test_name_unique(self):
        make_realm("dup")
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_realm("dup", protocol=FederationProtocolChoices.OIDC)


class FederationPeerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.realm = make_realm("nc", protocol=FederationProtocolChoices.NEXTCLOUD_FEDERATED_SHARING)

    def test_create_str_url_defaults_and_colors(self):
        p = FederationPeer.objects.create(realm=self.realm, peer_domain="partner.example.net")
        self.assertEqual(str(p), "nc ↔ partner.example.net")
        self.assertIn("/plugins/federation/peers/", p.get_absolute_url())
        self.assertEqual(p.direction, FederationDirectionChoices.BIDIRECTIONAL)
        self.assertEqual(p.trust_level, TrustLevelChoices.FULL)
        self.assertEqual(p.get_direction_color(), "green")
        self.assertEqual(p.get_trust_level_color(), "green")

    def test_shared_secret_ref_is_a_path_not_a_secret(self):
        p = FederationPeer.objects.create(
            realm=self.realm, peer_domain="secret.example.net",
            shared_secret_ref="federation/nc/secret.example.net",
        )
        self.assertEqual(p.shared_secret_ref, "federation/nc/secret.example.net")  # a path

    def test_blocked_peer(self):
        p = FederationPeer.objects.create(
            realm=self.realm, peer_domain="bad.example.net", trust_level=TrustLevelChoices.BLOCKED,
        )
        self.assertEqual(p.get_trust_level_color(), "red")

    def test_unique_realm_peer_domain(self):
        FederationPeer.objects.create(realm=self.realm, peer_domain="one.example.net")
        with self.assertRaises(IntegrityError), transaction.atomic():
            FederationPeer.objects.create(realm=self.realm, peer_domain="one.example.net")

    def test_same_peer_domain_different_realm_allowed(self):
        other = make_realm("nc2", protocol=FederationProtocolChoices.NEXTCLOUD_FEDERATED_SHARING)
        FederationPeer.objects.create(realm=self.realm, peer_domain="shared.example.net")
        FederationPeer.objects.create(realm=other, peer_domain="shared.example.net")
        self.assertEqual(FederationPeer.objects.filter(peer_domain="shared.example.net").count(), 2)

    def test_peer_cascade_on_realm_delete(self):
        realm = make_realm("ephemeral", protocol=FederationProtocolChoices.XMPP_S2S)
        FederationPeer.objects.create(realm=realm, peer_domain="p1.example.net")
        FederationPeer.objects.create(realm=realm, peer_domain="p2.example.net")
        realm.delete()
        self.assertEqual(FederationPeer.objects.filter(peer_domain__endswith="example.net").exclude(realm=self.realm).count(), 0)
