from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class UserViewSetTests(APITestCase):
    """Test for UserViewSet."""

    def test_create_user(self):
        """Test to check: list all section videos."""
        data = {
            "email": "test@test.com",
            "password": "Test@1001",
        }
        url = reverse("registration:user-create-user")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data["email"], data["email"])
