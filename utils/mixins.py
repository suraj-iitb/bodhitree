import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response

from course.models import Chapter, Course, Section
from utils.utils import check_course_registration, check_is_instructor_or_ta


logger = logging.getLogger(__name__)


class IsRegisteredMixin:
    """Mixin for course registration."""

    def _is_registered(self, course_id, user):
        """Checks if the user is registered in the given course.

        Args:
            course_id (int): Course id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user is registered in the course.

        Raises:
            HTTP_403_FORBIDDEN: Raised if the user is not registered in the course
        """
        try:
            Course.objects.get(id=course_id)
        except Course.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        if check_course_registration(course_id, user):
            return True

        error = "The user `{}` is not registered in the course with id: `{}`.".format(
            user, course_id
        )
        logger.error(error)
        return Response(error, status.HTTP_403_FORBIDDEN)

    def _is_instructor_or_ta(self, course_id, user):
        """Checks if the user is instructor/ta in the given course.

        Args:
            course_id (int): Course id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user is instructor/ta in the course.

        Raises:
            HTTP_403_FORBIDDEN: Raised if the user is not instructor/ta in the course
        """
        try:
            Course.objects.get(id=course_id)
        except Course.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        if check_is_instructor_or_ta(course_id, user):
            return True

        error = (
            "The user `{}` is not instructor/ta in the course with id: `{}`.".format(
                user, course_id
            )
        )
        logger.error(error)
        return Response(error, status.HTTP_403_FORBIDDEN)


class ContentMixin_Create(IsRegisteredMixin):
    """Mixin for content (`Video` or `Document`)."""

    def create_content(self, request):
        """Adds a content to the chapter/section

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created content data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised:
                1. Due to serialization errors
                2. If both (or none) the section/chapter is provided
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `_is_instructor_or_ta()` method
            HTTP_404_NOT_FOUND: Raised if the chapter/section does not exist
        """
        user = request.user
        request_data = request.data

        # Validation logic such that only chapter/section is provided. It is done by
        # serializer during validation but we are doing it here becuase we require
        # course_id using chapter/section to check for instructor/ta.
        if request_data["section"] == "" and request_data["chapter"] == "":
            error = "Atleast one of field (chapter or section) must be given."
            logger.error(error)
            return Response(error, status.HTTP_400_BAD_REQUEST)
        elif request_data["section"] != "" and request_data["chapter"] != "":
            error = "Both fields (chapter and section) must not be given."
            logger.error(error)
            return Response(error, status.HTTP_400_BAD_REQUEST)

        # Finds course id
        if request_data["chapter"] == "":
            section_id = request_data["section"]
            try:
                chapter_id = Section.objects.get(id=section_id).chapter_id
            except Section.DoesNotExist as e:
                logger.exception(e)
                return Response(str(e), status.HTTP_404_NOT_FOUND)
        else:
            chapter_id = request_data["chapter"]
        try:
            chapter = Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)
        course_id = chapter.course_id

        # This is specifically done during content creation (not during updation or
        # deletion) because it can't be handled by `IsInstructorOrTA` permission class.
        check = self._is_instructor_or_ta(course_id, user)
        if check is not True:
            return check

        serializer = self.get_serializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class ContentMixin_List(IsRegisteredMixin):
    """Mixin for content (`Video` or `Document`)."""

    def list_chapter_content(self, request, pk, model):
        """Gets all the contents in the chapter with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Chapter id
            model: `Model` class (`Video` or `Document`)

        Returns:
            `Response` with all the content data in chapter and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised if the chapter does not exist
        """
        try:
            course_id = Chapter.objects.get(id=pk).course_id
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        # This is specifically done during list all contents (not during retrieval of
        # a content) because it can't be handled by `IsInstructorOrTA` permission class.
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        contents = model.objects.filter(chapter_id=pk)
        serializer = self.get_serializer(contents, many=True)
        return Response(serializer.data)

    def list_section_content(self, request, pk, model):
        """Gets all the contents in the section with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Section id
            model: `Model` class (`Video` or `Document`)

        Returns:
            `Response` with all the content data in section and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised if the section does not exist
        """
        try:
            course_id = (
                Section.objects.select_related("chapter").get(id=pk).chapter.course_id
            )
        except Section.DoesNotExist as e:
            logger.exception(e)
            return Response(str(e), status.HTTP_404_NOT_FOUND)

        # This is specifically done during list all contents (not during retrieval of
        # a content) because it can't be handled by `IsInstructorOrTA` permission class.
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        contents = model.objects.filter(section_id=pk)
        serializer = self.get_serializer(contents, many=True)
        return Response(serializer.data)


class CreateMixin:
    """---"""

    def create(self, request):
        """---.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created chapter/page data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_403_FORBIDDEN: Raised:
                1. Due to `IntegrityError` of the database
            HTTP_404_NOT_FOUND: Raised if the course does not exist
        """
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


class InsOrTACreateMixin(CreateMixin, IsRegisteredMixin):
    """---"""

    def create(self, request, course_id):
        """---.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created chapter/page data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_403_FORBIDDEN: Raised:
                1. By `_is_instructor_or_ta()` method
                2. Due to `IntegrityError` of the database
            HTTP_404_NOT_FOUND: Raised if the course does not exist
        """
        # This is specifically done during chapter/page creation (not during updation or
        # deletion) because it can't be handled by `IsInstructorOrTA` permission class.
        check = self._is_instructor_or_ta(course_id, request.user)
        if check is not True:
            return check

        return super().create(request)


class RegisteredCreateMixin(CreateMixin, IsRegisteredMixin):
    """---"""

    def create(self, request, course_id):
        """---.

        Args:
            request (Request): DRF `Request` object

        Returns:
            `Response` with the created chapter/page data and status HTTP_201_CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_403_FORBIDDEN: Raised:
                1. By `_is_registered()` method
                2. Due to `IntegrityError` of the database
            HTTP_404_NOT_FOUND: Raised if the course does not exist
        """
        # This is specifically done during chapter/page creation (not during updation or
        # deletion) because it can't be handled by `IsInstructorOrTA` permission class.
        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        return super().create(request)


class ListMixin:
    """---"""

    def list(self, request, pk):
        """---

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the chapter/page data and status HTTP_200_OK.

        Raises:
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised if the course does not exist
        """
        queryset = self.filter_queryset(self.get_queryset_list(pk))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RegisteredListMixin(ListMixin, IsRegisteredMixin):
    """---"""

    def list(self, request, pk):
        """---

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the chapter/page data and status HTTP_200_OK.

        Raises:
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised if the course does not exist
        """
        # This is specifically done during list all chapters/pages (not during
        # retrieval of a chapter) because it can't be handled by `IsInstructorOrTA`
        # permission class.
        check = self._is_registered(pk, request.user)
        if check is not True:
            return check

        return super().list(request, pk)


class InsOrTAListMixin(ListMixin, IsRegisteredMixin):
    """---"""

    def list(self, request, pk):
        """---

        Args:
            request (Request): DRF `Request` object
            pk (int): Course id

        Returns:
            `Response` with all the chapter/page data and status HTTP_200_OK.

        Raises:
            HTTP_403_FORBIDDEN: Raised by `_is_registered()` method
            HTTP_404_NOT_FOUND: Raised if the course does not exist
        """
        # This is specifically done during list all chapters/pages (not during
        # retrieval of a chapter) because it can't be handled by `IsInstructorOrTA`
        # permission class.
        check = self._is_instructor_or_ta(pk, request.user)
        if check is not True:
            return check

        return super().list(request, pk)


class RetrieveMixin:
    """---"""

    def retrieve(self, request, pk):
        """---

        Args:
            request (Request): DRF `Request` object
            pk (int): Chapter/Page id

        Returns:
            `Response` with the chapter/page data and status HTTP_200_OK.

        Raises:
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class UpdateMixin:
    """---"""

    def update(self, request, pk):
        """---

        Args:
            request (Request): DRF `Request` object
            pk (int): Chapter/Page id

        Returns:
            `Response` with the updated chapter/page data and status HTTP_200_OK.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_403_FORBIDDEN: Raised by: `IntegrityError` of the database
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=True)
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


class DeleteMixin:
    """---"""

    def _delete(self, request, pk):
        """Deletes the chapter/page with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Chapter/Page id

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        obj = self.get_object()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
