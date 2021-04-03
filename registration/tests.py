from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from registration.models import User


class UserViewSetTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.user1 = User.objects.create_user("test1@test.com", "Test@1001")
        cls.user1.save()
        cls.user2 = User.objects.create_user("test2@test.com", "Test@1002")
        cls.user2.save()

    def test_get_users(self):
        """
        Ensure we can get all User objects.
        """
        url = reverse("registration:user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user(self):
        """
        Ensure we can get one User object.
        """
        url = reverse("registration:user-detail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        """
        Ensure we can create a new User object.
        """
        data = {"email": "test3@test.com", "password": "Test@1003"}
        url = reverse("registration:user-list")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
