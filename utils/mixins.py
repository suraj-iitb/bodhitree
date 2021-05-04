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
