from django.urls import include, path
from rest_framework import routers

from .api import DocumentViewSet


app_name = "document"

router = routers.DefaultRouter()
router.register(r"documents", DocumentViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
