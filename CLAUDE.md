# netbox-federation — Agent Operating Guide

Adapted from the sibling `../netbox-database` / `../netbox-services` plugins (same engineering +
test discipline), re-targeted to the **federation relationship layer**.

`netbox-federation` is an **AGPL-3.0** NetBox 4.6 plugin: the **native source of truth for
cross-service / cross-org federation** — the local services that participate in a federation
(`FederationRealm`) and the remote peers / trust relationships they hold (`FederationPeer`),
expressed uniformly across the federation protocols the lab runs: Matrix S2S, Nextcloud federated
sharing, SAML / OIDC identity federation, ActivityPub, and XMPP S2S. It is what the `tofu-matrix` /
`tofu-nextcloud` / `tofu-authentik` providers read. See **DESIGN.md** for the full data model, the
compose boundary, and verification owed.

**It composes `netbox-services`, it does not re-model it (the netbox-ai pattern):** a federated
realm is (optionally) a `netbox_services.ServiceInstance` — `FederationRealm` **FKs** it, so
`required_plugins = ["netbox_services"]` and the migration depends on `netbox_services.0001_initial`.

**Secret policy (load-bearing):** a federation signing key or peering shared secret is **never** a
field here. `FederationRealm.signing_key_ref` and `FederationPeer.shared_secret_ref` are **OpenBao
path** references (the netbox-services convention). NetBox holds the structure; OpenBao holds the
secret.

---

## Key Directives / Rules

### DO, ALWAYS:
- If functionality won't work without a parameter, make it a **required positional** parameter.
- Any time you modify a source file, ensure its accompanying test under `netbox_federation/tests/`
  contains **comprehensive tests for the change WITHOUT MOCKS**, so `manage.py test
  netbox_federation` discovers them, and update any `.md` in the same directory that references it.
- Write concise code (avoid obvious comments; one-liners where possible).
- **SPDX header on every source file**: `# SPDX-License-Identifier: AGPL-3.0-or-later`.

### DO NOT, EVER, UNDER ANY CIRCUMSTANCE:
- Make assumptions, or answer with "is likely", "probably", or "might be".
- Store a signing key, shared secret, or any secret value in a model field. Only OpenBao path
  references (`signing_key_ref`, `shared_secret_ref`).
- Duplicate `netbox_services` catalog/instance/HA models — FK / reference them.
- Use frame-local or thread-local state instead of passing data via parameters.
- Skip a failing test; keep a broken path as a fallback; or re-implement a function in a second
  location to bypass the original. No bandaid fixes.
- **Mock the database, the ORM, the NetBox API test client, or any integration path.** Tests run
  against a **real test database** with real `FederationRealm` / `FederationPeer` /
  `netbox_services.ServiceInstance` rows.

### Python / Django Guidelines:
- Import children of `datetime`: `from datetime import date` — never `import datetime`.
- Package-relative imports inside `netbox_federation` (`from .models import FederationRealm`);
  sibling use the real path (`from netbox_services.api.serializers import ServiceInstanceSerializer`).
- FKs to sibling models in `models.py` use **string labels** (`"netbox_services.ServiceInstance"`)
  — never import them there.
- Models inherit `netbox.models.NetBoxModel` (custom fields, tags, journaling, GraphQL — free).

---

## Architecture (NetBox 4.6 plugin)

| File | Responsibility |
|------|----------------|
| `__init__.py` | `PluginConfig` — name `netbox_federation`, `base_url='federation'`, min/max 4.6, `required_plugins=["netbox_services"]` |
| `choices.py` | `ChoiceSet`s: `FederationProtocolChoices`, `FederationDirectionChoices`, `TrustLevelChoices` |
| `models.py` | `FederationRealm` + `FederationPeer` |
| `migrations/0001_initial.py` | hand-authored (NetBox disables makemigrations in prod); verify with `makemigrations --check --dry-run`; deps: dcim, extras, netbox_services (no virtualization — no VM FK) |
| `api/serializers.py`, `api/views.py`, `api/urls.py` | REST (`NetBoxModelViewSet`, `NetBoxRouter`) — the contract the providers + seeder read; nests the netbox_services serializer |
| `filtersets.py` | `NetBoxModelFilterSet` per model (explicit `<fk>_id` + `search()`) |
| `tables.py`, `forms.py`, `navigation.py`, `views.py`, `urls.py` | UI (generic NetBox views; `_routes()` helper; PluginMenu group Federation) |
| `graphql/__init__.py` | placeholder (auto GraphQL via `NetBoxModel`) |

### Model — realm + peer
- **FederationRealm**: `name`(unique)·`protocol`·`server_name`·`well_known_url`·`entity_id`·
  `signing_key_ref`(OpenBao path)·`open_federation`; optional `service_instance`
  ("netbox_services.ServiceInstance", SET_NULL).
- **FederationPeer** (FK realm): `peer_domain`·`peer_endpoint`·`direction`·`trust_level`·
  `shared_secret_ref`(OpenBao path)·`metadata_url`; unique `(realm, peer_domain)`.

---

## Testing (NO MOCKS — real DB, NetBox test framework)

- Tests live in `netbox_federation/tests/` (`test_models.py`, `test_api.py`, `test_filtersets.py`).
  Build real realms via a `make_realm`/`_realm` helper; peers hang off a shared realm.
- `test_models` covers str/colors + the `(realm, peer_domain)` uniqueness constraint + cascade +
  the secret-ref-is-a-path policy; `test_api` runs the CRUD mixins per model; `test_filtersets`
  covers FK-id scoping, choice filters, and `search()`.
- **Run**: `python /opt/netbox/app/netbox/manage.py test netbox_federation --keepdb -v2`.
- **Verification owed (cannot run offline — no NetBox env in the build host):**
  `makemigrations netbox_federation --check --dry-run` on an ephemeral NetBox, and a full test run.
  Re-confirm against the pinned NetBox 4.6: the `netbox_services.serviceinstance` FK serialization,
  the migration `dependencies`, and the `netbox_services.api.serializers.ServiceInstanceSerializer`
  import path. `py_compile` passes on every module today.
- **Never skip a failing test** — fix the root cause.

---

## Licensing
- **AGPL-3.0-or-later** (workspace production-IaC standard). SPDX header in every file.
