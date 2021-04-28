import logging
import os

from django.db.models import Q

from course.models import Course, CourseHistory
from registration.models import SubscriptionHistory


logger = logging.getLogger(__name__)


def get_course_folder(course):
    course_id = course.id
    course_code = course.code.replace(" ", "_")
    course_title = course.title.replace(" ", "_")
    if course_code:
        return "{}.{}:{}".format(course_id, course_code, course_title)
    return "{}.{}".format(course_id, course_title)


def get_assignment_folder(assignment, assignment_type):
    assignment_id = assignment.id
    assignment_name = assignment.name.replace(" ", "_")
    assignment_folder = "{}.{}".format(assignment_id, assignment_name)
    if assignment_type == "programming":
        return os.path.join("programming_assignment", assignment_folder)
    elif assignment_type == "subjective":
        return os.path.join("subjective_assignment", assignment_folder)


def get_assignment_file_upload_path(assignment, assignment_type, sub_folder, filename):
    course_folder = get_course_folder(assignment.course)
    assignment_folder = get_assignment_folder(assignment, assignment_type)
    return os.path.join(course_folder, assignment_folder, sub_folder, filename)


def check_course_registration(course_id, user):
    course_history = CourseHistory.objects.filter(
        course_id=course_id, user=user
    ).count()
    if course_history:
        return True
    return False


def is_instructor_or_ta(course_id, user):
    course_history = CourseHistory.objects.filter(
        Q(course_id=course_id) & (Q(role="I") | Q(role="T")) & Q(user=user)
    ).count()
    if course_history:
        return True
    return False


# TODO: Add date check for subscription_history
def has_valid_subscription(user):
    subscription_history = SubscriptionHistory.objects.filter(user=user).count()
    if subscription_history:
        return True
    return False


# TODO: Add date check for subscription_history
def is_course_limit_reached(user):
    no_of_courses = Course.objects.filter(owner=user).count()
    try:
        subscription_history = SubscriptionHistory.objects.select_related(
            "subscription"
        ).get(user=user)
    except (
        SubscriptionHistory.DoesNotExist,
        SubscriptionHistory.MultipleObjectsReturned,
    ) as e:
        logger.exception(e)
        raise
    if no_of_courses < subscription_history.subscription.no_of_courses:
        return False
    return True
