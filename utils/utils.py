import logging
import os

from django.db.models import Q

from course.models import Course, CourseHistory
from registration.models import SubscriptionHistory


logger = logging.getLogger(__name__)


def get_course_folder(course):
    """Gets a course folder name.

    Args:
        course (Course): `Course` model instance

    Returns:
        A course folder name.
    """
    course_id = course.id
    course_code = course.code.strip().replace(" ", "_")
    course_title = course.title.strip().replace(" ", "_")
    if course_code:
        return "{}.{}:{}".format(course_id, course_code, course_title)
    return "{}.{}".format(course_id, course_title)


def get_assignment_folder(assignment, assignment_type):
    """Gets a assignment folder name.

    Args:
        assignment (Assignment): `Assignment` model instance
        assignment_type (str): Assignment type ("programming" or "subjective")

    Returns:
        A assignment folder name.
    """
    assignment_id = assignment.id
    assignment_name = assignment.name.strip().replace(" ", "_")
    assignment_folder = "{}.{}".format(assignment_id, assignment_name)
    if assignment_type == "programming":
        return os.path.join("programming_assignment", assignment_folder)
    elif assignment_type == "subjective":
        return os.path.join("subjective_assignment", assignment_folder)


def get_assignment_file_upload_path(assignment, assignment_type, sub_folder, filename):
    """Gets path to upload an assignment file (both programming & subjective).

    Args:
        assignment (Assignment): `Assignment` model instance
        assignment_type (str): Assignment type ("programming" or "subjective")
        sub_folder (str): "submission_files" or "question_files" or "testcase_files"
        filename (str): name of a file

    Returns:
        A path to upload a assignment file.
    """
    course_folder = get_course_folder(assignment.course)
    assignment_folder = get_assignment_folder(assignment, assignment_type)
    return os.path.join(
        course_folder, assignment_folder, sub_folder.strip(), filename.strip()
    )


def check_course_registration(course_id, user):
    """Checks if the user is registered in a course.

    Args:
        course_id (int): course id
        user (User): `User` model intstance

    Returns:
        A bool value indicating if the user is registered in a course or not.
    """
    course_history = CourseHistory.objects.filter(
        course_id=course_id, user=user
    ).count()
    if course_history:
        return True
    return False


def is_instructor_or_ta(course_id, user):
    """Checks if the user is instructor/ta in a course.

    Args:
        course_id (int): course id
        user (User): `User` model intstance

    Returns:
        A bool value indicating if the user is is instructor/ta in a course or not.
    """
    course_history = CourseHistory.objects.filter(
        Q(course_id=course_id) & (Q(role="I") | Q(role="T")) & Q(user=user)
    ).count()
    if course_history:
        return True
    return False


# TODO: Add date check for subscription_history
def has_valid_subscription(user):
    """Checks if the user has a subscription and is it valid?

    Args:
        user (User): `User` model intstance

    Returns:
        A bool value denoting if the user has a valid subscription or not.
    """
    subscription_history = SubscriptionHistory.objects.filter(user=user).count()
    if subscription_history:
        return True
    return False


# TODO: Add date check for subscription_history
def is_course_limit_reached(user):
    """Checks if the subscription course limit is exhausted for the user.

    Args:
        user (User): `User` model intstance

    Returns:
        A bool value denoting if the subscription course limit is exhausted for the
        user or not.

    Raises:
        SubscriptionHistory.DoesNotExist: Raised if the subscription history does not
            exist for the user.
    """
    no_of_courses = Course.objects.filter(owner=user).count()
    try:
        subscription_history = SubscriptionHistory.objects.select_related(
            "subscription"
        ).get(user=user)
    except SubscriptionHistory.DoesNotExist as e:
        logger.exception(e)
        raise
    if no_of_courses < subscription_history.subscription.no_of_courses:
        return False
    return True
