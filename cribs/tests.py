from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .models import Crib


ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
stu_cred = {"email": "student@bodhitree.com", "password": "student"}


class CribViewSetTest(APITestCase):
    """Test for CribViewSet."""

    fixtures = [
        "users.test.yaml",
        "colleges.test.yaml",
        "departments.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "cribs.test.yaml",
        "cribreply.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_cribs_helper(self, course_id, created_by, title, status_code):
        """Helper function for `test_create_crib()`.
        Args:
            course_id (int): Course id
            created_by (str): Creator of the Crib
            title (str): Title of the crib
            status_code (int): Expected status code of the API call
        """
        data = {
            "course": course_id,
            "created_by": created_by,
            "assigned_to": 1,
            "title": title,
            "description": "This is the description of the crib",
        }
        url = reverse("cribs:crib-create-crib")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["created_by"], data["created_by"])
            self.assertEqual(response_data["assigned_to"], data["assigned_to"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def test_create_crib(self):
        """Test: create a crib."""
        course_id = 1

        # Created by student
        self.login(**stu_cred)
        self._create_cribs_helper(course_id, 3, "Crib 1", status.HTTP_201_CREATED)
        self.logout()

        # HTTP_400_BAD_REQUEST due to is_valid()
        self.login(**stu_cred)
        self._create_cribs_helper(course_id, 3, "", status.HTTP_400_BAD_REQUEST)
        self.logout()

        # HTTP_401_UNAUTHORIZED due to IsInstructorOrTAorStudent
        self._create_cribs_helper(course_id, 3, "Crib 3", status.HTTP_401_UNAUTHORIZED)

        # HTTP_403_FORBIDDEN due to _is_registered()
        self.login(**stu_cred)
        self._create_cribs_helper(2, 3, "Crib 4", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _list_cribs_helper(self, course_id, status_code):
        """Helper function for `test_list_cribs()`.

        Args:
            course_id (int): Course id
            status_code (int): Expected status code of the API call
        """
        url = reverse("cribs:crib-list-cribs", args=[course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data["results"]),
                Crib.objects.filter(course_id=course_id).count(),
            )

    def test_list_cribs(self):
        """Test: list all cribs."""
        course_id = 1  # course with id 1 is created by django fixture

        # List by instructor
        self.login(**ins_cred)
        self._list_cribs_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_cribs_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # HTTP_401_UNAUTHORIZED due to IsInstructorOrTAOrStudent
        self._list_cribs_helper(course_id, status.HTTP_401_UNAUTHORIZED)

        # HTTP_403_FORBIDDEN due to _is_instructor_or_ta()
        self.login(**stu_cred)
        self._list_cribs_helper(course_id, status.HTTP_403_FORBIDDEN)
        self.logout()

    def _retrieve_crib_helper(self, crib_id, status_code):
        """Helper function for `test_retrieve_crib()`.
        Args:
            crib_id (int): Crib id
            status_code (int): Expected status code of the API call
        """
        url = reverse("cribs:crib-retrieve-crib", args=[crib_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], crib_id)

    def test_retrieve_crib(self):
        """Test: retrieve the crib."""
        crib_id = 1  # chapter with id 1 is created by django fixture

        # Retrieve by instructor
        self.login(**ins_cred)
        self._retrieve_crib_helper(crib_id, status.HTTP_200_OK)
        self.logout()

        # Retrieve by ta
        self.login(**ta_cred)
        self._retrieve_crib_helper(crib_id, status.HTTP_200_OK)
        self.logout()

        # Retrieve by student who is owner of crib
        self.login(**stu_cred)
        self._retrieve_crib_helper(3, status.HTTP_200_OK)
        self.logout()

        # HTTP_401_UNAUTHORIZED due to IsInstructorOrTA
        self._retrieve_crib_helper(crib_id, status.HTTP_401_UNAUTHORIZED)

        # Retrieve by student who is not owner of crib
        self.login(**stu_cred)
        self._retrieve_crib_helper(crib_id, status.HTTP_403_FORBIDDEN)
        self.logout()

    def _update_cribs_helper(self, crib_id, title, status_code, method):
        """Helper function for `test_update_crib()` & `test_partial_update_crib()`.
        Args:
            crib_id (int): Crib id
            title (str): Title of the crib
            status_code (int): Expected status code of the API call
            method (str): HTTP method ("PUT" or "PATCH")
        """
        course_id = 1  # course with id 1 is created by django fixture
        data = {
            "course": course_id,
            "title": title,
            "assigned_to": 1,
            "description": "Description of the crib",
        }
        url = reverse(("cribs:crib-update-crib"), args=[crib_id])

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["assigned_to"], data["assigned_to"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def _put_or_patch(self, method):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
        """
        crib_id = Crib.objects.create(
            course_id=1, created_by_id=3, assigned_to_id=1, title="Crib 1"
        ).id

        # Update by student
        self.login(**stu_cred)
        self._update_cribs_helper(crib_id, "Crib 2", status.HTTP_200_OK, method)
        self.logout()

        # HTTP_403_FORBIDDEN due to `IsOwner` permission class
        self.login(**ins_cred)
        self._update_cribs_helper(crib_id, "Crib 3", status.HTTP_403_FORBIDDEN, method)
        self.logout()

        # HTTP_403_FORBIDDEN due to `IsOwner` permission class
        self.login(**ta_cred)
        self._update_cribs_helper(crib_id, "Crib 3", status.HTTP_403_FORBIDDEN, method)
        self.logout()

        # HTTP_400_BAD_REQUEST due to is_valid()
        self.login(**stu_cred)
        self._update_cribs_helper(crib_id, "", status.HTTP_400_BAD_REQUEST, method)
        self.logout()

        # HTTP_401_UNAUTHORIZED due to IsOwner
        self._update_cribs_helper(
            crib_id, "Crib 4", status.HTTP_401_UNAUTHORIZED, method
        )

    def test_update_crib(self):
        """Test: update the crib."""
        self._put_or_patch("PUT")

    def test_partial_update_crib(self):
        """Test: partial update the crib."""
        self._put_or_patch("PATCH")
