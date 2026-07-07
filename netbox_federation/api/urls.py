# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.routers import NetBoxRouter
from . import views

app_name = "netbox_federation"

router = NetBoxRouter()
router.register("realms", views.FederationRealmViewSet)
router.register("peers", views.FederationPeerViewSet)

urlpatterns = router.urls
