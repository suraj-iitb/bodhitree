from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory, APITestCase

from course.models import Chapter
from registration.models import User
from utils.permissions import IsInstructorOrTA


class IsInstructorOrTATest(APITestCase):
    """Test for `IsInstructorOrTA` permission class."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "chapters.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = IsInstructorOrTA()

        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

        cls.chapter = Chapter.objects.get(id=1)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), False],
        ]

    def _permisison_helper(self, request, user_permissions, obj=None):
        """Helper class for `has_permission()` & `has_object_permission()` method.

        Args:
            request (Request): DRF `Request` object
            user_permissions (tuple): A 2-dimensional tuple where first column is
                `User` instance & second column is its permission.
            obj (Model, optional): `Model` instance (like Chapter, Section etc.).
                Defaults to None.
        """
        for user, assert_true in user_permissions:
            request.user = user
            if obj is None:
                permission = self.permission_class.has_permission(request, None)
            else:
                permission = self.permission_class.has_object_permission(
                    request, None, self.chapter
                )
            if assert_true:
                self.assertTrue(permission)
            else:
                self.assertFalse(permission)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._permisison_helper(request, self.user_permissions)
        self._permisison_helper(request, self.user_permissions, self.chapter)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self._permisison_helper(request, self.user_permissions)
        self.user_permissions[2][1] = False
        self._permisison_helper(request, self.user_permissions, self.chapter)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._permisison_helper(request, self.user_permissions)
        self.user_permissions[2][1] = False
        self._permisison_helper(request, self.user_permissions, self.chapter)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._permisison_helper(request, self.user_permissions)
        self.user_permissions[2][1] = False
        self._permisison_helper(request, self.user_permissions, self.chapter)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._permisison_helper(request, self.user_permissions)
        self.user_permissions[2][1] = False
        self._permisison_helper(request, self.user_permissions, self.chapter)
