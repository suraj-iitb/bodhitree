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
        self.client.login(email="test1@test.com", password="Test@1001")
        url = reverse("registration:user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user(self):
        """
        Ensure we can get one User object.
        """
        self.client.login(email="test1@test.com", password="Test@1001")
        url = reverse(
            "registration:user-detail", kwargs={"pk": UserViewSetTests.user1.id}
        )
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

    def test_update_user(self):
        """
        Ensure we can update a User object.
        """
        user = User.objects.create_user("test3@test.com", "Test@1003")
        user.save()
        self.client.login(email="test3@test.com", password="Test@1003")
        data = {"email": "test4@test.com", "password": "Test@1004"}
        url = reverse(("registration:user-detail"), kwargs={"pk": user.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_user(self):
        """
        Ensure we can partial update a User object.
        """
        user = User.objects.create_user("test5@test.com", "Test@1005")
        user.save()
        self.client.login(email="test5@test.com", password="Test@1005")
        data = {
            "email": "test6@test.com",
        }
        url = reverse(("registration:user-detail"), kwargs={"pk": user.id})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self):
        """
        Ensure we can delete a User object.
        """
        user = User.objects.create_user("test7@test.com", "Test@1007")
        user.save()
        self.client.login(email="test7@test.com", password="Test@1007")
        url = reverse(("registration:user-detail"), kwargs={"pk": user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
