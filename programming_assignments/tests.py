from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from utils import credentials

from .models import SimpleProgrammingAssignment


ins_cred = credentials.TEST_INSTRUCTOR_CREDENTIALS
ta_cred = credentials.TEST_TA_CREDENTIALS
stu_cred = credentials.TEST_STUDENT_CREDENTIALS


class SimpleProgrammingAssignmentViewSetTest(APITestCase):
    """Test for `SimpleProgrammingAssignmentViewSet`."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "simpleprogrammingassignment.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_simple_prog_assignment_helper(self, name, status_code):
        """Helper function `test_create_simple_prog_assignment()`.

        Args:
            name (str): name of the assignment
            status_code (int): Expected status code of the API call
        """
        programming_language = "C"
        course_id = 1
        start_date = "2021-10-25T14:30:59+05:30"
        end_date = "2021-11-25T14:30:59+05:30"
        extended_date = "2021-11-25T14:30:59+05:30"

        data = {
            "course": course_id,
            "programming_language": programming_language,
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "extended_date": extended_date,
        }
        url = reverse(
            "programming_assignments:simpleprogrammingassignment-create-assignment"
        )

        response = self.client.post(url, data)
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

    def test_create_simple_prog_assignment(self):
        """Test: create an assignment."""
        # Created by instructor
        self.login(**ins_cred)
        self._create_simple_prog_assignment_helper(
            "Assignment 1",
            status.HTTP_201_CREATED,
        )
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_simple_prog_assignment_helper(
            "Assignment 2",
            status.HTTP_201_CREATED,
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_simple_prog_assignment_helper(
            "",
            status.HTTP_400_BAD_REQUEST,
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._create_simple_prog_assignment_helper(
            "Assignment 3",
            status.HTTP_401_UNAUTHORIZED,
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._create_simple_prog_assignment_helper(
            "Assignment 4",
            status.HTTP_403_FORBIDDEN,
        )
        self.logout()

    def _list_assignments_helper(self, course_id, user_id, status_code):
        """Helper function for `test_list_assignments()`.

        Args:
            course_id (int): Course id
            user_id (int): User id
            status_code (int): Expected status code of the API call
        """
        stud_url = (
            "programming_assignments:simpleprogrammingassignment-list-assignments-stud"
        )
        if user_id != 3:
            url = reverse(
                "programming_assignments:simpleprogrammingassignment-list-assignments",
                args=[course_id],
            )
        else:
            url = reverse(
                stud_url,
                args=[course_id],
            )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK and user_id == 3:
            self.assertEqual(
                len(response.data),
                SimpleProgrammingAssignment.objects.filter(
                    course=course_id, is_published=True
                ).count(),
            )
        elif status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data),
                SimpleProgrammingAssignment.objects.filter(course_id=course_id).count(),
            )

    def test_list_assignments(self):
        """Test: list all assignments."""
        course_id = 1

        # List by instructor
        self.login(**ins_cred)
        self._list_assignments_helper(course_id, 1, status.HTTP_200_OK)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_assignments_helper(course_id, 2, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._list_assignments_helper(course_id, 2, status.HTTP_401_UNAUTHORIZED)

        # List by student
        self.login(**stu_cred)
        self._list_assignments_helper(course_id, 3, status.HTTP_200_OK)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        # List by student
        course_id = 100
        self.login(**stu_cred)
        self._list_assignments_helper(course_id, 3, status.HTTP_404_NOT_FOUND)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        # List by instructor
        self.login(**ins_cred)
        self._list_assignments_helper(course_id, 1, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _retrieve_assignment_helper(self, assignment_id, status_code):
        """Helper function for `test_retrieve_assignments()`.

        Args:
            assignment_id (int): Assignment id
            status_code (int): Expected status code of the API call
        """
        url = reverse(
            "programming_assignments:simpleprogrammingassignment-retrieve-assignment",
            args=[assignment_id],
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], assignment_id)

    def test_retrieve_assignments(self):
        """Test: retrieve an assignment."""
        assignment_id = 1

        # Retrieve by instructor
        self.login(**ins_cred)
        self._retrieve_assignment_helper(assignment_id, status.HTTP_200_OK)
        self.logout()

        # Retrieve by ta
        self.login(**ta_cred)
        self._retrieve_assignment_helper(assignment_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._retrieve_assignment_helper(assignment_id, status.HTTP_401_UNAUTHORIZED)

        # Retrieve by student
        self.login(**stu_cred)
        self._retrieve_assignment_helper(assignment_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        # Retrieve by student
        assignment_id = 100
        self.login(**stu_cred)
        self._retrieve_assignment_helper(assignment_id, status.HTTP_404_NOT_FOUND)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        # Retrieve by instructor
        self.login(**ins_cred)
        self._retrieve_assignment_helper(assignment_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _update_simple_prog_assignment_helper(
        self, assignment_id, name, status_code, method
    ):
        """Helper function `test_update_assignment()` `and test_partial_update_assignment()`.

        Args:
            assignment_id (int): Assignment id
            name (str): name of the assignment
            status_code (int): Expected status code of the API call
            method: HTTP method ("PUT or "PATCH")
        """
        programming_language = "C"
        course_id = 1
        start_date = "2021-10-25T14:30:59+05:30"
        end_date = "2021-11-25T14:30:59+05:30"
        extended_date = "2021-11-25T14:30:59+05:30"

        data = {
            "course": course_id,
            "programming_language": programming_language,
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "extended_date": extended_date,
        }
        url = reverse(
            "programming_assignments:simpleprogrammingassignment-update-assignment",
            args=[assignment_id],
        )

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
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

    def _put_or_patch(self, method):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
        """
        assignment_id = SimpleProgrammingAssignment.objects.create(
            course_id=1,
            programming_language="C",
            name="Assignment test",
            start_date="2021-10-25T14:30:59+05:30",
            end_date="2021-11-25T14:30:59+05:30",
            extended_date="2021-12-25T14:30:59+05:30",
        ).id

        # Update by instructor
        self.login(**ins_cred)
        self._update_simple_prog_assignment_helper(
            assignment_id, "Assignment 1", status.HTTP_200_OK, method
        )
        self.logout()

        # Update by ta
        self.login(**ta_cred)
        self._update_simple_prog_assignment_helper(
            1, "Assignment 2", status.HTTP_200_OK, method
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_simple_prog_assignment_helper(
            1, "", status.HTTP_400_BAD_REQUEST, method
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._update_simple_prog_assignment_helper(
            1, "Assignment 3", status.HTTP_401_UNAUTHORIZED, method
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._update_simple_prog_assignment_helper(
            1, "Assignment 4", status.HTTP_403_FORBIDDEN, method
        )
        self.logout()

    def test_update_assignment(self):
        """Test: update the assignment."""
        self._put_or_patch("PUT")

    def test_partial_update_assignment(self):
        """Test: partial update the assignment."""
        self._put_or_patch("PATCH")

    def _delete_assignment_helper(self, name, status_code):
        """Helper function for `test_delete_course()`.

        Args:
            name (str): name of the assignment
            status_code (int): Expected status code of the API call
        """
        assignment = SimpleProgrammingAssignment.objects.create(
            course_id=1,
            programming_language="C++",
            name=name,
            start_date="2021-10-25T14:30:59+05:30",
            end_date="2021-11-25T14:30:59+05:30",
            extended_date="2021-12-25T14:30:59+05:30",
        )
        assignment.save()

        url = reverse(
            ("programming_assignments:simpleprogrammingassignment-delete-assignment"),
            args=[assignment.id],
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(
                SimpleProgrammingAssignment.objects.filter(id=assignment.id).count(), 0
            )

    def test_delete_assignment(self):
        """Test: delete the assignment."""
        # Delete by instructor
        self.login(**ins_cred)
        self._delete_assignment_helper("Assignment 7", status.HTTP_204_NO_CONTENT)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsOwner` permissioon class
        self._delete_assignment_helper("Assignment 8", status.HTTP_401_UNAUTHORIZED)

        # Delete by ta
        self.login(**ta_cred)
        self._delete_assignment_helper("Assignment 9", status.HTTP_204_NO_CONTENT)
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permissioon class (delete by student)
        self.login(**stu_cred)
        self._delete_assignment_helper("Assignment 10", status.HTTP_403_FORBIDDEN)
        self.logout()
