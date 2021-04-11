from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from discussion_forum.models import DiscussionForum
from utils.drf_utils import IsInstructorOrTA, IsInstructorOrTAOrReadOnly
from utils.utils import (
    check_course_registration,
    has_valid_subscription,
    is_instructor_or_ta,
)

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

    def create(self, request):
        user = request.user
        data = request.data.copy()
        anonymous_to_instructor = data.pop("anonymous_to_instructor", True)
        send_email_to_all = data.pop("send_email_to_all", False)
        if not has_valid_subscription(user):
            data = {
                "error": "User: {} does not have a valid subscription or the"
                "limit of number of courses in subscription exceeded".format(user),
            }
            return Response(data, status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            course_history = CourseHistory(
                user=user, course=serializer.instance, role="I", status="E"
            )
            course_history.save()
            discussion_forum = DiscussionForum(
                course=serializer.instance,
                anonymous_to_instructor=anonymous_to_instructor,
                send_email_to_all=send_email_to_all,
            )
            discussion_forum.save()
            return Response({}, status=status.HTTP_201_CREATED)


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

        if not check_course_registration(course_id, user):
            data = {
                "error": "User: {} not registered in course with id: {}".format(
                    user, course_id
                ),
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        return True

    @action(detail=True, methods=["POST"])
    def add_page(self, request, pk):
        """Add a page to a course with primary key as pk"""
        user = request.user
        instructor_or_ta = is_instructor_or_ta(pk, user)
        if not instructor_or_ta:
            data = {
                "error": "User: {} is not instructor/ta of course with id: {}".format(
                    user, pk
                ),
            }
            return Response(data, status.HTTP_401_UNAUTHORIZED)
        check = self._checks(pk, user)
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
        page = self.get_object()
        check = self._checks(page.course.id, request.user)
        if check is True:
            serializer = self.get_serializer(page)
            return Response(serializer.data)
        return check

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_page(self, request, pk):
        """Update page with primary key as pk"""
        page = self.get_object()
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
        page = self.get_object()
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
