from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory, APITestCase

from course.models import Chapter, Course, CourseHistory
from registration.models import SubscriptionHistory
from utils.permissions import (
    IsAdmin,
    IsInstructorOrTA,
    IsInstructorOrTAOrReadOnly,
    IsInstructorOrTAOrStudent,
    IsOwner,
    UserPermission,
)


User = get_user_model()


class PermissionHelperMixin:
    """Helper class for permision class tests."""

    def _permisison_helper(self, request, obj=None):
        """Helper method for `has_permission()` & `has_object_permission()` method.

        Args:
            request (Request): DRF `Request` object
            obj (Model, optional): `Model` instance (`Course`, 'Chapter` etc.).
                Defaults to None.
        """
        for user, assert_true in self.user_permissions:
            request.user = user
            if obj is None:
                permission = self.permission_class.has_permission(request, None)
            else:
                permission = self.permission_class.has_object_permission(
                    request, None, obj
                )
            if assert_true:
                self.assertTrue(permission)
            else:
                self.assertFalse(permission)


class IsInstructorOrTATest(APITestCase, PermissionHelperMixin):
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

    def _helper(self, request):
        self._permisison_helper(request)
        self.user_permissions[2][1] = False
        self._permisison_helper(request, self.chapter)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._permisison_helper(request)
        self._permisison_helper(request, self.chapter)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)

    def test_get_course_from_object(self):
        """Test `_get_course_from_object()` method."""
        actual_course = self.permission_class._get_course_from_object(self.chapter)
        expected_course = self.chapter.course
        self.assertEqual(actual_course, expected_course)


class IsInstructorOrTAOrReadOnlyTest(APITestCase, PermissionHelperMixin):
    """Test for `IsInstructorOrTAOrReadOnly` permission class."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = IsInstructorOrTAOrReadOnly()

        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

        cls.course = Course.objects.get(id=1)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), True],
        ]

    def _helper(self, request):
        self.user_permissions[3][1] = False
        self._permisison_helper(request)
        self.user_permissions[2][1] = False
        self._permisison_helper(request, self.course)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._permisison_helper(request)
        self._permisison_helper(request, self.course)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self.user_permissions[3][1] = False
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)


class IsInstructorOrTAOrStudentTest(APITestCase, PermissionHelperMixin):
    """Test for `IsInstructorOrTAOrStudent` permission class."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = IsInstructorOrTAOrStudent()

        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

        cls.course_history_inst = CourseHistory.objects.get(id=1)
        cls.course_history_ta = CourseHistory.objects.get(id=2)
        cls.course_history_stud = CourseHistory.objects.get(id=3)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), False],
        ]

    def _helper(self, request):
        self._permisison_helper(request)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self._permisison_helper(request, self.course_history_inst)
        self.user_permissions[0][1] = False
        self.user_permissions[1][1] = True
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self._permisison_helper(request, self.course_history_ta)
        self.user_permissions[0][1] = False
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = True
        self.user_permissions[3][1] = False
        self._permisison_helper(request, self.course_history_stud)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._permisison_helper(request)
        self._permisison_helper(request, self.course_history_inst)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)

    def test_get_user_from_object(self):
        """Test `_get_user_from_object()` method."""
        (
            actual_course,
            actual_user,
        ) = self.permission_class._get_course_and_user_from_object(
            self.course_history_inst
        )
        expected_user = self.course_history_inst.user
        expected_course = self.course_history_inst.course
        self.assertEqual(actual_user, expected_user)
        self.assertEqual(actual_course, expected_course)


class UserPermissionTest(APITestCase, PermissionHelperMixin):
    """Test for `UserPermission` permission class."""

    fixtures = [
        "users.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = UserPermission()

        cls.admin = User.objects.create_superuser(
            email="admin@bodhitree.com", password="admin"
        )
        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.admin, True],
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), False],
        ]

    def _helper(self, request):
        self._permisison_helper(request)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = True
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self.user_permissions[4][1] = False
        self._permisison_helper(request, self.instructor)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = True
        self.user_permissions[3][1] = False
        self.user_permissions[4][1] = False
        self._permisison_helper(request, self.ta)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = True
        self.user_permissions[4][1] = False
        self._permisison_helper(request, self.student)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._helper(request)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self.user_permissions[4][1] = True
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)


class IsAdminTest(APITestCase, PermissionHelperMixin):
    """Test for `IsAdmin` permission class."""

    fixtures = [
        "users.test.yaml",
        "plans.test.yaml",
        "subscriptions.test.yaml",
        "subscriptionhistories.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = IsAdmin()

        cls.admin = User.objects.create_superuser(
            email="admin@bodhitree.com", password="admin"
        )
        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

        cls.subscription_history = SubscriptionHistory.objects.get(id=1)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.admin, True],
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), False],
        ]

    def _helper(self, request):
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self.user_permissions[4][1] = False
        self._permisison_helper(request)
        self._permisison_helper(request, self.subscription_history)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._permisison_helper(request)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = True
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self.user_permissions[4][1] = False
        self._permisison_helper(request, self.subscription_history)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self.user_permissions[4][1] = False
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)


class IsOwnerTest(APITestCase, PermissionHelperMixin):
    """Test for `IsOwner` permission class."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """Allows the creation of initial data at the class level."""
        cls.factory = APIRequestFactory()
        cls.permission_class = IsOwner()

        cls.instructor = User.objects.get(id=1)
        cls.ta = User.objects.get(id=2)
        cls.student = User.objects.get(id=3)

        cls.course = Course.objects.get(id=1)

    def setUp(self):
        """Allows the creation of initial data at the method level."""
        self.user_permissions = [
            [self.instructor, True],
            [self.ta, True],
            [self.student, True],
            [AnonymousUser(), False],
        ]

    def _helper(self, request):
        self._permisison_helper(request)
        self.user_permissions[0][1] = True
        self.user_permissions[1][1] = False
        self.user_permissions[2][1] = False
        self.user_permissions[3][1] = False
        self._permisison_helper(request, self.course)

    def test_get(self):
        """Test `GET` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.get("/")
        self._helper(request)

    def test_post(self):
        """Test `POST` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.post("/")
        self._permisison_helper(request)

    def test_put(self):
        """Test `PUT` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.put("/")
        self._helper(request)

    def test_patch(self):
        """Test `PATCH` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.patch("/")
        self._helper(request)

    def test_delete(self):
        """Test `DELETE` for `has_permission()` & `has_object_permission()` method."""
        request = self.factory.delete("/")
        self._helper(request)

    def test_get_user_from_object(self):
        """Test `_get_user_from_object()` method."""
        for obj in [self.course]:
            actual_user = self.permission_class._get_user_from_object(obj)
            expected_user = obj.owner
            self.assertEqual(actual_user, expected_user)
