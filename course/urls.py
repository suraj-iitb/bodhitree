from django.urls import include, path
from rest_framework import routers

from .api import ChapterViewSet, CourseHistoryViewSet, CourseViewSet


app_name = "course"

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"coursehistories", CourseHistoryViewSet)
router.register(r"chapter", ChapterViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
