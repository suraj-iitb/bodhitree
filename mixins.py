import logging

from rest_framework import status
from rest_framework.response import Response

from course.models import Course
from utils.utils import check_course_registration, is_instructor_or_ta


logger = logging.getLogger(__name__)


class IsRegisteredMixins:
    def _is_registered(self, course_id, user):
        """Checks if the user is registered in the given course.

        Args:
            course_id (int): course id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user is registered
            in the course with id course_id.

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
                "error": "Course with id: {} does not exist".format(course_id),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)

        if not check_course_registration(course_id, user):
            data = {
                "error": "User: {} is not registered in the course: {}".format(
                    user, course
                ),
            }
            logger.warning(data["error"])
            return Response(data, status.HTTP_404_NOT_FOUND)
        return True

    def _is_registered_as_instructor_or_ta(self, course_id, user):
        """Checks if the user is registered in the given course as instructor/ta

        Args:
            course_id (int): course id
            user (User): `User` model object

        Returns:
            A bool value representing whether the user is registered
            in the course with id course_id as instructor/ta.

        Raises:
            HTTP_404_NOT_FOUND: Raised if the course does not exist
            HTTP_403_FORBIDDEN: Raise if the user is not instructor/ta
        """
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist as e:
            logger.exception(e)
            data = {
                "error": "Course with id: {} does not exist".format(course_id),
            }
            return Response(data, status.HTTP_404_NOT_FOUND)
        if not is_instructor_or_ta(course_id, user):
            data = {
                "error": "User: {} is not registered in the course: {} as"
                " instructor/ta".format(user, course),
            }
            logger.warning(data["error"])
            return Response(data, status.HTTP_403_FORBIDDEN)
        return True
