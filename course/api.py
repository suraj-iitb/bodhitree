from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from utils.drf_utils import IsInstructorOrTA, IsInstructorOrTAOrReadOnly
from utils.utils import check_course_registration

from .models import Chapter, Course, CourseHistory, Page
from .serializers import (
    ChapterSerializer,
    CourseHistorySerializer,
    CourseSerializer,
    PageSerializer,
)


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


class PageViewSet(viewsets.GenericViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsInstructorOrTA,)
    pagination_class = None

    def _checks(self, course_id, user):
        """To check if the user is registered in a given course"""
        try:
            Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            data = {
                "error": "Course with id: {} does not exist".format(course_id),
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)

        if check_course_registration(course_id, user) is False:
            data = {
                "error": "User: {} not registered in course with id: {}".format(
                    user, course_id
                ),
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        return True

    def _get_page(self, page_id):
        """Get page if it exists"""
        try:
            page = Page.objects.get(id=page_id)
            return page
        except Page.DoesNotExist:
            data = {"error": "Page with id: {} does not exist".format(page_id)}
            return Response(data, status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["POST"])
    def add_page(self, request, pk):
        """Add a page to a course with primary key as pk"""
        check = self._checks(pk, request.user)
        if check is True:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return check

    @action(detail=True, methods=["GET"])
    def list_pages(self, request, pk):
        """Get all pages of a course with primary key as pk"""
        check = self._checks(pk, request.user)
        if check is True:
            pages = Page.objects.filter(course_id=pk)
            serializer = self.get_serializer(pages, many=True)
            return Response(serializer.data)
        return check

    @action(detail=True, methods=["GET"])
    def retrieve_page(self, request, pk):
        """Get a page with primary key as pk"""
        page = self._get_page(pk)
        if type(page) != Page:
            return page
        check = self._checks(page.course.id, request.user)
        if check is True:
            serializer = self.get_serializer(page)
            return Response(serializer.data)
        return check

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_page(self, request, pk):
        """Update page with primary key as pk"""
        page = self._get_page(pk)
        if type(page) != Page:
            return page
        check = self._checks(page.course.id, request.user)
        if check is True:
            serializer = self.get_serializer(page, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        return check

    @action(detail=True, methods=["DELETE"])
    def delete_page(self, request, pk):
        """Delete page with primary key as pk"""
        page = self._get_page(pk)
        if type(page) != Page:
            return page
        check = self._checks(page.course.id, request.user)
        if check is True:
            page.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return check


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
