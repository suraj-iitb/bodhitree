import os
from unittest import mock

from django.test import TestCase

from course.models import Course
from programming_assignments.models import Assignment
from utils.utils import (
    get_assignment_file_upload_path,
    get_assignment_folder,
    get_course_folder,
)


class TestGetCourseFolder(TestCase):
    """Test for `get_course_folder()` function"""

    def setUp(self):
        # Mocking of Course
        self.course_mock = mock.MagicMock(spec=Course, name="CourseMock")
        self.course_mock.id = 1
        self.course_mock.owner = 1
        self.course_mock.code = ""
        self.course_mock.title = "   Course 1 "

    def test_get_course_folder_without_code(self):
        """Test for `get_course_folder()` function without course code"""
        actual_course_folder = get_course_folder(self.course_mock)

        self.course_mock.title = self.course_mock.title.strip().replace(" ", "_")
        expected_course_folder = "{}.{}".format(
            self.course_mock.id, self.course_mock.title
        )

        self.assertEqual(actual_course_folder, expected_course_folder)

    def test_get_course_folder_with_code(self):
        """Test for `get_course_folder()` function with course code"""
        self.course_mock.code = "Code 1"

        actual_course_folder = get_course_folder(self.course_mock)

        self.course_mock.code = self.course_mock.code.strip().replace(" ", "_")
        self.course_mock.title = self.course_mock.title.strip().replace(" ", "_")
        expected_course_folder = "{}.{}:{}".format(
            self.course_mock.id, self.course_mock.code, self.course_mock.title
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


class TestGetAssignmentFileUploadPath(TestCase):
    """Test for `get_assignment_file_upload_path()` function"""

    def test_get_assignment_file_upload_path_for_programming(self):
        """Test for `get_assignment_file_upload_path()` function for programming"""
        assignment_type = "programming"
        sub_folder = "   question_files"
        filename = "file.pdf   "

        # Mocking of Course
        course_mock = mock.MagicMock(spec=Course, name="CourseMock")
        course_mock.id = 1
        course_mock.owner = 1
        course_mock.code = " Code 1      "
        course_mock.title = "Course  1 "
        # Mocking of Assignment
        assignment_mock = mock.MagicMock(spec=Assignment, name="AssignmentMock")
        assignment_mock.id = 1
        assignment_mock.name = "   Assignment 1 "
        assignment_mock.course = course_mock

        actual_assignment_file_upload_path = get_assignment_file_upload_path(
            assignment_mock, assignment_type, sub_folder, filename
        )

        course_folder = get_course_folder(assignment_mock.course)
        assignment_folder = get_assignment_folder(assignment_mock, assignment_type)
        expected_assignment_file_upload_path = os.path.join(
            course_folder, assignment_folder, sub_folder.strip(), filename.strip()
        )

        self.assertEqual(
            actual_assignment_file_upload_path, expected_assignment_file_upload_path
        )

    def test_get_assignment_file_upload_path_for_subjective(self):
        """Test for `get_assignment_file_upload_path()` function for subjective"""
        assignment_type = "subjective"
        sub_folder = "submission_files "
        filename = " file.pdf"

        # Mocking of Course
        course_mock = mock.MagicMock(spec=Course, name="CourseMock")
        course_mock.id = 1
        course_mock.owner = 1
        course_mock.code = " Code 1      "
        course_mock.title = "Course  1 "
        # Mocking of Assignment
        assignment_mock = mock.MagicMock(spec=Assignment, name="AssignmentMock")
        assignment_mock.id = 1
        assignment_mock.name = "   Assignment 1 "
        assignment_mock.course = course_mock

        actual_assignment_file_upload_path = get_assignment_file_upload_path(
            assignment_mock, assignment_type, sub_folder, filename
        )

        course_folder = get_course_folder(assignment_mock.course)
        assignment_folder = get_assignment_folder(assignment_mock, assignment_type)
        expected_assignment_file_upload_path = os.path.join(
            course_folder, assignment_folder, sub_folder.strip(), filename.strip()
        )

        self.assertEqual(
            actual_assignment_file_upload_path, expected_assignment_file_upload_path
        )
