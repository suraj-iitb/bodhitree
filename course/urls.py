from django.urls import include, path
from rest_framework import routers

from .api import CourseHistoryViewSet, CourseViewSet, PageViewSet, SectionViewSet


app_name = "course"

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"coursehistories", CourseHistoryViewSet)
router.register(r"sections", SectionViewSet)
router.register(r"pages", PageViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
