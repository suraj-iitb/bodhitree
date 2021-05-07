from django.urls import include, path
from rest_framework import routers

from .api import CribReplyViewSet, CribViewSet


app_name = "cribs"

router = routers.DefaultRouter()
router.register(r"cribs", CribViewSet)
router.register(r"cribreplies", CribReplyViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
