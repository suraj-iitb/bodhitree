from unittest import mock

from django.core.files import File
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from utils import credentials

from .models import (
    AdvancedProgrammingAssignment,
    AssignmentSection,
    SimpleProgrammingAssignment,
)


ins_cred = credentials.TEST_INSTRUCTOR_CREDENTIALS
ta_cred = credentials.TEST_TA_CREDENTIALS
stu_cred = credentials.TEST_STUDENT_CREDENTIALS


class AssignmentViewSetTest(APITestCase):
    """Test for `SimpleProgrammingAssignmentViewSet`."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "simpleprogrammingassignment.test.yaml",
        "advancedprogrammingassignment.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_assignment_helper(self, name, status_code, assign_type):
        """Helper function `test_create_simple_prog_assignment()`.

        Args:
            name (str): name of the assignment
            status_code (int): Expected status code of the API call
            assign_type: "simple" or "adv"
        """
        programming_language = "C"
        course_id = 1
        start_date = "2021-10-25T14:30:59+05:30"
        end_date = "2021-11-25T14:30:59+05:30"
        extended_date = "2021-11-25T14:30:59+05:30"
        data_simple = {
            "course": course_id,
            "programming_language": programming_language,
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "extended_date": extended_date,
        }
        if assign_type == "adv":
            # Helper code mock file
            helper_code_mock = mock.MagicMock(spec=File, name="FileMock")
            helper_code_mock.name = "helper.cpp"

            # instructor solution code mock file
            instructor_solution_code_mock = mock.MagicMock(spec=File, name="FileMock")
            instructor_solution_code_mock.name = "ins_solution_code.cpp"

            data_adv = {
                "helper_code": helper_code_mock,
                "instructor_solution_code": instructor_solution_code_mock,
                "files_to_be_submitted": ["file1.cpp", "file2.cpp"],
                "policy": "A",
            }
            data = dict(data_simple, **data_adv)
            create_url = (
                "programming_assignments:advancedprogrammingassignment"
                "-create-assignment"
            )

            url = reverse(create_url)

        else:
            data = data_simple
            url = reverse(
                "programming_assignments:simpleprogrammingassignment-create-assignment"
            )

        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(
                response_data["programming_language"], data["programming_language"]
            )
            self.assertEqual(response_data["name"], data["name"])
            self.assertEqual(response_data["start_date"], data["start_date"])
            self.assertEqual(response_data["end_date"], data["end_date"])
            self.assertEqual(response_data["extended_date"], data["extended_date"])
            if assign_type == "adv":
                self.assertEqual(
                    response_data["files_to_be_submitted"],
                    data["files_to_be_submitted"],
                )
                self.assertEqual(response_data["policy"], data["policy"])

    def _create_simple_or_advance_assignment_helper(self, assign_type):
        """Test: create an assignment.

        Args:
            assign_type: "simple" or "adv"
        """
        # Created by instructor
        self.login(**ins_cred)
        self._create_assignment_helper(
            "Assignment 1",
            status.HTTP_201_CREATED,
            assign_type,
        )
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_assignment_helper(
            "Assignment 2",
            status.HTTP_201_CREATED,
            assign_type,
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_assignment_helper(
            "",
            status.HTTP_400_BAD_REQUEST,
            assign_type,
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._create_assignment_helper(
            "Assignment 3",
            status.HTTP_401_UNAUTHORIZED,
            assign_type,
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._create_assignment_helper(
            "Assignment 4",
            status.HTTP_403_FORBIDDEN,
            assign_type,
        )
        self.logout()

    def test_create_simple_assignment(self):
        self._create_simple_or_advance_assignment_helper("simple")

    def test_create_advanced_assignment(self):
        self._create_simple_or_advance_assignment_helper("adv")

    def _list_assignments_helper(self, course_id, user_id, status_code, assign_type):
        """Helper function for `test_list_assignments()`.

        Args:
            course_id (int): Course id
            user_id (int): User id
            status_code (int): Expected status code of the API call
            assign_type: "simple" or "adv"
        """
        if assign_type == "simple":
            stud_url_str = (
                "programming_assignments:simpleprogrammingassignment-"
                "list-assignments-stud"
            )
            ins_url_str = (
                "programming_assignments:simpleprogrammingassignment-list-assignments"
            )
        elif assign_type == "adv":
            stud_url_str = (
                "programming_assignments:advancedprogrammingassignment-"
                "list-assignments-stud"
            )
            ins_url_str = (
                "programming_assignments:advancedprogrammingassignment-"
                "list-assignments"
            )

        if user_id == 3:
            url = reverse(
                stud_url_str,
                args=[course_id],
            )
        else:
            url = reverse(
                ins_url_str,
                args=[course_id],
            )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            if user_id == 3:
                if assign_type == "simple":
                    self.assertEqual(
                        len(response.data),
                        SimpleProgrammingAssignment.objects.filter(
                            course=course_id, is_published=True
                        ).count(),
                    )
                else:
                    self.assertEqual(
                        len(response.data),
                        AdvancedProgrammingAssignment.objects.filter(
                            course=course_id, is_published=True
                        ).count(),
                    )
            else:
                if assign_type == "simple":
                    self.assertEqual(
                        len(response.data),
                        SimpleProgrammingAssignment.objects.filter(
                            course_id=course_id
                        ).count(),
                    )
                else:
                    self.assertEqual(
                        len(response.data),
                        AdvancedProgrammingAssignment.objects.filter(
                            course_id=course_id
                        ).count(),
                    )

    def _list_simple_or_advanced_assignments_helper(self, assign_type):
        """Test: list all assignments.

        Args:
            assign_type: "simple" or "adv"
        """
        course_id = 1

        # List by instructor
        self.login(**ins_cred)
        self._list_assignments_helper(course_id, 1, status.HTTP_200_OK, assign_type)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_assignments_helper(course_id, 2, status.HTTP_200_OK, assign_type)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._list_assignments_helper(
            course_id, 2, status.HTTP_401_UNAUTHORIZED, assign_type
        )

        # List by student
        self.login(**stu_cred)
        self._list_assignments_helper(course_id, 3, status.HTTP_200_OK, assign_type)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        # List by student
        course_id = 100
        self.login(**stu_cred)
        self._list_assignments_helper(
            course_id, 3, status.HTTP_404_NOT_FOUND, assign_type
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        # List by instructor
        self.login(**ins_cred)
        self._list_assignments_helper(
            course_id, 1, status.HTTP_404_NOT_FOUND, assign_type
        )
        self.logout()

    def test_list_simple_assignment(self):
        self._list_simple_or_advanced_assignments_helper("simple")

    def test_list_advanced_assignment(self):
        self._list_simple_or_advanced_assignments_helper("adv")

    def _retrieve_assignment_helper(self, assignment_id, status_code, assign_type):
        """Helper function for `test_retrieve_assignments()`.

        Args:
            assignment_id (int): Assignment id
            status_code (int): Expected status code of the API call
            assign_type: "simple" or "adv"
        """
        if assign_type == "simple":
            retrieve_url = (
                "programming_assignments:simpleprogrammingassignment-"
                "retrieve-assignment"
            )
        else:
            retrieve_url = (
                "programming_assignments:advancedprogrammingassignment-"
                "retrieve-assignment"
            )
        url = reverse(
            retrieve_url,
            args=[assignment_id],
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], assignment_id)

    def _retrieve_simple_or_advanced_assignment_helper(self, assign_type):
        """Test: retrieve an assignment.

        Args:
            assign_type: "simple" or "adv"
        """
        assignment_id = 1

        # Retrieve by instructor
        self.login(**ins_cred)
        self._retrieve_assignment_helper(assignment_id, status.HTTP_200_OK, assign_type)
        self.logout()

        # Retrieve by ta
        self.login(**ta_cred)
        self._retrieve_assignment_helper(assignment_id, status.HTTP_200_OK, assign_type)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._retrieve_assignment_helper(
            assignment_id, status.HTTP_401_UNAUTHORIZED, assign_type
        )

        assignment_id = 3
        # Retrieve by student
        self.login(**stu_cred)
        self._retrieve_assignment_helper(
            assignment_id, status.HTTP_403_FORBIDDEN, assign_type
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        # Retrieve by student
        assignment_id = 100
        self.login(**stu_cred)
        self._retrieve_assignment_helper(
            assignment_id, status.HTTP_404_NOT_FOUND, assign_type
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        # Retrieve by instructor
        self.login(**ins_cred)
        self._retrieve_assignment_helper(
            assignment_id, status.HTTP_404_NOT_FOUND, assign_type
        )
        self.logout()

    def test_retrieve_simple_assignment(self):
        self._retrieve_simple_or_advanced_assignment_helper("simple")

    def test_retrieve_advanced_assignment(self):
        self._retrieve_simple_or_advanced_assignment_helper("adv")

    def _update_simple_prog_assignment_helper(
        self, assignment_id, name, status_code, method, assign_type
    ):
        """Helper function `test_update_assignment()`
        and `test_partial_update_assignment()`.

        Args:
            assignment_id (int): Assignment id
            name (str): name of the assignment
            status_code (int): Expected status code of the API call
            method: HTTP method ("PUT or "PATCH")
            assign_type: "simple" or "adv"
        """
        programming_language = "C++"
        course_id = 1
        start_date = "2021-10-25T14:30:59+05:30"
        end_date = "2021-11-25T14:30:59+05:30"
        extended_date = "2021-11-25T14:30:59+05:30"
        data_simple = {
            "course": course_id,
            "programming_language": programming_language,
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "extended_date": extended_date,
        }
        if assign_type == "adv":
            # Helper code mock file
            helper_code_mock = mock.MagicMock(spec=File, name="FileMock")
            helper_code_mock.name = "helper.cpp"

            # instructor solution code mock file
            instructor_solution_code_mock = mock.MagicMock(spec=File, name="FileMock")
            instructor_solution_code_mock.name = "ins_solution_code.cpp"

            data_adv = {
                "helper_code": helper_code_mock,
                "instructor_solution_code": instructor_solution_code_mock,
                "files_to_be_submitted": ["file1.cpp", "file2.cpp"],
                "policy": "A",
            }
            data = dict(data_simple, **data_adv)
            update_url = (
                "programming_assignments:advancedprogrammingassignment-"
                "update-assignment"
            )
            url = reverse(
                update_url,
                args=[assignment_id],
            )

        else:
            data = data_simple
            url = reverse(
                "programming_assignments:simpleprogrammingassignment-update-assignment",
                args=[assignment_id],
            )

        if method == "PUT":
            response = self.client.put(url, data, format="multipart")
        else:
            response = self.client.patch(url, data, format="multipart")
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(
                response_data["programming_language"], data["programming_language"]
            )
            self.assertEqual(response_data["name"], data["name"])
            self.assertEqual(response_data["start_date"], data["start_date"])
            self.assertEqual(response_data["end_date"], data["end_date"])
            self.assertEqual(response_data["extended_date"], data["extended_date"])
            if assign_type == "adv":
                self.assertEqual(
                    response_data["files_to_be_submitted"],
                    data["files_to_be_submitted"],
                )
                self.assertEqual(response_data["policy"], data["policy"])

    def _put_or_patch_simple_or_advanced_assignment_helper(self, method, assign_type):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
            assign_type: "simple" or "adv"
        """
        # Update by instructor
        self.login(**ins_cred)
        self._update_simple_prog_assignment_helper(
            1, "Assignment 1", status.HTTP_200_OK, method, assign_type
        )
        self.logout()

        # Update by ta
        self.login(**ta_cred)
        self._update_simple_prog_assignment_helper(
            1, "Assignment 2", status.HTTP_200_OK, method, assign_type
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_simple_prog_assignment_helper(
            1, "", status.HTTP_400_BAD_REQUEST, method, assign_type
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._update_simple_prog_assignment_helper(
            1, "Assignment 3", status.HTTP_401_UNAUTHORIZED, method, assign_type
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._update_simple_prog_assignment_helper(
            1, "Assignment 4", status.HTTP_403_FORBIDDEN, method, assign_type
        )
        self.logout()

    def test_update_simple_assignment(self):
        """Test: update the assignment."""
        self._put_or_patch_simple_or_advanced_assignment_helper("PUT", "simple")
        self._put_or_patch_simple_or_advanced_assignment_helper("PATCH", "simple")

    def test_update_advanced_assignment(self):
        """Test: partial update the assignment."""
        self._put_or_patch_simple_or_advanced_assignment_helper("PUT", "adv")
        self._put_or_patch_simple_or_advanced_assignment_helper("PATCH", "adv")

    def _delete_assignment_helper(self, name, status_code, assign_type):
        """Helper function for `test_delete_course()`.

        Args:
            name (str): name of the assignment
            status_code (int): Expected status code of the API call
            assign_type: "simple" or "adv"
        """
        if assign_type == "simple":
            assignment = SimpleProgrammingAssignment.objects.create(
                course_id=1,
                programming_language="C++",
                name=name,
                start_date="2021-10-25T14:30:59+05:30",
                end_date="2021-11-25T14:30:59+05:30",
                extended_date="2021-12-25T14:30:59+05:30",
            )
            assignment.save()

            delete_url = (
                "programming_assignments:simpleprogrammingassignment-"
                "delete-assignment"
            )
        else:
            assignment = AdvancedProgrammingAssignment.objects.create(
                course_id=1,
                programming_language="C++",
                name=name,
                start_date="2021-10-25T14:30:59+05:30",
                end_date="2021-11-25T14:30:59+05:30",
                extended_date="2021-12-25T14:30:59+05:30",
                files_to_be_submitted=["file1.cpp", "file2.cpp"],
                policy="A",
            )
            assignment.save()

            delete_url = (
                "programming_assignments:advancedprogrammingassignment-"
                "delete-assignment"
            )

        url = reverse(delete_url, args=[assignment.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            if assign_type == "simple":
                self.assertEqual(
                    SimpleProgrammingAssignment.objects.filter(
                        id=assignment.id
                    ).count(),
                    0,
                )
            else:
                self.assertEqual(
                    AdvancedProgrammingAssignment.objects.filter(
                        id=assignment.id
                    ).count(),
                    0,
                )

    def _delete_simple_or_advanced_assignment_helper(self, assign_type):
        """Test: delete the assignment.

        Args:
            assign_type: "simple" or "adv"
        """
        # Delete by instructor
        self.login(**ins_cred)
        self._delete_assignment_helper(
            "Assignment 7", status.HTTP_204_NO_CONTENT, assign_type
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsOwner` permissioon class
        self._delete_assignment_helper(
            "Assignment 8", status.HTTP_401_UNAUTHORIZED, assign_type
        )

        # Delete by ta
        self.login(**ta_cred)
        self._delete_assignment_helper(
            "Assignment 9", status.HTTP_204_NO_CONTENT, assign_type
        )
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permissioon class (delete by student)
        self.login(**stu_cred)
        self._delete_assignment_helper(
            "Assignment 10", status.HTTP_403_FORBIDDEN, assign_type
        )
        self.logout()

    def test_delete_simple_assignment(self):
        self._delete_simple_or_advanced_assignment_helper("simple")

    def test_delete_advanced_assignment(self):
        self._delete_simple_or_advanced_assignment_helper("adv")


class AssignmentSectionViewSetTest(APITestCase):
    """Test for `AssignmentSectionViewSet`."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "simpleprogrammingassignment.test.yaml",
        "advancedprogrammingassignment.test.yaml",
        "assignmentsection.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_section_helper(self, assignment_id, name, description, status_code):
        """Helper function for `test_create_section()`.

        Args:
            assignment_id (int): Assignment id
            name (str): Name of the section
            description (str): Description of the section
            status_code (int): Expected status code of the API call
        """
        data = {
            "assignment": assignment_id,
            "name": name,
            "description": description,
        }
        url = reverse("programming_assignments:assignmentsection-create-section")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["assignment"], data["assignment"])
            self.assertEqual(response_data["name"], data["name"])
            self.assertEqual(response_data["description"], data["description"])

    def test_create_section(self):
        """Test: create a section."""
        assignment_id = 1

        # Created by instructor
        self.login(**ins_cred)
        self._create_section_helper(
            assignment_id, "Section 1", "Description section 1", status.HTTP_201_CREATED
        )
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_section_helper(
            assignment_id, "Section 2", "Description section 2", status.HTTP_201_CREATED
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_section_helper(
            assignment_id, "", "Description section 3", status.HTTP_400_BAD_REQUEST
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._create_section_helper(
            assignment_id,
            "Section 4",
            "Description section 4",
            status.HTTP_401_UNAUTHORIZED,
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._create_section_helper(
            assignment_id,
            "Section 5",
            "Description section 5",
            status.HTTP_403_FORBIDDEN,
        )
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        assignment_id = 3
        self.login(**ins_cred)
        self._create_section_helper(
            assignment_id,
            "Section 6",
            "Description section 6",
            status.HTTP_403_FORBIDDEN,
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to
        # `SimpleProgrammingAssignment.DoesNotExist` exception
        assignment_id = 100
        self.login(**stu_cred)
        self._create_section_helper(
            assignment_id,
            "Section 7",
            "Description section 7",
            status.HTTP_404_NOT_FOUND,
        )
        self.logout()

    def _list_sections_helper(self, assignment_id, status_code, user_id):
        """Helper function for `test_list_sections()`.

        Args:
            assignment_id (int): Assignment id
            status_code (int): Expected status code of the API call
            user_id (int): User id
        """
        url = reverse(
            "programming_assignments:assignmentsection-list-sections",
            args=[assignment_id],
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)

        if status_code == status.HTTP_200_OK:
            if user_id == 3:
                assignment = SimpleProgrammingAssignment.objects.get(id=assignment_id)
                if assignment.is_published == "True":
                    self.assertEqual(
                        len(response.data),
                        AssignmentSection.objects.filter(
                            assignment=assignment_id, section_type="V"
                        ).count(),
                    )
            else:
                self.assertEqual(
                    len(response.data),
                    AssignmentSection.objects.filter(assignment=assignment_id).count(),
                )

    def test_list_sections(self):
        """Test: list all sections."""
        assignment_id = 1

        # List by instructor
        self.login(**ins_cred)
        self._list_sections_helper(assignment_id, status.HTTP_200_OK, 1)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_sections_helper(assignment_id, status.HTTP_200_OK, 2)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._list_sections_helper(assignment_id, status.HTTP_401_UNAUTHORIZED, 1)

        # List by student
        self.login(**stu_cred)
        self._list_sections_helper(assignment_id, status.HTTP_200_OK, 3)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to
        # `SimpleProgrammingAssignment.DoesNotExist` exception
        assignment_id = 100
        self.login(**stu_cred)
        self._list_sections_helper(assignment_id, status.HTTP_404_NOT_FOUND, 3)
        self.logout()

    def _retrieve_section_helper(self, section_id, status_code, user_id):
        """Helper function for `test_retrieve_section()`.

        Args:
            section_id (int): Section id
            status_code (int): Expected status code of the API call
            user_id (int): User id
        """
        url = reverse(
            "programming_assignments:assignmentsection-retrieve-section",
            args=[section_id],
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            section = AssignmentSection.objects.get(id=section_id)
            if user_id == 3:
                if (
                    section.section_type == "V"
                    and section.assignment.is_published == "True"
                ):
                    self.assertEqual(response.data["id"], section_id)
            else:
                self.assertEqual(response.data["id"], section_id)

    def test_retrieve_section(self):
        """Test: retrieve the section."""
        section_id = 1

        # Retrieve by instructor
        self.login(**ins_cred)
        self._retrieve_section_helper(section_id, status.HTTP_200_OK, 1)
        self.logout()

        # Retrieve by ta
        self.login(**ta_cred)
        self._retrieve_section_helper(section_id, status.HTTP_200_OK, 2)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `StrictIsInstructorOrTA`/`IsOwner` permission
        # class
        self._retrieve_section_helper(section_id, status.HTTP_401_UNAUTHORIZED, 1)

        # Retrive by student
        self.login(**stu_cred)
        self._retrieve_section_helper(section_id, status.HTTP_200_OK, 3)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        section_id = 100
        self.login(**ta_cred)
        self._retrieve_section_helper(section_id, status.HTTP_404_NOT_FOUND, 2)
        self.logout()

    def _update_section_helper(
        self, section_id, assignment_id, name, description, status_code, method
    ):
        """Helper function for `test_update_section()` and `test_partial_update_section()`.

        Args:
            section_id (int): Section id
            assignment_id (int): Assignment id
            name (str): Name of the section
            description (str): Description of the section
            status_code (int): Expected status code of the API call
            method: HTTP method ("PUT or "PATCH")
        """
        data = {
            "assignment": assignment_id,
            "name": name,
            "description": description,
        }
        url = reverse(
            "programming_assignments:assignmentsection-update-section",
            args=[section_id],
        )

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["assignment"], data["assignment"])
            self.assertEqual(response_data["name"], data["name"])
            self.assertEqual(response_data["description"], data["description"])

    def _put_or_patch(self, method):
        """Test: update a section."""
        section_id = 1
        assignment_id = 1

        # Update by instructor
        self.login(**ins_cred)
        self._update_section_helper(
            section_id,
            assignment_id,
            "Section 1",
            "Description section 1",
            status.HTTP_200_OK,
            method,
        )
        self.logout()

        # Update by ta
        self.login(**ta_cred)
        self._update_section_helper(
            section_id,
            assignment_id,
            "Section 1",
            "Description section 1",
            status.HTTP_200_OK,
            method,
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_section_helper(
            section_id,
            assignment_id,
            "",
            "Description section 1",
            status.HTTP_400_BAD_REQUEST,
            method,
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._update_section_helper(
            section_id,
            assignment_id,
            "Section 1",
            "Description section 1",
            status.HTTP_401_UNAUTHORIZED,
            method,
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._update_section_helper(
            section_id,
            assignment_id,
            "Section 1",
            "Description section 1",
            status.HTTP_403_FORBIDDEN,
            method,
        )
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        section_id = 2
        self.login(**ins_cred)
        self._update_section_helper(
            section_id,
            assignment_id,
            "Section 1",
            "Description section 1",
            status.HTTP_403_FORBIDDEN,
            method,
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to
        # `SimpleProgrammingAssignment.DoesNotExist` exception
        section_id = 100
        self.login(**stu_cred)
        self._update_section_helper(
            section_id,
            assignment_id,
            "Section 1",
            "Description section 1",
            status.HTTP_404_NOT_FOUND,
            method,
        )
        self.logout()

    def test_update_section(self):
        """Test: update the section."""
        self._put_or_patch("PUT")

    def test_partial_update_section(self):
        """Test: partial update the section."""
        self._put_or_patch("PATCH")

    def _delete_section_helper(self, name, description, status_code):
        """Helper function for `test_delete_section()`.

        Args:
            name (str): Name of the section
            description (str): Description of the section
            status_code (int): Expected status code of the API call
        """
        section_id = AssignmentSection.objects.create(
            assignment_id=1, name=name, description=description
        ).id
        url = reverse(
            ("programming_assignments:assignmentsection-delete-section"),
            args=[section_id],
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(AssignmentSection.objects.filter(id=section_id).count(), 0)

    def test_delete_section(self):
        """Test: delete the section."""
        # Deleted by instructor
        self.login(**ins_cred)
        self._delete_section_helper(
            "Section 1", "section 1 description", status.HTTP_204_NO_CONTENT
        )
        self.logout()

        # Deleted by ta
        self.login(**ta_cred)
        self._delete_section_helper(
            "Section 2", "section 2 description", status.HTTP_204_NO_CONTENT
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._delete_section_helper(
            "Section 3", "section 3 description", status.HTTP_401_UNAUTHORIZED
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._delete_section_helper(
            "Section 4", "section 4 description", status.HTTP_403_FORBIDDEN
        )
        self.logout()
