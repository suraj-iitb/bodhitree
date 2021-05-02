import os
from unittest import mock

from django.test import TestCase

from course.models import Course
from programming_assignments.models import Assignment
from utils.utils import get_assignment_folder, get_course_folder


class TestGetCourseFolder(TestCase):
    """Test for `get_course_folder()` function"""

    def test_get_course_folder_without_code(self):
        """Test for `get_course_folder()` function without course code"""
        # Mocking of Course
        course_mock = mock.MagicMock(spec=Course, name="CourseMock")
        course_mock.id = 1
        course_mock.owner = 1
        course_mock.code = ""
        course_mock.title = "   Course 1 "

        actual_course_folder = get_course_folder(course_mock)

        course_mock.title = course_mock.title.strip().replace(" ", "_")
        expected_course_folder = "{}.{}".format(course_mock.id, course_mock.title)

        self.assertEqual(actual_course_folder, expected_course_folder)

    def test_get_course_folder_with_code(self):
        """Test for `get_course_folder()` function with course code"""
        # Mocking of Course
        course_mock = mock.MagicMock(spec=Course, name="CourseMock")
        course_mock.id = 1
        course_mock.owner = 1
        course_mock.code = " Code 1      "
        course_mock.title = "Course  1 "

        actual_course_folder = get_course_folder(course_mock)

        course_mock.code = course_mock.code.strip().replace(" ", "_")
        course_mock.title = course_mock.title.strip().replace(" ", "_")
        expected_course_folder = "{}.{}:{}".format(
            course_mock.id, course_mock.code, course_mock.title
        )

        self.assertEqual(actual_course_folder, expected_course_folder)


class TestGetAssignmentFolder(TestCase):
    """Test for `get_assignment_folder()` function"""

    def test_get_assignment_folder_for_programming(self):
        """Test for `get_assignment_folder()` function for programming"""
        # Mocking of Assignment
        assignment_mock = mock.MagicMock(spec=Assignment, name="AssignmentMock")
        assignment_mock.id = 1
        assignment_mock.name = "   Assignment 1 "

        actual_assignment_folder = get_assignment_folder(assignment_mock, "programming")

        assignment_mock.name = assignment_mock.name.strip().replace(" ", "_")
        expected_assignment_folder = "{}.{}".format(
            assignment_mock.id, assignment_mock.name
        )
        expected_assignment_folder = os.path.join(
            "programming_assignment", expected_assignment_folder
        )

        self.assertEqual(actual_assignment_folder, expected_assignment_folder)

    def test_get_assignment_folder_for_subjective(self):
        """Test for `get_assignment_folder()` function for subjective"""
        # Mocking of Assignment
        assignment_mock = mock.MagicMock(spec=Assignment, name="AssignmentMock")
        assignment_mock.id = 1
        assignment_mock.name = "   Assignment 1    "

        actual_assignment_folder = get_assignment_folder(assignment_mock, "subjective")

        assignment_mock.name = assignment_mock.name.strip().replace(" ", "_")
        expected_assignment_folder = "{}.{}".format(
            assignment_mock.id, assignment_mock.name
        )
        expected_assignment_folder = os.path.join(
            "subjective_assignment", expected_assignment_folder
        )

        self.assertEqual(actual_assignment_folder, expected_assignment_folder)
