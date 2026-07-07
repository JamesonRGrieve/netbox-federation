# SPDX-License-Identifier: AGPL-3.0-or-later
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from .choices import FederationDirectionChoices, FederationProtocolChoices, TrustLevelChoices
from .models import FederationPeer, FederationRealm


class FederationRealmForm(NetBoxModelForm):
    fieldsets = (
        FieldSet("name", "protocol", "server_name", name="Realm"),
        FieldSet("service_instance", "well_known_url", "entity_id", name="Identity / discovery"),
        FieldSet("signing_key_ref", "open_federation", name="Signing / policy"),
    )

    class Meta:
        model = FederationRealm
        fields = ["name", "protocol", "server_name", "service_instance", "well_known_url",
                  "entity_id", "signing_key_ref", "open_federation", "tags"]


class FederationPeerForm(NetBoxModelForm):
    realm = DynamicModelChoiceField(queryset=FederationRealm.objects.all())

    fieldsets = (
        FieldSet("realm", "peer_domain", "peer_endpoint", name="Peer"),
        FieldSet("direction", "trust_level", name="Trust"),
        FieldSet("shared_secret_ref", "metadata_url", name="Secret / metadata"),
    )

    class Meta:
        model = FederationPeer
        fields = ["realm", "peer_domain", "peer_endpoint", "direction", "trust_level",
                  "shared_secret_ref", "metadata_url", "tags"]


class FederationRealmFilterForm(NetBoxModelFilterSetForm):
    model = FederationRealm
    protocol = forms.MultipleChoiceField(choices=FederationProtocolChoices, required=False)
    open_federation = forms.NullBooleanField(required=False)
    tag = TagFilterField(FederationRealm)


class FederationPeerFilterForm(NetBoxModelFilterSetForm):
    model = FederationPeer
    realm_id = DynamicModelMultipleChoiceField(queryset=FederationRealm.objects.all(), required=False, label="Realm")
    direction = forms.MultipleChoiceField(choices=FederationDirectionChoices, required=False)
    trust_level = forms.MultipleChoiceField(choices=TrustLevelChoices, required=False)
    tag = TagFilterField(FederationPeer)
