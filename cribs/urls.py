from django.urls import include, path
from rest_framework import routers

from .api import CribViewSet


app_name = "cribs"

router = routers.DefaultRouter()
router.register(r"cribs", CribViewSet)


urlpatterns = [
    path("api/", include(router.urls)),
]
