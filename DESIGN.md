<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-federation — Design

## 0. Purpose

NetBox is the native source of truth for **cross-service / cross-org federation** — the local
services that participate in a federation and the remote parties they trust. It spans the
federation protocols the lab actually runs, one uniform model for all: Matrix server-to-server,
Nextcloud federated sharing (OCM), SAML and OIDC identity federation, ActivityPub, and XMPP
server-to-server.

The insight is that every one of these is the same shape — *"a local realm with a federated
identity trusts a set of remote peers, in some direction, at some trust level"* — even though the
wire protocols differ. Modeling it once, natively, lets `tofu-matrix` / `tofu-nextcloud` /
`tofu-authentik` each read the same SoT to realize their side.

Everything is a real typed column — no `config_context`, no CustomField data-blob (the workspace's
retired anti-pattern).

## 1. Model diagram

```
        netbox_services.ServiceInstance
                   ▲ (optional FK — composition link)
                   │
          ┌────────┴──────────────────────────────────┐
          │              FederationRealm               │
          │  name·protocol·server_name·well_known_url· │
          │  entity_id·signing_key_ref·open_federation │
          └────────────────────┬───────────────────────┘
                               │ FK peers (CASCADE)
                               ▼
                        FederationPeer
          peer_domain·peer_endpoint·direction·
          trust_level·shared_secret_ref·metadata_url
                 unique (realm, peer_domain)
```

- **FederationRealm** is the anchor: a LOCAL service that federates. `protocol` selects the
  federation mechanism; `server_name` is the federated identity the outside world addresses it by
  (a Matrix `server_name`, the Nextcloud domain, the SAML/OIDC entity host). `service_instance` is
  an *optional* composition link to the `netbox-services` instance that deployed it
  (`on_delete=SET_NULL` — deleting the deployment record must not cascade away the federation SoT).
  `open_federation` toggles allow-any vs. allowlist-only peering. `signing_key_ref` is an OpenBao
  **path** to the federation signing/private key (§3), never the key itself. `entity_id` /
  `well_known_url` carry the protocol-specific discovery identity where applicable (SAML/OIDC
  entity id; Matrix/`.well-known` discovery).
- **FederationPeer** is a REMOTE federated party a realm trusts. `direction`
  (inbound/outbound/bidirectional) and `trust_level` (full/limited/blocked — `blocked` is a
  denylist entry) bound the relationship. `shared_secret_ref` is an OpenBao **path** for a peering
  shared secret (e.g. a Nextcloud federated-share secret); `metadata_url` points at a SAML/OIDC IdP
  metadata document. Unique per `(realm, peer_domain)` — a realm names each peer once — while the
  same `peer_domain` may recur under different realms.

## 2. The compose-with-netbox-services boundary

`netbox-services` owns the **service catalog + instance layer**. A federated service *is* a
`ServiceInstance` (its catalog row carries deployment metadata, health endpoint, resources, etc.).
`FederationRealm` **FKs** that instance rather than re-modeling deployment metadata:
`required_plugins = ["netbox_services"]` + the migration dependency on
`netbox_services.0001_initial` make the dependency hard and fail-fast — the `netbox-ai` pattern.
The link is optional (`null=True`) so a realm for an externally-hosted or not-yet-catalogued
service can still be recorded.

This plugin adds **only** the federation relationship layer on top; it duplicates nothing from
`netbox-services`.

## 3. Secret-ref policy

A federation signing key or a peering shared secret is **never** a model field.
`FederationRealm.signing_key_ref` and `FederationPeer.shared_secret_ref` are **OpenBao path
references** — the `netbox-services` `credential_ref` convention. NetBox holds the structure (which
realm speaks which protocol under which identity, which peers it trusts in which direction);
OpenBao holds the secret value, resolved at apply time by the provider. State and change logs
therefore never carry a plaintext key or secret.

## 4. Consumers (how the providers read this)

- **`tofu-matrix`** reads `FederationRealm` (protocol `matrix_s2s`) + its `FederationPeer` rows to
  configure the homeserver's federation allowlist/denylist and `server_name` / `.well-known`
  delegation; the signing key is fetched from OpenBao at `signing_key_ref`.
- **`tofu-nextcloud`** reads `FederationRealm` (protocol `nextcloud_federated_sharing`) + peers to
  configure trusted servers / OCM federated sharing, with the per-peer share secret from
  `shared_secret_ref`.
- **`tofu-authentik`** reads `FederationRealm` (protocol `saml` / `oidc`) — `entity_id`,
  `well_known_url`, `signing_key_ref` — and its peers (`metadata_url`, `direction`) to wire the
  IdP/SP federation.
- The ActivityPub / XMPP S2S protocols follow the same realm↔peer shape for their respective
  providers.

The password/key each provider needs is fetched from OpenBao at the `*_ref` path, never from
NetBox.

## 5. Verification owed (cannot run offline — no NetBox env in the build host)

The full NetBox Django test run and `makemigrations netbox_federation --check --dry-run` require a
live NetBox and are **owed**, not yet run here. `python -m py_compile` passes on every module.
Re-confirm against the pinned NetBox 4.6:

- the `FederationRealm.service_instance` FK target serializes (`netbox_services.serviceinstance`)
  and the migration `dependencies` resolve;
- the `ServiceInstanceSerializer` import path (`netbox_services.api.serializers`) is stable;
- run `python /opt/netbox/app/netbox/manage.py test netbox_federation --keepdb -v2` green.

Open deep-work items are tracked in `todo.json` (live migration verification, deploy + backfill,
the seeder, and consumer wiring).
