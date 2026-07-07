# SPDX-License-Identifier: AGPL-3.0-or-later
"""Native federation source-of-truth models. ``FederationRealm`` is the anchor: a LOCAL service
that participates in a federation (a Matrix homeserver, a Nextcloud, a SAML/OIDC IdP or SP, ...),
optionally linked to the ``netbox_services.ServiceInstance`` that deployed it. ``FederationPeer``
is a REMOTE federated party a realm trusts, with a direction and a trust level.

FKs to sibling models use STRING labels ("netbox_services.ServiceInstance") — never import those
into this module.

SECRET POLICY: a federation signing key or a peering shared secret is NEVER a field here.
``FederationRealm.signing_key_ref`` and ``FederationPeer.shared_secret_ref`` are OpenBao path
references (the netbox-services convention); the secret value stays in OpenBao.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from .choices import FederationDirectionChoices, FederationProtocolChoices, TrustLevelChoices


def validate_secret_ref(value, field_name):
    """Enforce the secret-boundary policy: a ``*_ref`` field holds an OpenBao KV PATH, never the
    secret value. A path contains ``/`` and is neither a URL (``://``) nor a user@host / email
    (``@``). Blank is allowed (the ref is optional). Raises ``ValidationError`` keyed to the field
    so an inline literal (e.g. a bare secret or a full URL) is rejected at ``clean()`` time — which
    NetBox's ``ValidatedModelSerializer`` runs, so the API path is covered too."""
    if not value:
        return
    if "://" in value or "@" in value or "/" not in value:
        raise ValidationError(
            {field_name: f"{field_name} must be an OpenBao path (e.g. clients/app/svc/key), "
                         "never the secret value or a URL."}
        )


class FederationRealm(NetBoxModel):
    """A LOCAL service that participates in federation. ``server_name`` is the federated identity —
    the domain the outside world addresses this realm by (e.g. ``matrix.example.org``, the
    Nextcloud domain, or the SAML/OIDC entity host). Optionally the
    ``netbox_services.ServiceInstance`` it was deployed as (composition link). ``open_federation``
    toggles between federating with any peer vs. only the explicit :class:`FederationPeer`
    allowlist."""

    name = models.CharField(max_length=100, unique=True)
    protocol = models.CharField(max_length=32, choices=FederationProtocolChoices)
    server_name = models.CharField(
        max_length=255, help_text="Federated identity / domain (e.g. matrix.example.org)."
    )
    service_instance = models.ForeignKey(
        "netbox_services.ServiceInstance", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="federation_realms",
        help_text="The netbox-services instance this realm was deployed as (composition link).",
    )
    well_known_url = models.URLField(
        blank=True, help_text="Federation discovery document (e.g. /.well-known/matrix/server)."
    )
    entity_id = models.CharField(
        max_length=255, blank=True, help_text="SAML/OIDC entity id (blank for non-identity protocols)."
    )
    signing_key_ref = models.CharField(
        max_length=255, blank=True,
        help_text="OpenBao path for the federation signing/private key — NEVER the secret.",
    )
    open_federation = models.BooleanField(
        default=False, help_text="Federate with any peer (True) vs. only the peer allowlist (False)."
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Federation Realm"

    def clean(self):
        super().clean()
        validate_secret_ref(self.signing_key_ref, "signing_key_ref")

    def __str__(self):
        return f"{self.name} ({self.protocol})"

    def get_absolute_url(self):
        return reverse("plugins:netbox_federation:federationrealm", args=[self.pk])

    def get_protocol_color(self):
        return FederationProtocolChoices.colors.get(self.protocol)


class FederationPeer(NetBoxModel):
    """A REMOTE federated party trusted by a realm. ``peer_domain`` is the remote server_name /
    domain; ``direction`` and ``trust_level`` bound the relationship. ``shared_secret_ref`` (e.g. a
    Nextcloud federated-share secret) and ``metadata_url`` (a SAML/OIDC IdP metadata endpoint) are
    optional. ``shared_secret_ref`` is an OpenBao PATH — never the secret value."""

    realm = models.ForeignKey(FederationRealm, on_delete=models.CASCADE, related_name="peers")
    peer_domain = models.CharField(
        max_length=255, help_text="Remote server_name / domain of the federated peer."
    )
    peer_endpoint = models.URLField(
        blank=True, help_text="Peer federation / metadata endpoint (blank = discover)."
    )
    direction = models.CharField(
        max_length=16, choices=FederationDirectionChoices, default=FederationDirectionChoices.BIDIRECTIONAL
    )
    trust_level = models.CharField(
        max_length=16, choices=TrustLevelChoices, default=TrustLevelChoices.FULL
    )
    shared_secret_ref = models.CharField(
        max_length=255, blank=True,
        help_text="OpenBao path for the peering shared secret (e.g. Nextcloud share) — NEVER the secret.",
    )
    metadata_url = models.URLField(
        blank=True, help_text="SAML/OIDC IdP metadata URL (blank for non-identity protocols)."
    )

    class Meta:
        ordering = ["realm", "peer_domain"]
        verbose_name = "Federation Peer"
        constraints = [
            models.UniqueConstraint(
                fields=["realm", "peer_domain"], name="netbox_federation_federationpeer_unique_realm_peer"
            ),
        ]

    def clean(self):
        super().clean()
        validate_secret_ref(self.shared_secret_ref, "shared_secret_ref")

    def __str__(self):
        return f"{self.realm.name} ↔ {self.peer_domain}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_federation:federationpeer", args=[self.pk])

    def get_direction_color(self):
        return FederationDirectionChoices.colors.get(self.direction)

    def get_trust_level_color(self):
        return TrustLevelChoices.colors.get(self.trust_level)
