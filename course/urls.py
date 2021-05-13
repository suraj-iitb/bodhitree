from django.urls import include, path
from rest_framework import routers

from .api import (
    AnnouncementViewSet,
    ChapterViewSet,
    CourseHistoryViewSet,
    CourseViewSet,
    PageViewSet,
    ScheduleViewSet,
    SectionViewSet,
)


app_name = "course"

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"coursehistories", CourseHistoryViewSet)
router.register(r"chapters", ChapterViewSet)
router.register(r"sections", SectionViewSet)
router.register(r"pages", PageViewSet)
router.register(r"announcements", AnnouncementViewSet)
router.register(r"schedules", ScheduleViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
