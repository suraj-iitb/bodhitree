from rest_framework import mixins, status, viewsets
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


class PageViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsInstructorOrTA,)
    pagination_class = None

    @action(detail=True, methods=["POST"])
    def add_page(self, request, pk):
        """Add a page to a course with primary key as pk"""
        if check_course_registration(pk, request.user) is False:
            data = {
                "error": "User: {} not registered in Course with id: {}".format(
                    request.user, pk
                )
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        try:
            Course.objects.get(id=pk)
        except Course.DoesNotExist:
            data = {"error": "Course with id: {} does not exist".format(pk)}
            return Response(data, status.HTTP_400_BAD_REQUEST)
        serializer = PageSerializer(data=request.data)
        if serializer.is_valid():
            page = serializer.save()
            return Response(PageSerializer(page).data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"])
    def list_pages(self, request, pk):
        """Get all pages of a course with primary key as pk"""
        if check_course_registration(pk, request.user) is False:
            data = {
                "error": "User: {} not registered in Course with id: {}".format(
                    request.user, pk
                )
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        try:
            Course.objects.get(id=pk)
        except Course.DoesNotExist:
            data = {"error": "Course with id: {} does not exist".format(pk)}
            return Response(data, status.HTTP_400_BAD_REQUEST)
        pages = Page.objects.filter(course_id=pk)
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def page_retrieve(self, request, pk):
        """Get 1 page of a course with primary key as pk"""
        if check_course_registration(pk, request.user) is False:
            data = {
                "error": "User: {} not registered in Course with id: {}".format(
                    request.user, pk
                )
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        try:
            Course.objects.get(id=pk)
        except Course.DoesNotExist:
            data = {"error": "Course with id: {} does not exist".format(pk)}
            return Response(data, status.HTTP_400_BAD_REQUEST)
        pages = Page.objects.filter(course_id=pk)
        serializer = PageSerializer(pages)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT"])
    def update_page(self, request, pk):
        """Update page of a course with page primary key as pk"""
        page = Page.objects.get(id=pk)
        course_id = page.course.id
        if check_course_registration(course_id, request.user) is False:
            data = {
                "error": "User: {} not registered in Course with id: {}".format(
                    request.user, course_id
                )
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        try:
            Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            data = {"error": "Course with id: {} does not exist".format(course_id)}
            return Response(data, status.HTTP_400_BAD_REQUEST)
        serializer = PageSerializer(page, data=request.data)
        if serializer.is_valid():
            page = serializer.save()
            return Response(PageSerializer(page).data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"])
    def partial_update_page(self, request, pk):
        """Partial update page of a course with page primary key as pk"""
        page = Page.objects.get(id=pk)
        course_id = page.course.id
        if check_course_registration(course_id, request.user) is False:
            data = {
                "error": "User: {} not registered in Course with id: {}".format(
                    request.user, course_id
                )
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        try:
            Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            data = {"error": "Course with id: {} does not exist".format(course_id)}
            return Response(data, status.HTTP_400_BAD_REQUEST)
        serializer = PageSerializer(page, data=request.data, partial=True)
        if serializer.is_valid():
            page = serializer.save()
            return Response(PageSerializer(page).data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["DELETE"])
    def destroy_page(self, request, pk):
        """Delete page of a course with page primary key as pk"""
        try:
            page = Page.objects.get(id=pk)
        except Page.DoesNotExist:
            data = {"error": "Page with id: {} does not exist".format(pk)}
            return Response(data, status.HTTP_400_BAD_REQUEST)
        course_id = page.course.id
        if check_course_registration(course_id, request.user) is False:
            data = {
                "error": "User: {} not registered in Course with id: {}".format(
                    request.user, course_id
                )
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        try:
            Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            data = {"error": "Course with id: {} does not exist".format(course_id)}
            return Response(data, status.HTTP_400_BAD_REQUEST)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
