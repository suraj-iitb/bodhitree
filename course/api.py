import logging

from django.db import IntegrityError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from registration.models import SubscriptionHistory
from utils import mixins as custom_mixins
from utils.pagination import StandardResultsSetPagination
from utils.permissions import (
    IsInstructorOrTA,
    IsInstructorOrTAOrReadOnly,
    IsInstructorOrTAOrStudent,
    IsOwner,
)
from utils.subscription import SubscriptionView

from .models import Announcement, Chapter, Course, CourseHistory, Page, Section
from .serializers import (
    AnnouncementSerializer,
    ChapterSerializer,
    CourseHistorySerializer,
    CourseSerializer,
    PageSerializer,
    SectionSerializer,
)


logger = logging.getLogger(__name__)


class CourseViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    custom_mixins.UpdateMixin,
    custom_mixins.DeleteMixin,
):
    """ViewSet for `Course`."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsInstructorOrTAOrReadOnly,)
    pagination_class = StandardResultsSetPagination
    filterset_fields = (
        "owner__email",
        "code",
        "title",
        "is_published",
    )
    search_fields = (
        "owner__email",
        "code",
        "title",
        "is_published",
    )

    def _create_course_check(self, user):
        """Checks if the user can create a course.

        Args:
            user (User): `User` model object

        Returns:
            A bool value representing whether the user can create a course or not.

        Raises:
            `HTTP_403_FORBIDDEN`: Raised if:
                1. The course limit of the subscription is reached.
                2. `SubscriptionHistory.DoesNotExist` exception
        """
        try:
            if not SubscriptionView.is_course_limit_reached(user):
                return True

            error = "For user: `{}`, the limit of number of courses reached.".format(
                user
            )
            logger.warning(error)
            return Response(error, status.HTTP_403_FORBIDDEN)
        except SubscriptionHistory.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_403_FORBIDDEN)

    def _update_course_check(self, course_id, user):
        """Checks if the user can update a course.

        Args:
            course_id: Course id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user can update a course or not.

        Raises:
            `HTTP_404_NOT_FOUND`: Raised by `Course.DoesNotExist` exception
            `HTTP_403_FORBIDDEN`: Raised if the subscription is not valid
        """
        try:
            course = Course.objects.select_related("owner").get(id=course_id)
        except Course.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        if SubscriptionView.has_valid_subscription(course.owner):
            return True

        error = "User: `{}` is not permitted to update the course: `{}`.".format(
            user, course
        )
        logger.warning(error)
        return Response(error, status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=["POST"])
    def create_course(self, request):
        """Adds a course.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created course data and status `HTTP_201_CREATED`.

        Raises:
            `HTTP_400_BAD_REQUEST`: Raised due to serialization errors
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrReadOnly` permission
                class
            HTTP_403_FORBIDDEN: Raised by:
                1. `IntegrityError` of the database
                2. `_create_course_check()` method
        """
        user = request.user
        check = self._create_course_check(user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            course_history = CourseHistory(
                user=user, course=serializer.instance, role="I", status="E"
            )
            course_history.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_course(self, request, pk):
        """Updates a course with id as pk

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with the updated course data and status `HTTP_200_OK`.

        Raises:
            `HTTP_400_BAD_REQUEST`: Raised due to serialization errors
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrReadOnly` permission
                class
            `HTTP_403_FORBIDDEN`: Raised by:
                1.  `IsInstructorOrTAOrReadOnly` permission class
                2. `IntegrityError` of the database
                3. `_update_course_check()` method
            HTTP_404_NOT_FOUND: Raise by `_update_course_check()` method
        """
        check = self._update_course_check(pk, request.user)
        if check is not True:
            return check

        return self.update(request, pk)

    @action(detail=True, methods=["DELETE"], permission_classes=[IsOwner])
    def delete_course(self, request, pk):
        """Deletes the course with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsOwner` permission class
            `HTTP_403_FORBIDDEN`: Raised by `IsOwner` permission class
        """
        return self._delete(request, pk)


class CourseHistoryViewSet(
    viewsets.GenericViewSet,
    custom_mixins.RegisteredListMixin,
    custom_mixins.CreateMixin,
    custom_mixins.RetrieveMixin,
    custom_mixins.UpdateMixin,
):
    """ViewSet for `CourseHistory`."""

    queryset = CourseHistory.objects.all()
    serializer_class = CourseHistorySerializer
    permission_classes = (IsInstructorOrTAOrStudent,)
    pagination_class = StandardResultsSetPagination

    def get_queryset_list(self, course_id):
        queryset = CourseHistory.objects.filter(course=course_id)
        return queryset

    @action(detail=False, methods=["POST"])
    def create_course_history(self, request):
        """Adds a course history for a course

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created course history data and status
            `HTTP_201_CREATED`.

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrStudent` permission
                class
        """
        course_id = request.data["course"]
        try:
            Course.objects.get(id=course_id)
        except Course.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)
        return self.create(request)

    @action(detail=True, methods=["GET"])
    def list_course_histories(self, request, pk):
        """Gets all the course history in the course with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the course histories data and status `HTTP_200_OK`.

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrStudent` permission
                class
        """
        return self.list(request, pk)

    @action(detail=True, methods=["GET"])
    def retrieve_course_history(self, request, pk):
        """Gets the course history with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course history id

        Returns:
            `Response` with the course history data and status `HTTP_200_OK`.

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsInstructorOrTAOrStudent` permission
                class
            `HTTP_403_FORBIDDEN`: Raised by `IsInstructorOrTAOrStudent` permission class
            `HTTP_404_NOT_FOUND`: Raised by `get_object()` method
        """
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"], permission_classes=[IsOwner])
    def update_course_history(self, request, pk):
        """Updates the course history with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course history id

        Returns:
            `Response` with the updated course history data and status `HTTP_200_OK`.

        Raises:
            `HTTP_401_UNAUTHORIZED`: Raised by `IsOwner` permission class
            `HTTP_403_FORBIDDEN`: Raised by:
                1. `IsOwner` permission class
                2. `IntegrityError` of the database
        """
        return self.update(request, pk)


class ChapterViewSet(
    viewsets.GenericViewSet,
    custom_mixins.InsOrTACreateMixin,
    custom_mixins.RetrieveMixin,
    custom_mixins.RegisteredListMixin,
    custom_mixins.DeleteMixin,
    custom_mixins.UpdateMixin,
):
    """Viewset for `Chapter`."""

    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = (IsInstructorOrTA,)

    def get_queryset_list(self, course_id):
        queryset = Chapter.objects.filter(course=course_id)
        return queryset

    @action(detail=False, methods=["POST"])
    def create_chapter(self, request):
        course_id = request.data["course"]
        return self.create(request, course_id)

    @action(detail=True, methods=["GET"])
    def list_chapters(self, request, pk):
        return self.list(request, pk)

    @action(detail=True, methods=["GET"])
    def retrieve_chapter(self, request, pk):
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_chapter(self, request, pk):
        return self.update(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_chapter(self, request, pk):
        return self._delete(request, pk)


class SectionViewSet(
    viewsets.GenericViewSet,
    custom_mixins.InsOrTACreateMixin,
    custom_mixins.ListMixin,
    custom_mixins.RetrieveMixin,
    custom_mixins.UpdateMixin,
    custom_mixins.DeleteMixin,
):
    """Viewset for `Section`."""

    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = (IsInstructorOrTA,)

    def get_queryset_list(self, chapter_id):
        queryset = Section.objects.filter(chapter_id=chapter_id)
        return queryset

    @action(detail=False, methods=["POST"])
    def create_section(self, request):
        """Adds a section to the chapter.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created section data and status HTTP_201_CREATED.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `_is_instructor_or_ta()` permission class
            HTTP_404_NOT_FOUND: Raised if the chapter does not exist
        """
        chapter_id = request.data["chapter"]

        try:
            chapter = Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)
        course_id = chapter.course_id

        # This is specifically done during section creation (not during updation or
        # deletion) because it can't be handled by `IsInstructorOrTA` permission class
        return self.create(request, course_id)

    @action(detail=True, methods=["GET"])
    def list_sections(self, request, pk):
        """Gets all the sections in the chapter with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Chapter id

        Returns:
            `Response` with all the sections data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised if the chapter does not exist
        """
        try:
            chapter = Chapter.objects.get(id=pk)
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)
        course_id = chapter.course_id

        # This is specifically done during list all sections (not during retrieval of
        # a section) because it can't be handled by `IsInstructorOrTA` permission class.
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check
        return self.list(request, pk)

    @action(detail=True, methods=["GET"])
    def retrieve_section(self, request, pk):
        """Gets the section with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Section id

        Returns:
            `Response` with the section data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
        """
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_section(self, request, pk):
        """Updates the section with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Section id

        Returns:
            `Response` with the updated section data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
        """
        return self.update(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_section(self, request, pk):
        """Deletes the section with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Section id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
        """
        return self._delete(request, pk)


class PageViewSet(
    viewsets.GenericViewSet,
    custom_mixins.InsOrTACreateMixin,
    custom_mixins.RetrieveMixin,
    custom_mixins.RegisteredListMixin,
    custom_mixins.DeleteMixin,
    custom_mixins.UpdateMixin,
):
    """Viewset for `Page`."""

    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsInstructorOrTA,)

    def get_queryset_list(self, course_id):
        queryset = Page.objects.filter(course=course_id)
        return queryset

    @action(detail=False, methods=["POST"])
    def create_page(self, request):
        course_id = request.data["course"]
        return self.create(request, course_id)

    @action(detail=True, methods=["GET"])
    def list_pages(self, request, pk):
        return self.list(request, pk)

    @action(detail=True, methods=["GET"])
    def retrieve_page(self, request, pk):
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_page(self, request, pk):
        return self.update(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_page(self, request, pk):
        return self._delete(request, pk)


class AnnouncementViewSet(
    viewsets.GenericViewSet,
    custom_mixins.InsOrTACreateMixin,
    custom_mixins.RetrieveMixin,
    custom_mixins.RegisteredListMixin,
    custom_mixins.DeleteMixin,
    custom_mixins.UpdateMixin,
):
    """Viewset for `Announcement`."""

    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = (IsInstructorOrTA,)

    def get_queryset_list(self, course_id):
        queryset = Announcement.objects.filter(course=course_id)
        return queryset

    @action(detail=False, methods=["POST"])
    def create_announcement(self, request):
        course_id = request.data["course"]
        return self.create(request, course_id)

    @action(detail=True, methods=["GET"])
    def list_announcements(self, request, pk):
        return self.list(request, pk)

    @action(detail=True, methods=["GET"])
    def retrieve_announcement(self, request, pk):
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_announcement(self, request, pk):
        return self.update(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_announcement(self, request, pk):
        return self._delete(request, pk)
