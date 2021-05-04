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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Mocking of Assignment
        cls.assignment_mock = mock.MagicMock(spec=Assignment, name="AssignmentMock")
        cls.assignment_mock.id = 1
        cls.assignment_mock.name = "   Assignment 1 "

    def test_get_assignment_folder_for_programming(self):
        """Test for `get_assignment_folder()` function for programming"""
        actual_assignment_folder = get_assignment_folder(
            self.assignment_mock, "programming"
        )

        self.assignment_mock.name = self.assignment_mock.name.strip().replace(" ", "_")
        expected_assignment_folder = "{}.{}".format(
            self.assignment_mock.id, self.assignment_mock.name
        )
        expected_assignment_folder = os.path.join(
            "programming_assignment", expected_assignment_folder
        )

        self.assertEqual(actual_assignment_folder, expected_assignment_folder)

    def test_get_assignment_folder_for_subjective(self):
        """Test for `get_assignment_folder()` function for subjective"""
        actual_assignment_folder = get_assignment_folder(
            self.assignment_mock, "subjective"
        )

        self.assignment_mock.name = self.assignment_mock.name.strip().replace(" ", "_")
        expected_assignment_folder = "{}.{}".format(
            self.assignment_mock.id, self.assignment_mock.name
        )
        expected_assignment_folder = os.path.join(
            "subjective_assignment", expected_assignment_folder
        )

        self.assertEqual(actual_assignment_folder, expected_assignment_folder)


class TestGetAssignmentFileUploadPath(TestCase):
    """Test for `get_assignment_file_upload_path()` function"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Mocking of Course
        cls.course_mock = mock.MagicMock(spec=Course, name="CourseMock")
        cls.course_mock.id = 1
        cls.course_mock.owner = 1
        cls.course_mock.code = " Code 1      "
        cls.course_mock.title = "Course  1 "
        # Mocking of Assignment
        cls.assignment_mock = mock.MagicMock(spec=Assignment, name="AssignmentMock")
        cls.assignment_mock.id = 1
        cls.assignment_mock.name = "   Assignment 1 "
        cls.assignment_mock.course = cls.course_mock

    def test_get_assignment_file_upload_path_for_programming(self):
        """Test for `get_assignment_file_upload_path()` function for programming"""
        assignment_type = "programming"
        sub_folder = "   question_files"
        filename = "file.pdf   "

        actual_assignment_file_upload_path = get_assignment_file_upload_path(
            self.assignment_mock, assignment_type, sub_folder, filename
        )

        course_folder = get_course_folder(self.assignment_mock.course)
        assignment_folder = get_assignment_folder(self.assignment_mock, assignment_type)
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

        actual_assignment_file_upload_path = get_assignment_file_upload_path(
            self.assignment_mock, assignment_type, sub_folder, filename
        )

        course_folder = get_course_folder(self.assignment_mock.course)
        assignment_folder = get_assignment_folder(self.assignment_mock, assignment_type)
        expected_assignment_file_upload_path = os.path.join(
            course_folder, assignment_folder, sub_folder.strip(), filename.strip()
        )

        self.assertEqual(
            actual_assignment_file_upload_path, expected_assignment_file_upload_path
        )
