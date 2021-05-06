import logging

from rest_framework import status
from rest_framework.response import Response

from course.models import Chapter, Section
from utils.utils import check_course_registration, check_is_instructor_or_ta


logger = logging.getLogger(__name__)


class IsRegisteredMixins:
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
        if check_is_instructor_or_ta(course_id, user):
            return True

        error = (
            "The user `{}` is not instructor/ta in the course with id: `{}`.".format(
                user, course_id
            )
        )
        logger.error(error)
        return Response(error, status.HTTP_403_FORBIDDEN)

    def _is_registered_using_chapter_id(self, chapter_id, user):
        """Checks if the user is registered in the given course.

        Args:
            chapter_id (int): chapter id
            user (User): `User` model object

        Returns:
            A 2-valued tuple where
                first_value: boolean representing whether the user is registered
                    in the course
                second_value: course id

        Raises:
            HTTP_404_NOT_FOUND: Raised if:
                1. The chapter does not exist
                2. The user is not registered in the course
        """
        try:
            chapter = Chapter.objects.select_related("course").get(id=chapter_id)
        except Chapter.DoesNotExist as e:
            logger.exception(e)
            return (Response(e, status.HTTP_404_NOT_FOUND), None)

        course_id = chapter.course.id
        if not check_course_registration(course_id, user):
            data = {
                "error": "User: {} is not registered in the course with id: {}.".format(
                    user, course_id
                ),
            }
            logger.warning(data["error"])
            return (Response(data, status.HTTP_404_NOT_FOUND), None)
        return (True, course_id)

    def _is_registered_using_section_id(self, section_id, user):
        """Checks if the user is registered in the given course.

        Args:
            section_id (int): section id
            user (User): `User` model object

        Returns:
            A 2-valued tuple where
                first_value: boolean representing whether the user is registered
                    in the course
                second_value: course id

        Raises:
            HTTP_404_NOT_FOUND: Raised if:
                1. The chapter does not exist
                2. The user is not registered in the course
        """
        try:
            section = Section.objects.select_related("chapter__course").get(
                id=section_id
            )
        except Section.DoesNotExist as e:
            logger.exception(e)
            return (Response(e, status.HTTP_404_NOT_FOUND), None)

        course_id = section.chapter.course.id
        if not check_course_registration(course_id, user):
            data = {
                "error": "User: {} is not registered in the course with id: {}.".format(
                    user, course_id
                ),
            }
            logger.warning(data["error"])
            return (Response(data, status.HTTP_404_NOT_FOUND), None)
        return (True, course_id)


class ContentMixin(IsRegisteredMixins):
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
            HTTP_404_NOT_FOUND: Raised if chapter/section does not exist
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

        check = self._is_registered(course_id, request.user)
        if check is not True:
            return check

        contents = model.objects.filter(section_id=pk)
        serializer = self.get_serializer(contents, many=True)
        return Response(serializer.data)

    def retrieve_content(self, request, pk):
        """Gets the content with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Content id (video_id or document_id)

        Returns:
            `Response` with the content data and status HTTP_200_OK.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        content = self.get_object()
        serializer = self.get_serializer(content)
        return Response(serializer.data)

    def update_content(self, request, pk):
        """Updates the content with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Content id (video_id or document_id)

        Returns:
            `Response` with the updated content data and status HTTP_200_OK.

        Raises:
            HTTP_400_BAD_REQUEST: Raised due to serialization errors
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        content = self.get_object()
        serializer = self.get_serializer(content, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        errors = serializer.errors
        logger.error(errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_content(self, request, pk):
        """Deletes the content with primary key as pk.

        Args:
            request (Request): DRF `Request` object
            pk (int): Content id (video_id or document_id)

        Returns:
            `Response` with no data and status HTTP_204_NO_CONTENT.

        Raises:
            HTTP_401_UNAUTHORIZED: Raised by `IsInstructorOrTA` permission class
            HTTP_403_FORBIDDEN: Raised by `IsInstructorOrTA` permission class
            HTTP_404_NOT_FOUND: Raised by `get_object()` method
        """
        content = self.get_object()
        content.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
