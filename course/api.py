from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from utils.drf_utils import IsInstructorOrTA, IsInstructorOrTAOrReadOnly, Isowner
from utils.utils import (
    check_course_registration,
    has_valid_subscription,
    is_instructor_or_ta,
)

from .models import Chapter, Course, CourseHistory, Page, Section
from .serializers import (
    ChapterSerializer,
    CourseHistorySerializer,
    CourseSerializer,
    PageSerializer,
    SectionSerializer,
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

    def valid_subscription(self, user):
        if has_valid_subscription(user):
            return True
        else:
            data = {
                "error": """User: {} does not have a valid subscription or the
                limit of number of courses in subscription exceeded""".format(
                    user
                ),
            }
            return Response(data, status.HTTP_403_FORBIDDEN)

    def _checks(self, course_id, user):
        course = get_object_or_404(Course, id=course_id)
        if self.valid_subscription(course.owner):
            return True
        elif CourseHistory.objects.filter(Q(role="I") | Q(role="T")):
            if not check_course_registration(course_id, user):
                data = {
                    "error": "User: {} not registered in course with id: {}".format(
                        user, course_id
                    ),
                }
                return Response(data, status.HTTP_401_UNAUTHORIZED)
        return True

    def create(self, request):
        user = request.user
        data = request.data
        _check = self.valid_subscription(user)
        if _check is True:
            serializer = self.get_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                course_history = CourseHistory(
                    user=user, course=serializer.instance, role="I", status="E"
                )
                course_history.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return _check

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_course(self, request, pk):
        user = request.user
        data = request.data
        check = self._checks(pk, user)
        if check:
            serializer = self.get_serializer(self.get_object(), data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        return check

    @action(detail=True, methods=["DELETE"], permission_classes=[Isowner])
    def delete_course(self, request, pk):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class ChapterViewSet(viewsets.GenericViewSet):
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
    def create_chapter(self, request, pk):
        """Add a chapter to a course with primary key as pk"""
        user = request.user
        instructor_or_ta = is_instructor_or_ta(pk, user)
        if not instructor_or_ta:
            data = {
                "error": "User: {} is not instructor/ta of course with id: {}".format(
                    user, pk
                ),
            }
            return Response(data, status.HTTP_403_FORBIDDEN)
        check = self._checks(pk, user)
        if check is True:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                serializer.save()
            except IntegrityError:
                error = {
                    "error": "Chapter with title '{}' already exists".format(
                        serializer.initial_data["title"]
                    )
                }
                return Response(error, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return check

    @action(detail=True, methods=["GET"])
    def list_chapters(self, request, pk):
        """Get all chapters of a course with primary key as pk"""
        check = self._checks(pk, request.user)
        if check is True:
            chapters = Chapter.objects.filter(course_id=pk)
            serializer = self.get_serializer(chapters, many=True)
            return Response(serializer.data)
        return check

    @action(detail=True, methods=["GET"])
    def retrieve_chapter(self, request, pk):
        """Get a chapter with primary key as pk"""
        chapter = self.get_object()
        check = self._checks(chapter.course.id, request.user)
        if check is True:
            serializer = self.get_serializer(chapter)
            return Response(serializer.data)
        return check

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_chapter(self, request, pk):
        """Update chapter with primary key as pk"""
        chapter = self.get_object()
        check = self._checks(chapter.course.id, request.user)
        if check is True:
            serializer = self.get_serializer(chapter, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                try:
                    serializer.save()
                except IntegrityError:
                    error = {
                        "error": "Chapter with title '{}' already exists".format(
                            serializer.initial_data["title"]
                        )
                    }
                    return Response(error, status=status.HTTP_403_FORBIDDEN)
                return Response(serializer.data)
        return check

    @action(detail=True, methods=["DELETE"])
    def delete_chapter(self, request, pk):
        """Delete chapter with primary key as pk"""
        chapter = self.get_object()
        check = self._checks(chapter.course.id, request.user)
        if check is True:
            chapter.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return check


class SectionViewSet(viewsets.GenericViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = (IsInstructorOrTA,)
    filterset_fields = (
        "chapter__title",
        "title",
    )
    search_fields = (
        "chapter__title",
        "title",
    )
    ordering_fields = ("id",)

    def _checks(self, course_id, chapter_id, user):
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

        try:
            Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist:
            data = {
                "error": "Chapter with id: {} does not exist".format(chapter_id),
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)

        return True

    @action(detail=True, methods=["POST"])
    def create_section(self, request, pk):
        """Add a section to a chapter with primary key as pk"""
        user = request.user
        try:
            course_id = Chapter.objects.get(id=pk).course.id
        except Course.DoesNotExist:
            data = {
                "error": "Course with id: {} does not exist".format(course_id),
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        instructor_or_ta = is_instructor_or_ta(course_id, user)
        if not instructor_or_ta:
            data = {
                "error": "User: {} is not instructor/ta of course with id: {}".format(
                    user, course_id
                ),
            }
            return Response(data, status.HTTP_403_FORBIDDEN)
        check = self._checks(course_id, pk, user)
        if check is True:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                serializer.save()
            except IntegrityError:
                error = {
                    "error": "Section with title '{}' already exists".format(
                        serializer.initial_data["title"]
                    )
                }
                return Response(error, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return check

    @action(detail=True, methods=["GET"])
    def list_sections(self, request, pk):
        """Get all sections of a chapter with primary key as pk"""
        try:
            course_id = Chapter.objects.get(id=pk).course.id
        except Course.DoesNotExist:
            data = {
                "error": "Course with id: {} does not exist".format(course_id),
            }
            return Response(data, status.HTTP_400_BAD_REQUEST)
        check = self._checks(course_id, pk, request.user)
        if check is True:
            sections = Section.objects.filter(chapter_id=pk)
            serializer = self.get_serializer(sections, many=True)
            return Response(serializer.data)
        return check

    @action(detail=True, methods=["GET"])
    def retrieve_section(self, request, pk):
        """Get a section with primary key as pk"""
        section = self.get_object()
        check = self._checks(
            section.chapter.course.id, section.chapter.id, request.user
        )
        if check is True:
            serializer = self.get_serializer(section)
            return Response(serializer.data)
        return check

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_section(self, request, pk):
        """Update section with primary key as pk"""
        section = self.get_object()
        check = self._checks(
            section.chapter.course.id, section.chapter.id, request.user
        )
        if check is True:
            serializer = self.get_serializer(section, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        return check

    @action(detail=True, methods=["DELETE"])
    def delete_section(self, request, pk):
        """Delete section with primary key as pk"""
        section = self.get_object()
        check = self._checks(
            section.chapter.course.id, section.chapter.id, request.user
        )
        if check is True:
            section.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return check
