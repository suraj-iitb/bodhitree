from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from utils.drf_utils import IsInstructorOrTA, IsInstructorOrTAOrReadOnly

from .models import Chapter, Course, CourseHistory
from .serializers import ChapterSerializer, CourseHistorySerializer, CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsInstructorOrTAOrReadOnly,)
    filterset_fields = (
        "owner__email",
        "code",
        "title",
        "course_type",
    )
    search_fields = (
        "owner__email",
        "code",
        "title",
        "course_type",
    )
    ordering_fields = ("id",)


class CourseHistoryViewSet(viewsets.ModelViewSet):
    queryset = CourseHistory.objects.all()
    serializer_class = CourseHistorySerializer
    permission_classes = (AllowAny,)
    filterset_fields = (
        "user__email",
        "course__title",
        "role",
        "status",
    )
    search_fields = (
        "user__email",
        "course__title",
        "role",
        "status",
    )
    ordering_fields = ("id",)


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = (IsInstructorOrTA,)
    filterset_fields = (
        "course__title",
        "title",
    )
    search_fields = (
        "course__title",
        "title",
    )
    ordering_fields = ("id",)
