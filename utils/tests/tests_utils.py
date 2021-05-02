from django.test import TestCase

from course.models import Course
from utils.utils import get_course_folder


class TestGetCourseFolder(TestCase):
    """Test for `get_course_folder()` function"""

    fixtures = [
        "users.test.yaml",
    ]

    def test_get_course_folder_without_code(self):
        """Test for `get_course_folder()` function without course code"""
        course = Course(
            owner_id=1,
            title="Course 1",
        )
        course.save()
        actual_course_folder = get_course_folder(course)
        course_id = course.id
        course_title = course.title.replace(" ", "_")
        expected_course_folder = "{}.{}".format(course_id, course_title)
        self.assertEqual(actual_course_folder, expected_course_folder)

    def test_get_course_folder_with_code(self):
        """Test for `get_course_folder()` function with course code"""
        course = Course(
            owner_id=1,
            code="Code 1",
            title="Course 1",
        )
        course.save()
        actual_course_folder = get_course_folder(course)
        course_id = course.id
        course_code = course.code.replace(" ", "_")
        course_title = course.title.replace(" ", "_")
        expected_course_folder = "{}.{}:{}".format(course_id, course_code, course_title)
        self.assertEqual(actual_course_folder, expected_course_folder)
