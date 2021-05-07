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
from utils.utils import check_course_registration, check_is_instructor_or_ta

from .models import Chapter, Course, CourseHistory, Page, Section
from .serializers import (
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
            HTTP_403_FORBIDDEN: Raised if:
                1. The course limit of the subscription is reached.
                2. The subscription plan does not exist.
        """
        try:
            if not SubscriptionView.is_course_limit_reached(user):
                return True
            data = {
                "error": "For user: {}, the limit of number of courses in "
                "subscription exceeded.".format(user),
            }
            logger.warning(data["error"])
        except SubscriptionHistory.DoesNotExist as e:
            logger.exception(e)
            data = {
                "error": "User: {} does not have a valid subscription.".format(user),
            }
        return Response(data, status.HTTP_403_FORBIDDEN)

    def _update_course_check(self, course_id, user):
        """Checks if the user can update a course.

        Args:
            course_id: course id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user can update a course or not.

        Raises:
            HTTP_404_NOT_FOUND: Raised if the course does not exist
            HTTP_403_FORBIDDEN: Raised if the subscription is not valid
        """
        try:
            course = Course.objects.select_related("owner").get(id=course_id)
        except Course.DoesNotExist as e:
            logger.exception(e)
            return Response(e, status.HTTP_404_NOT_FOUND)

        if SubscriptionView.has_valid_subscription(course.owner):
            return True
        data = {
            "error": "User: {} is not permitted to update the course: {}.".format(
                user, course
            ),
        }
        logger.warning(data["error"])
        return Response(data, status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=["POST"])
    def create_course(self, request):
        """Adds a course.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created course data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrReadOnly`
                permission class
            HTTP_403_FORBIDDEN: Raised by:
                1. `IsInstructorOrTAOrReadOnly` permission class
                2. `IntegrityError` of the database
                3. `_create_course_check()` method
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
                data = {
                    "error": "Course with code '{}' & title '{}' already exists for"
                    " you.".format(
                        serializer.initial_data["code"],
                        serializer.initial_data["title"],
                    )
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)
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
            pk (int): course id

        Returns:
            `Response` with the updated course data and status HTTP_200_OK.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrReadOnly`
                permission class
            HTTP_403_FORBIDDEN: Raised by:
                1. `IsInstructorOrTAOrReadOnly` permission class
                2. `IntegrityError` of the database
                3. `_update_course_check()` method
            HTTP_404_NOT_FOUND: Raise by `_update_course_check()` method
        """
        check = self._update_course_check(pk, request.user)
        if check is not True:
            return check

        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                data = {
                    "error": "Course with code '{}' & title '{}' already exists for"
                    " you.".format(
                        serializer.initial_data["code"],
                        serializer.initial_data["title"],
                    )
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["DELETE"], permission_classes=[IsOwner])
    def delete_course(self, request, pk):
        """Deletes the course with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): course id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsOwner` permission class
            HTTP_403_FORBIDDEN: Raised by `IsOwner` permission class
        """
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseHistoryViewSet(
    viewsets.GenericViewSet,
    custom_mixins.IsRegisteredMixin,
):
    """ViewSet for `CourseHistory`."""

    queryset = CourseHistory.objects.all()
    serializer_class = CourseHistorySerializer
    permission_classes = (IsInstructorOrTAOrStudent, IsOwner)
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=["POST"])
    def create_course_history(self, request):
        """Adds a course history.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created course history data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by:
                1. `IsInstructorOrTAOrStudent` permission class
                2. `IsOwner` permission class
            HTTP_403_FORBIDDEN: Raised by:
                1. `IsInstructorOrTAOrStudent` permission class
                2. `IsOwner` permission class
                3. `IntegrityError` of the database
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                data = {
                    "error": "Course history for the user with id: {} in the course"
                    " with id: {} exists.".format(
                        serializer.initial_data["user"],
                        serializer.initial_data["course"],
                    )
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"])
    def list_course_histories(self, request, pk):
        """Gets all the course history in the course with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the course histories data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Can be raised by:
                1. `IsInstructorOrTAOrStudent` permission class
                2. `IsOwner` permission class
            HTTP_403_FORBIDDEN: Can be raised by:
                1. `IsInstructorOrTAOrStudent` permission class
                2. `IsOwner` permission class
        """
        check = self._is_registered(pk, request.user)

        if check is not True:
            return check

        course_histories = CourseHistory.objects.filter(course_id=pk)
        page = self.paginate_queryset(course_histories)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(course_histories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_course_history(self, request, pk):
        """Gets the course history with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): course history id

        Returns:
            `Response` with the course history data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent` permission class
            HTTP_404_NOT_FOUND: Raised by:
                1. `_is_registered()` method
                2. CourseHistory object does not exist
        """
        try:
            course_history = CourseHistory.objects.select_related("course").get(id=pk)
        except CourseHistory.DoesNotExist as e:
            logger.exception(e)
            data = {"error": "Course history with id: {} does not exists.".format(pk)}
            return Response(data["error"], status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, course_history)
        check = self._is_registered(course_history.course.id, request.user)
        if check is not True:
            return check

        serializer = self.get_serializer(course_history)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_course_history(self, request, pk):
        """Updates the course history with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): course history id

        Returns:
            `Response` with the updated course history data and status HTTP_200_OK.

        Raises:
            HTTP_400_BAD_REQUEST: Raised by `is_valid()` method of the serializer
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTAOrStudent`
                permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTAOrStudent` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        course_history = CourseHistory.objects.select_related("course").get(id=pk)
        self.check_object_permissions(request, course_history)
        check = self._is_registered(course_history.course.id, request.user)
        if check is not True:
            return check

        serializer = self.get_serializer(
            course_history, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class ChapterViewSet(viewsets.GenericViewSet, custom_mixins.ChapterorPageMixin):
    """Viewset for `Chapter`."""

    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_chapter(self, request):
        return self.create(request)

    @action(detail=True, methods=["GET"])
    def list_chapters(self, request, pk):
        return self.list(request, pk, Chapter)

    @action(detail=True, methods=["GET"])
    def retrieve_chapter(self, request, pk):
        return self.retrieve(request, pk)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_chapter(self, request, pk):
        return self.update(request, pk)

    @action(detail=True, methods=["DELETE"])
    def delete_chapter(self, request, pk):
        return self._delete(request, pk)


class SectionViewSet(viewsets.GenericViewSet, custom_mixins.IsRegisteredMixin):
    """Viewset for `Section`."""

    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = (IsInstructorOrTA,)

    @action(detail=False, methods=["POST"])
    def create_section(self, request):
        """Adds a section to the chapter.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created section data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by:
                1. `_is_instructor_or_ta()` permission class
                2. `IntegrityError` of the database
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
        check = self._is_instructor_or_ta(course_id, request.user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

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

        sections = Section.objects.filter(chapter_id=pk)
        serializer = self.get_serializer(sections, many=True)
        return Response(serializer.data)

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
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        section = self.get_object()
        serializer = self.get_serializer(section)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_section(self, request, pk):
        """Updates the section with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Section id

        Returns:
            `Response` with the updated section data and status HTTP_200_OK.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by
                1. `IsInstructorOrTA` permission class
                2. `IntegrityError` of the database
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        section = self.get_object()
        serializer = self.get_serializer(section, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

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
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        section = self.get_object()
        section.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PageViewSet(viewsets.GenericViewSet):
    """Viewset for `Page`."""

    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsInstructorOrTA,)

    def _is_registered(self, course_id, user):
        """Checks if the user is registered in the given course.

        Args:
            course_id (int): course id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user is registered
            in the course with id course_id or not.

        Raises:
            HTTP_404_NOT_FOUND: Raised if:
                1. The course does not exist
                2. The user is not registered in the course
        """
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist as e:
            logger.exception(e)
            data = {
                "error": "Course with id: {} does not exist.".format(course_id),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)

        if not check_course_registration(course_id, user):
            data = {
                "error": "User: {} is not registered in the course: {}.".format(
                    user, course
                ),
            }
            logger.warning(data["error"])
            return Response(data, status.HTTP_404_NOT_FOUND)
        return True

    @action(detail=False, methods=["POST"])
    def create_page(self, request):
        """Adds a page to the course.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created page data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by:
                1. If the user is not the instructor/ta of the course
                2. `IsInstructorOrTA` permission class
                3. `IntegrityError` of the database
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        user = request.user
        course_id = request.data["course"]
        check = self._is_registered(course_id, user)
        if check is not True:
            return check

        # This is specifically done during page creation (not during updation or
        # deletion) because it can't be handled by IsInstructorOrTA permission class
        if not check_is_instructor_or_ta(course_id, user):
            data = {
                "error": "User: {} is not the instructor/ta of"
                " the course with id: {}.".format(user, course_id),
            }
            logger.warning(data["error"])
            return Response(data, status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                data = {
                    "error": "Page with title '{}' already exists.".format(
                        serializer.initial_data["title"]
                    )
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"])
    def list_pages(self, request, pk):
        """Gets all the pages in the course with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): course id

        Returns:
            `Response` with all the pages data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        check = self._is_registered(pk, request.user)
        if check is not True:
            return check

        pages = Page.objects.filter(course_id=pk)
        serializer = self.get_serializer(pages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def retrieve_page(self, request, pk):
        """Gets the page with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): page id

        Returns:
            `Response` with the page data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        page = self.get_object()
        check = self._is_registered(page.course.id, request.user)
        if check is not True:
            return check

        serializer = self.get_serializer(page)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT", "PATCH"])
    def update_page(self, request, pk):
        """Updates the page with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): page id

        Returns:
            `Response` with the updated page data and status HTTP_200_OK.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by
                1. `IsInstructorOrTA` permission class
                2. `IntegrityError` of the database
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        page = self.get_object()
        check = self._is_registered(page.course.id, request.user)
        if check is not True:
            return check

        serializer = self.get_serializer(page, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as e:
                logger.exception(e)
                data = {
                    "error": "Page with title '{}' already exists.".format(
                        serializer.initial_data["title"]
                    )
                }
                return Response(data, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["DELETE"])
    def delete_page(self, request, pk):
        """Deletes the page with id as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): page id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `_is_registered()` method
        """
        page = self.get_object()
        check = self._is_registered(page.course.id, request.user)
        if check is not True:
            return check

        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
