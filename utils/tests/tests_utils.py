import os
from unittest import mock

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase

from course.models import Course, CourseHistory
from programming_assignments.models import Assignment
from utils.utils import (
    check_course_registration,
    check_is_instructor_or_ta,
    get_assignment_file_upload_path,
    get_assignment_folder,
    get_course_folder,
)


User = get_user_model()


class TestGetCourseFolder(TestCase):
    """Test for `get_course_folder()` function"""

    def setUp(self):
        # Mocking of Course
        self.course_mock = mock.MagicMock(spec=Course, name="CourseMock")
        self.course_mock.id = 1
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

    def setUp(self):
        # Mocking of Assignment
        self.assignment_mock = mock.MagicMock(spec=Assignment, name="AssignmentMock")
        self.assignment_mock.id = 1
        self.assignment_mock.name = "   Assignment 1 "

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

    def setUp(self):
        # Mocking of Course
        self.course_mock = mock.MagicMock(spec=Course, name="CourseMock")
        self.course_mock.id = 1
        self.course_mock.code = " Code 1      "
        self.course_mock.title = "Course  1 "
        # Mocking of Assignment
        self.assignment_mock = mock.MagicMock(spec=Assignment, name="AssignmentMock")
        self.assignment_mock.id = 1
        self.assignment_mock.name = "   Assignment 1 "
        self.assignment_mock.course = self.course_mock

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


class TestCheckCourseRegistration(TestCase):
    """Test for `check_course_registration()` function"""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
    ]

    def _helper(self, course_id, user_id):
        user = User.objects.get(id=user_id)
        actual_registration = check_course_registration(course_id, user)
        course_history = CourseHistory.objects.filter(
            course_id=course_id, user=user
        ).count()
        expected_registration = True if course_history else False
        self.assertEqual(actual_registration, expected_registration)

    def test_check_course_registration_if_registered(self):
        """Test for `check_course_registration()` function if user is registered."""
        course_id = 1
        user_id = 1
        self._helper(course_id, user_id)

    def test_check_course_registration_if_not_registered(self):
        """Test for `check_course_registration()` function if user is not registered."""
        course_id = 2
        user_id = 1
        self._helper(course_id, user_id)


class TestIsInstructorOrTa(TestCase):
    """Test for `check_is_instructor_or_ta()` function"""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
    ]

    def _helper(self, course_id, user_id):
        user = User.objects.get(id=user_id)
        actual_role = check_is_instructor_or_ta(course_id, user)
        course_history = CourseHistory.objects.filter(
            Q(course_id=course_id) & (Q(role="I") | Q(role="T")) & Q(user=user)
        ).count()
        expected_role = True if course_history else False
        self.assertEqual(actual_role, expected_role)

    def test_is_instructor_or_ta_if_user_is_instructor(self):
        """Test for `check_is_instructor_or_ta()` function if user is instructor."""
        course_id = 1
        user_id = 1
        self._helper(course_id, user_id)

    def test_is_instructor_or_ta_if_user_is_ta(self):
        """Test for `check_is_instructor_or_ta()` function if user is ta."""
        course_id = 1
        user_id = 2
        self._helper(course_id, user_id)

    def test_is_instructor_or_ta_if_user_is_student(self):
        """Test for `check_is_instructor_or_ta()` function if user is student."""
        course_id = 1
        user_id = 3
        self._helper(course_id, user_id)

    def test_is_instructor_or_ta_if_user_is_not_registered(self):
        """Test for `check_is_instructor_or_ta()` function if user is not registered."""
        course_id = 2
        user_id = 1
        self._helper(course_id, user_id)
