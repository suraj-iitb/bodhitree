from django.urls import include, path
from rest_framework import routers

from .api import ChapterViewSet, CourseHistoryViewSet, CourseViewSet, PageViewSet


app_name = "course"

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"coursehistories", CourseHistoryViewSet)
router.register(r"chapters", ChapterViewSet)
router.register(r"pages", PageViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
