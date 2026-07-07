# SPDX-License-Identifier: AGPL-3.0-or-later
"""netbox-federation: NetBox as the native source of truth for **cross-service / cross-org
federation** — the local services that participate in a federation and the remote peers / trust
relationships they hold, expressed uniformly across the federation protocols the lab actually runs:
Matrix server-to-server, Nextcloud federated sharing, SAML / OIDC identity federation,
ActivityPub, and XMPP server-to-server.

A :class:`netbox_federation.models.FederationRealm` is a *local* service that federates (a Matrix
homeserver, a Nextcloud, an Authentik / SAML IdP-or-SP, ...). A
:class:`netbox_federation.models.FederationPeer` is a *remote* federated party a realm trusts, with
a direction and a trust level. Consumers ``tofu-matrix`` / ``tofu-nextcloud`` / ``tofu-authentik``
read this plugin as SoT to realize each side of a federation.

**It composes ``netbox-services``, it does not re-model it (the netbox-ai pattern):** a federated
realm is (optionally) a :class:`netbox_services.ServiceInstance` — ``FederationRealm`` **FKs** it,
so ``required_plugins = ["netbox_services"]`` and the migration depends on
``netbox_services.0001_initial``.

**Secret policy (load-bearing):** a federation signing key or a peering shared secret is **never** a
field here. ``FederationRealm.signing_key_ref`` and ``FederationPeer.shared_secret_ref`` are OpenBao
**path references** (the netbox-services convention); the secret value stays in OpenBao.
"""
from netbox.plugins import PluginConfig

__version__ = "0.0.1"


class NetBoxFederationConfig(PluginConfig):
    name = "netbox_federation"
    verbose_name = "NetBox Federation"
    description = "Native SoT for cross-service/cross-org federation realms and peers (Matrix S2S, Nextcloud, SAML/OIDC, ActivityPub, XMPP S2S)"
    version = __version__
    author = "Jameson"
    base_url = "federation"
    min_version = "4.6.0"
    max_version = "4.6.99"
    # FederationRealm.service_instance FKs netbox_services.ServiceInstance and the migration depends
    # on netbox_services.0001_initial, so the dependency is hard and fails fast at startup.
    required_plugins = ["netbox_services"]


config = NetBoxFederationConfig
