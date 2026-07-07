<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-federation

A NetBox 4.6 plugin: the **native source of truth for cross-service / cross-org federation** — the
local services that participate in a federation and the remote peers / trust relationships they
hold, expressed uniformly across the federation protocols the lab runs: Matrix server-to-server,
Nextcloud federated sharing, SAML / OIDC identity federation, ActivityPub, and XMPP
server-to-server.

It is what the `tofu-matrix` / `tofu-nextcloud` / `tofu-authentik` providers read to realize each
side of a federation.

## Scope

- **In scope:** federated *realms* (a local service that federates, with its federated identity /
  server name, discovery URL, entity id, and signing-key reference) and their *peers* (a remote
  federated party, with direction and trust level).
- **Out of scope:** the service deployment itself (that is a `netbox-services` `ServiceInstance`,
  referenced not re-modeled) and secret values (OpenBao owns signing keys and shared secrets).

## Composes netbox-services

A federated realm is (optionally) a `netbox_services.ServiceInstance`. `FederationRealm` FKs it, so
`PluginConfig.required_plugins = ["netbox_services"]` and the migration depends on
`netbox_services.0001_initial`. This plugin is the **federation layer on top of** `ServiceInstance`
— it references, it does not re-model (the `netbox-ai` pattern).

## Model

- **FederationRealm** — a LOCAL service that participates in a federation. `name`, `protocol`
  (Matrix S2S / Nextcloud federated sharing / SAML / OIDC / ActivityPub / XMPP S2S), `server_name`
  (the federated identity / domain), optional `service_instance` composition link, `well_known_url`
  (discovery), `entity_id` (SAML/OIDC), `signing_key_ref` (**OpenBao path**), `open_federation`
  (federate with any peer vs. the allowlist).
- **FederationPeer** (FK realm) — a REMOTE federated party trusted by a realm. `peer_domain`,
  `peer_endpoint`, `direction` (inbound / outbound / bidirectional), `trust_level` (full / limited
  / blocked), `shared_secret_ref` (**OpenBao path**), `metadata_url` (SAML/OIDC IdP metadata).
  Unique per `(realm, peer_domain)`.

All models inherit `NetBoxModel` (custom fields, tags, change logging, GraphQL, REST API).

## Secret policy

A federation signing key or a peering shared secret is **never** a field here.
`FederationRealm.signing_key_ref` and `FederationPeer.shared_secret_ref` are **OpenBao path
references** (the `netbox-services` convention). NetBox holds the structure; OpenBao holds the
secret.

## Install

```bash
uv pip install --python /opt/netbox/venv/bin/python netbox-federation   # or: pip install -e .
# add "netbox_federation" to PLUGINS in configuration.py (netbox_services must be enabled too)
python manage.py migrate netbox_federation
python manage.py collectstatic --no-input
systemctl restart netbox netbox-rq
```

## Develop / test

Tests run against a **real NetBox test database** (no mocks) via NetBox's Django test framework.

```bash
python /opt/netbox/app/netbox/manage.py test netbox_federation --keepdb -v2
```

## License

AGPL-3.0-or-later.
