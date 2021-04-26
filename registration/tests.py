from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from registration.models import User


class UserViewSetTests(APITestCase):
    fixtures = [
        "users.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
        cls.ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
        cls.stu_cred = {"email": "student@bodhitree.com", "password": "student"}

    # def test_get_users(self):
    #     """
    #     Ensure we can get all User objects.
    #     """
    #     self.login(**self.ins_cred)
    #     url = reverse("registration:user-list")
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     length = User.objects.count()
    #     self.assertEqual(len(response.data["results"]), length)
    #     self.logout()

    def test_get_user(self):
        """
        Ensure we can get one User object.
        """
        self.login(**self.ins_cred)
        url = reverse("registration:user-detail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)
        self.logout()

    def test_create_user(self):
        """
        Ensure we can create a new User object.
        """
        data = {"email": "test3@test.com", "password": "Test@1003"}
        url = reverse("registration:user-list")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return_data = response.data
        for k in ["id", "full_name", "is_active", "date_joined", "last_login"]:
            return_data.pop(k)
        data.pop("password")
        self.assertEqual(return_data, data)

    def test_update_user(self):
        """
        Ensure we can update a User object.
        """
        self.client.login(**self.ins_cred)
        data = {"email": "test4@test.com", "password": "Test@1004"}
        url = reverse(("registration:user-detail"), kwargs={"pk": 1})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.data
        for k in ["id", "full_name", "is_active", "date_joined", "last_login"]:
            return_data.pop(k)
        data.pop("password")
        self.assertEqual(return_data, data)
        self.logout()

    def test_partial_update_user(self):
        """
        Ensure we can partial update a User object.
        """
        self.client.login(**self.ins_cred)
        data = {
            "email": "test6@test.com",
        }
        url = reverse(("registration:user-detail"), kwargs={"pk": 1})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.data
        for k in ["id", "full_name", "is_active", "date_joined", "last_login"]:
            return_data.pop(k)
        self.assertEqual(return_data, data)
        self.logout()

    def test_delete_user(self):
        """
        Ensure we can delete a User object.
        """
        user = User.objects.create_user("test7@test.com", "Test@1007")
        user.save()
        self.client.login(email="test7@test.com", password="Test@1007")
        url = reverse(("registration:user-detail"), kwargs={"pk": user.id})
        response = self.client.delete(url)
        try:
            User.objects.get(id=user.id)
        except ObjectDoesNotExist:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
