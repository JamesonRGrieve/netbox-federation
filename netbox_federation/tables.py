# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import FederationPeer, FederationRealm


class FederationRealmTable(NetBoxTable):
    name = tables.Column(linkify=True)
    protocol = columns.ChoiceFieldColumn()
    service_instance = tables.Column(linkify=True)
    open_federation = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_federation:federationrealm_list")

    class Meta(NetBoxTable.Meta):
        model = FederationRealm
        fields = ("pk", "id", "name", "protocol", "server_name", "service_instance", "well_known_url",
                  "entity_id", "signing_key_ref", "open_federation", "tags", "created", "last_updated")
        default_columns = ("name", "protocol", "server_name", "open_federation")


class FederationPeerTable(NetBoxTable):
    realm = tables.Column(linkify=True)
    peer_domain = tables.Column(linkify=True)
    direction = columns.ChoiceFieldColumn()
    trust_level = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_federation:federationpeer_list")

    class Meta(NetBoxTable.Meta):
        model = FederationPeer
        fields = ("pk", "id", "realm", "peer_domain", "peer_endpoint", "direction", "trust_level",
                  "shared_secret_ref", "metadata_url", "tags", "created", "last_updated")
        default_columns = ("realm", "peer_domain", "direction", "trust_level")
