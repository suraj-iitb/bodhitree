from django.urls import include, path
from rest_framework import routers

from .api import VideoViewSet


app_name = "video"

router = routers.DefaultRouter()
router.register(r"videos", VideoViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
