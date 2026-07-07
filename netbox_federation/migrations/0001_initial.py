# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored initial migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_federation --check --dry-run   (on a dev/ephemeral NetBox)
# Re-confirm against the pinned NetBox 4.6: the FederationRealm.service_instance FK target
# (netbox_services.serviceinstance) serializes and the FederationPeer unique constraint resolves.
# No dcim/virtualization FK is used — those apps appear only to fix migration ordering for tags.
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models

_BASE = [
    ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
    ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
    ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
    ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
]
_TAGS = ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag"))


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
        # FederationRealm.service_instance FKs netbox_services.ServiceInstance — its table must exist.
        ("netbox_services", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="FederationRealm",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=100, unique=True)),
                ("protocol", models.CharField(max_length=32)),
                ("server_name", models.CharField(max_length=255)),
                ("well_known_url", models.URLField(blank=True)),
                ("entity_id", models.CharField(blank=True, max_length=255)),
                ("signing_key_ref", models.CharField(blank=True, max_length=255)),
                ("open_federation", models.BooleanField(default=False)),
                ("service_instance", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="federation_realms", to="netbox_services.serviceinstance")),
                _TAGS,
            ],
            options={"verbose_name": "Federation Realm", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="FederationPeer",
            fields=[
                *_BASE,
                ("peer_domain", models.CharField(max_length=255)),
                ("peer_endpoint", models.URLField(blank=True)),
                ("direction", models.CharField(default="bidirectional", max_length=16)),
                ("trust_level", models.CharField(default="full", max_length=16)),
                ("shared_secret_ref", models.CharField(blank=True, max_length=255)),
                ("metadata_url", models.URLField(blank=True)),
                ("realm", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="peers", to="netbox_federation.federationrealm")),
                _TAGS,
            ],
            options={
                "verbose_name": "Federation Peer",
                "ordering": ["realm", "peer_domain"],
                "constraints": [models.UniqueConstraint(fields=("realm", "peer_domain"), name="netbox_federation_federationpeer_unique_realm_peer")],
            },
        ),
    ]
