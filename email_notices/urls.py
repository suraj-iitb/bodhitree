from django.urls import include, path
from rest_framework import routers

from .api import EmailViewSet


app_name = "email_notices"

router = routers.DefaultRouter()
router.register(r"email_notices", EmailViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
