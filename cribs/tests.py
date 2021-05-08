from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from utils import credentials

from .models import Crib, CribReply


ins_cred = credentials.TEST_INSTRUCTOR_CREDENTIALS
ta_cred = credentials.TEST_TA_CREDENTIALS
stu_cred = credentials.TEST_STUDENT_CREDENTIALS


class CribViewSetTest(APITestCase):
    """Test for `CribViewSet`."""

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
            created_by (str): Creator of the crib
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

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**stu_cred)
        self._create_cribs_helper(course_id, 3, "", status.HTTP_400_BAD_REQUEST)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAorStudent` permission class
        self._create_cribs_helper(course_id, 3, "Crib 3", status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        course_id = 2
        self.login(**stu_cred)
        self._create_cribs_helper(course_id, 3, "Crib 4", status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Crib.DoesNotExist` exception
        course_id = 100
        self.login(**stu_cred)
        self._create_cribs_helper(course_id, 3, "Crib 5", status.HTTP_404_NOT_FOUND)
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
        course_id = 1

        # List by instructor
        self.login(**ins_cred)
        self._list_cribs_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_cribs_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAOrStudent` permission class
        self._list_cribs_helper(course_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._list_cribs_helper(course_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        course_id = 100
        self.login(**stu_cred)
        self._list_cribs_helper(course_id, status.HTTP_404_NOT_FOUND)
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
        crib_id = 1

        # Retrieve by instructor
        self.login(**ins_cred)
        self._retrieve_crib_helper(crib_id, status.HTTP_200_OK)
        self.logout()

        # Retrieve by ta
        self.login(**ta_cred)
        self._retrieve_crib_helper(crib_id, status.HTTP_200_OK)
        self.logout()

        # Retrieve by student who is owner of crib
        crib_id = 3
        self.login(**stu_cred)
        self._retrieve_crib_helper(crib_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `StrictIsInstructorOrTA`/`IsOwner` permission
        # class
        self._retrieve_crib_helper(crib_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `StrictIsInstructorOrTA`/`IsOwner` permission
        # class
        crib_id = 1
        self.login(**stu_cred)
        self._retrieve_crib_helper(crib_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        course_id = 100
        self.login(**stu_cred)
        self._list_cribs_helper(course_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _update_cribs_helper(self, crib_id, title, status_code, method):
        """Helper function for `test_update_crib()` & `test_partial_update_crib()`.

        Args:
            crib_id (int): Crib id
            title (str): Title of the crib
            status_code (int): Expected status code of the API call
            method (str): HTTP method ("PUT" or "PATCH")
        """
        course_id = 1
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

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**stu_cred)
        self._update_cribs_helper(crib_id, "", status.HTTP_400_BAD_REQUEST, method)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsOwner` permission class
        self._update_cribs_helper(
            crib_id, "Crib 4", status.HTTP_401_UNAUTHORIZED, method
        )

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permission class
        self.login(**ins_cred)
        self._update_cribs_helper(crib_id, "Crib 3", status.HTTP_403_FORBIDDEN, method)
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permission class
        self.login(**ta_cred)
        self._update_cribs_helper(crib_id, "Crib 3", status.HTTP_403_FORBIDDEN, method)
        self.logout()

    def test_update_crib(self):
        """Test: update the crib."""
        self._put_or_patch("PUT")

    def test_partial_update_crib(self):
        """Test: partial update the crib."""
        self._put_or_patch("PATCH")


class CribReplyViewSetTest(APITestCase):
    """Test for `CribReplyViewSet`."""

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

    def _create_crib_reply_helper(self, crib_id, user, status_code):
        """Helper function for `test_create_crib_reply()`.

        Args:
            crib_id (int): Crib id
            user (str): Creator of the crib reply
            status_code (int): Expected status code of the API call
        """
        data = {
            "crib": crib_id,
            "user": user,
            "description": "This is the description of the crib",
        }
        url = reverse("cribs:cribreply-create-crib-reply")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["crib"], data["crib"])
            self.assertEqual(response_data["user"], data["user"])
            self.assertEqual(response_data["description"], data["description"])

    def test_create_crib_reply(self):
        """Test: create a crib."""
        crib_id = 1

        # Created by instructor
        self.login(**ins_cred)
        self._create_crib_reply_helper(crib_id, 1, status.HTTP_201_CREATED)
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_crib_reply_helper(crib_id, 2, status.HTTP_201_CREATED)
        self.logout()

        # Created by student
        self.login(**stu_cred)
        self._create_crib_reply_helper(crib_id, 3, status.HTTP_201_CREATED)
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**stu_cred)
        self._create_crib_reply_helper(crib_id, 6, status.HTTP_400_BAD_REQUEST)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAorStudent` permission class
        self._create_crib_reply_helper(crib_id, 3, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        crib_id = 4
        self.login(**stu_cred)
        self._create_crib_reply_helper(crib_id, 3, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Crib.DoesNotExist` exception
        crib_id = 100
        self.login(**stu_cred)
        self._create_crib_reply_helper(crib_id, 3, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _list_crib_replies_helper(self, crib_id, status_code):
        """Helper function for `test_list_crib_replies()`.

        Args:
            crib_id (int): Crib id
            status_code (int): Expected status code of the API call
        """
        url = reverse("cribs:cribreply-list-crib-replies", args=[crib_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data["results"]),
                CribReply.objects.filter(crib=crib_id).count(),
            )

    def test_list_crib_replies(self):
        """Test: list all crib replies."""
        crib_id = 1

        # List by instructor
        self.login(**ins_cred)
        self._list_crib_replies_helper(crib_id, status.HTTP_200_OK)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_crib_replies_helper(crib_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAOrStudent` permission class
        self._list_crib_replies_helper(crib_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to Non-owner student
        self.login(**stu_cred)
        self._list_crib_replies_helper(crib_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Crib.DoesNotExist` exception
        crib_id = 100
        self.login(**stu_cred)
        self._list_crib_replies_helper(crib_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _retrieve_crib_reply_helper(self, crib_reply_id, status_code):
        """Helper function for `test_retrieve_crib_reply()`.

        Args:
            crib_reply_id (int): Crib reply id
            status_code (int): Expected status code of the API call
        """
        url = reverse("cribs:cribreply-retrieve-crib-reply", args=[crib_reply_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], crib_reply_id)

    def test_retrieve_crib_reply(self):
        """Test: retrieve the crib reply."""
        crib_reply_id = 1

        # Retrieve by instructor
        self.login(**ins_cred)
        self._retrieve_crib_reply_helper(crib_reply_id, status.HTTP_200_OK)
        self.logout()

        # Retrieve by ta
        self.login(**ta_cred)
        self._retrieve_crib_reply_helper(crib_reply_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `StrictIsInstructorOrTA`/`IsOwner` permission
        # class
        self._retrieve_crib_reply_helper(crib_reply_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to student who is not owner of crib
        self.login(**stu_cred)
        self._retrieve_crib_reply_helper(crib_reply_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        crib_reply_id = 100
        self.login(**ta_cred)
        self._retrieve_crib_reply_helper(crib_reply_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _update_crib_reply_helper(
        self, crib_reply_id, user, description, status_code, method
    ):
        """Helper function for `test_update_crib_reply()` & `test_partial_update_crib_reply()`.

        Args:
            crib_reply_id (int): Crib reply id
            user (str): Title of the crib
            status_code (int): Expected status code of the API call
            method (str): HTTP method ("PUT" or "PATCH")
        """
        crib_id = 1
        data = {
            "crib": crib_id,
            "user": user,
            "description": description,
        }
        url = reverse(("cribs:cribreply-update-crib-reply"), args=[crib_reply_id])

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["crib"], data["crib"])
            self.assertEqual(response_data["user"], data["user"])
            self.assertEqual(response_data["description"], data["description"])

    def _put_or_patch(self, method):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
        """
        crib_reply_id = CribReply.objects.create(
            crib_id=1, user_id=3, description="Crib 1"
        ).id

        # Update by student
        self.login(**stu_cred)
        self._update_crib_reply_helper(
            crib_reply_id, 3, "Crib reply 2", status.HTTP_200_OK, method
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsOwner` permission class
        self._update_crib_reply_helper(
            crib_reply_id, 3, "Crib reply 5", status.HTTP_401_UNAUTHORIZED, method
        )

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permission class
        self.login(**ta_cred)
        self._update_crib_reply_helper(
            crib_reply_id, 2, "Crib reply 3", status.HTTP_403_FORBIDDEN, method
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        crib_reply_id = 100
        self.login(**ta_cred)
        self._update_crib_reply_helper(
            crib_reply_id, 2, "Crib reply 3", status.HTTP_404_NOT_FOUND, method
        )
        self.logout()

    def test_update_crib_reply(self):
        """Test: update the crib reply."""
        self._put_or_patch("PUT")

    def test_partial_update_crib_reply(self):
        """Test: partial update the crib reply."""
        self._put_or_patch("PATCH")
