# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem


def _item(model, label):
    return PluginMenuItem(
        link=f"plugins:netbox_federation:{model}_list",
        link_text=label,
        buttons=[
            PluginMenuButton(f"plugins:netbox_federation:{model}_add", "Add", "mdi mdi-plus-thick")
        ],
    )


menu = PluginMenu(
    label="Federation",
    groups=(
        (
            "Federation",
            (
                _item("federationrealm", "Federation Realms"),
                _item("federationpeer", "Federation Peers"),
            ),
        ),
    ),
    icon_class="mdi mdi-transit-connection-variant",
)
