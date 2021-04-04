from django.urls import include, path
from rest_framework import routers

from .api import CourseViewSet


app_name = "course"


router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
