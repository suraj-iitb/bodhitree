from django.urls import include, path
from rest_framework import routers

from .api import UserViewSet


app_name = "registration"


router = routers.DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
