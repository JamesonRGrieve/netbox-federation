# SPDX-License-Identifier: AGPL-3.0-or-later
"""Choice sets for the federation models. Protocol values match the on-the-wire federation
mechanism verbatim; direction and trust level bound each realm↔peer relationship."""
from utilities.choices import ChoiceSet


class FederationProtocolChoices(ChoiceSet):
    """The federation mechanism a realm speaks. ``matrix_s2s`` (Matrix server-to-server),
    ``nextcloud_federated_sharing`` (Nextcloud OCM federated shares), ``saml`` / ``oidc``
    (identity federation), ``activitypub`` (fediverse), ``xmpp_s2s`` (XMPP server-to-server)."""
    MATRIX_S2S = "matrix_s2s"
    NEXTCLOUD_FEDERATED_SHARING = "nextcloud_federated_sharing"
    SAML = "saml"
    OIDC = "oidc"
    ACTIVITYPUB = "activitypub"
    XMPP_S2S = "xmpp_s2s"
    CHOICES = [
        (MATRIX_S2S, "Matrix S2S", "green"),
        (NEXTCLOUD_FEDERATED_SHARING, "Nextcloud Federated Sharing", "blue"),
        (SAML, "SAML", "indigo"),
        (OIDC, "OIDC", "purple"),
        (ACTIVITYPUB, "ActivityPub", "orange"),
        (XMPP_S2S, "XMPP S2S", "cyan"),
    ]


class FederationDirectionChoices(ChoiceSet):
    """Direction of trust/flow between a realm and a peer. ``inbound`` (peer federates to us),
    ``outbound`` (we federate to the peer), ``bidirectional`` (mutual)."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"
    CHOICES = [
        (INBOUND, "Inbound", "blue"),
        (OUTBOUND, "Outbound", "orange"),
        (BIDIRECTIONAL, "Bidirectional", "green"),
    ]


class TrustLevelChoices(ChoiceSet):
    """How far a realm trusts a peer. ``full`` (unrestricted federation), ``limited`` (partial /
    filtered federation), ``blocked`` (explicitly denied — a denylist entry)."""
    FULL = "full"
    LIMITED = "limited"
    BLOCKED = "blocked"
    CHOICES = [
        (FULL, "Full", "green"),
        (LIMITED, "Limited", "yellow"),
        (BLOCKED, "Blocked", "red"),
    ]
