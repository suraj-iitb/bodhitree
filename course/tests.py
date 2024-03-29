import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from course.models import (
    Announcement,
    Chapter,
    Course,
    CourseHistory,
    Page,
    Schedule,
    Section,
)
from discussion_forum.models import DiscussionForum
from registration.models import SubscriptionHistory
from utils import credentials


ins_cred = credentials.TEST_INSTRUCTOR_CREDENTIALS
ta_cred = credentials.TEST_TA_CREDENTIALS
stu_cred = credentials.TEST_STUDENT_CREDENTIALS


class CourseViewSetTest(APITestCase):
    """Test for `CourseViewSet`."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "plans.test.yaml",
        "subscriptions.test.yaml",
        "subscriptionhistories.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_course_helper(self, status_code, title, owner_id):
        """Helper function for `test_create_course()`.

        Args:
            status_code (int): Expected status code of the API call
            title (str): Title of the course
            owner_id (int): Owner id
        """
        data = {
            "owner": owner_id,
            "code": "101",
            "title": title,
            "description": "This is the description of the course",
            "is_published": False,
            "course_type": "O",
            "chapters_sequence": [],
            "institute": 1,
            "department": 1,
            "df_settings": {
                "anonymous_to_instructor": True,
                "send_email_to_all": False,
            },
        }
        url = reverse("course:course-create-course")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            for field in ["id", "image", "created_on", "modified_on"]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_create_course(self):
        """Test: create a course."""
        # Normal creation
        self.login(**ins_cred)
        self._create_course_helper(status.HTTP_201_CREATED, "Course 1", 1)
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_course_helper(status.HTTP_400_BAD_REQUEST, "", 1)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAOrReadOnly` permission class
        self._create_course_helper(status.HTTP_401_UNAUTHORIZED, "Course 2", 1)

        # `HTTP_403_FORBIDDEN` due to `IntegrityError` of the database
        self.login(**ins_cred)
        with transaction.atomic():
            self._create_course_helper(status.HTTP_403_FORBIDDEN, "Course 1", 1)
        self.logout()

        # `HTTP_403_FORBIDDEN` due to the course limit of the subscription is reached
        self.login(**ta_cred)
        self._create_course_helper(status.HTTP_403_FORBIDDEN, "Course 3", 2)
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `SubscriptionHistory.DoesNotExist` exception
        self.login(**stu_cred)
        self._create_course_helper(status.HTTP_403_FORBIDDEN, "Course 4", 3)
        self.logout()

    def test_list_courses(self):
        """Test: list all courses."""
        url = reverse("course:course-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), Course.objects.count())

    def test_retrieve_course(self):
        """Test: retrieve a course."""
        course_id = 1  # course with id 1 is created by django fixture
        url = reverse("course:course-detail", args=[course_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], course_id)

    def _update_course_helper(self, course, status_code, title, user_id, role, method):
        """Helper function for `test_update_course()`.

        Args:
            course (Course): `Course` model instance
            status_code (int): Expected status code of the API call
            title (str): Title of the course
            user_id (int): User id
            role (str): Role of the user (instructor/ta/student)
            method (str): HTTP method ("PUT" or "PATCH")
        """
        CourseHistory.objects.get_or_create(
            user_id=user_id,
            course=course,
            role=role,
            status="E",
        )
        data = {
            "owner": user_id,
            "code": "111",
            "title": title,
            "description": "This is the description of the course",
            "is_published": True,
            "course_type": "O",
            "chapters_sequence": [],
            "institute": 1,
            "department": 1,
            "df_settings": {
                "anonymous_to_instructor": False,
                "send_email_to_all": True,
            },
        }
        url = reverse("course:course-update-course", args=[course.id])

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            for field in ["id", "image", "created_on", "modified_on"]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def _put_or_patch(self, method):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
        """
        course = Course(
            owner_id=1,
            title="Course 4",
            course_type="O",
        )
        course.save()
        discussion_forum = DiscussionForum(
            course=course,
            anonymous_to_instructor=True,
            send_email_to_all=True,
        )
        discussion_forum.save()

        # Updated by instructor
        self.login(**ins_cred)
        self._update_course_helper(
            course, status.HTTP_200_OK, "Course 5", 1, "I", method
        )
        self.logout()

        # Updated by ta
        self.login(**ta_cred)
        self._update_course_helper(
            course, status.HTTP_200_OK, "Course 6", 2, "T", method
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_course_helper(
            course, status.HTTP_400_BAD_REQUEST, "", 1, "I", method
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAOrReadOnly` permission class
        self._update_course_helper(
            course, status.HTTP_401_UNAUTHORIZED, "Course 7", 1, "I", method
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTAOrReadOnly` permission class
        self.login(**stu_cred)
        self._update_course_helper(
            course, status.HTTP_403_FORBIDDEN, "Course 8", 3, "S", method
        )
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IntegrityError` of the database
        self.login(**ins_cred)
        with transaction.atomic():
            self._update_course_helper(
                course, status.HTTP_403_FORBIDDEN, "Course", 1, "I", method
            )
        self.logout()

        # `HTTP_403_FORBIDDEN` due to the subscription is not valid
        subscription_history = SubscriptionHistory.objects.get(user_id=2)
        subscription_history.delete()
        self.login(**ins_cred)
        self._update_course_helper(
            course, status.HTTP_403_FORBIDDEN, "Course 9", 1, "I", method
        )
        self.logout()

    def test_update_course(self):
        """Test: update the course."""
        self._put_or_patch("PUT")

    def test_partial_update_course(self):
        """Test: partial update the course."""
        self._put_or_patch("PATCH")

    def _delete_course_helper(self, status_code, title, user_id, role):
        """Helper function for `test_delete_course()`.

        Args:
            status_code (int): Expected status code of the API call
            title (str): Title of the course
            user_id (int): User id
            role (str): Role of the user (instructor/ta/student)
        """
        course = Course(
            owner_id=1,
            title=title,
            course_type="O",
        )
        course.save()
        discussion_forum = DiscussionForum(
            course=course,
            anonymous_to_instructor="True",
            send_email_to_all="True",
        )
        discussion_forum.save()
        course_history = CourseHistory(
            user_id=user_id,
            course=course,
            role=role,
            status="E",
        )
        course_history.save()

        url = reverse(("course:course-delete-course"), args=[course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Course.objects.filter(id=course.id).count(), 0)

    def test_delete_course(self):
        """Test: delete the course."""
        # Delete by owner
        self.login(**ins_cred)
        self._delete_course_helper(status.HTTP_204_NO_CONTENT, "Course 4", 1, "I")
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsOwner` permissioon class
        self._delete_course_helper(status.HTTP_401_UNAUTHORIZED, "Course 5", 1, "I")

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permissioon class (delete by ta)
        self.login(**ta_cred)
        self._delete_course_helper(status.HTTP_403_FORBIDDEN, "Course 6", 2, "T")
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permissioon class (delete by student)
        self.login(**stu_cred)
        self._delete_course_helper(status.HTTP_403_FORBIDDEN, "Course 19", 3, "S")
        self.logout()

    def _list_tas_non_tas_helper(self, status_code, course_id, tas=False):
        """Helper function for `test_list_non_tas()` and `test_list_tas()`.

        Args:
            status_code (int): Expected status code of the API call
            course_id (int): Course id
        """
        if tas:
            url = reverse(
                "course:course-list-tas",
                args=[course_id],
            )
        else:
            url = reverse(
                "course:course-list-non-tas",
                args=[course_id],
            )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            if tas:
                count = CourseHistory.objects.filter(
                    course=course_id, role="T", status="E"
                ).count()
            else:
                count = CourseHistory.objects.filter(
                    course=course_id, role="S", status="E"
                ).count()
            self.assertEqual(len(response.data), count)

    def test_list_non_tas(self):
        """Test: list non tas in the course."""
        # List by owner
        self.login(**ins_cred)
        self._list_tas_non_tas_helper(status.HTTP_200_OK, 1)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_tas_non_tas_helper(status.HTTP_200_OK, 1)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `StrictIsInstructorOrTA` permissioon class
        self._list_tas_non_tas_helper(status.HTTP_401_UNAUTHORIZED, 1)

        # `HTTP_403_FORBIDDEN` due to `StrictIsInstructorOrTA` permission class
        # (delete by student)
        self.login(**stu_cred)
        self._list_tas_non_tas_helper(status.HTTP_403_FORBIDDEN, 1)
        self.logout()

    def test_list_tas(self):
        """Test: list non tas in the course."""
        # List by owner
        self.login(**ins_cred)
        self._list_tas_non_tas_helper(status.HTTP_200_OK, 1, True)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_tas_non_tas_helper(status.HTTP_200_OK, 1, True)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `StrictIsInstructorOrTA` permissioon class
        self._list_tas_non_tas_helper(status.HTTP_401_UNAUTHORIZED, 1, True)

        # `HTTP_403_FORBIDDEN` due to `StrictIsInstructorOrTA` permission class
        # (delete by student)
        self.login(**stu_cred)
        self._list_tas_non_tas_helper(status.HTTP_403_FORBIDDEN, 1, True)
        self.logout()

    def _ta_permission_helper(self, status_code, remove_ta="false"):
        """Helper function for `test_grant_ta_permission()` and `test_remove_ta_permission()`.

        Args:
            status_code (int): Expected status code of the API call
            remove_ta (boolean): Remove ta boolean
        """
        course_id = 1
        if remove_ta == "false":
            data = {
                "user_emails": ("student@bodhitree.com", "ta@bodhitree.com"),
                "grant_ta": "true",
            }
        else:
            data = {
                "user_emails": ("student@bodhitree.com", "ta@bodhitree.com"),
                "remove_ta": remove_ta,
            }
        url = reverse(
            "course:course-handle-ta-permission",
            args=[course_id],
        )

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            course_histories = CourseHistory.objects.filter(
                course=course_id, user__email__in=data["user_emails"]
            )
            for course_history in course_histories:
                if remove_ta == "true":
                    self.assertEqual(course_history.role, "S")
                else:
                    self.assertEqual(course_history.role, "T")

    def test_grant_ta_permission(self):
        """Test: grant ta permission."""
        # Grant by owner
        self.login(**ins_cred)
        self._ta_permission_helper(status.HTTP_200_OK)
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permission class (access by ta)
        self.login(**ta_cred)
        self._ta_permission_helper(status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsOwner` permissioon class
        self._ta_permission_helper(status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permission class (access by student)
        self.login(**stu_cred)
        self._ta_permission_helper(status.HTTP_403_FORBIDDEN)
        self.logout()

    def test_remove_ta_permission(self):
        """Test: remove ta permission."""
        # Grant by owner
        self.login(**ins_cred)
        self._ta_permission_helper(status.HTTP_200_OK, "true")
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permission class (access by ta)
        self.login(**ta_cred)
        self._ta_permission_helper(status.HTTP_403_FORBIDDEN, "true")
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsOwner` permissioon class
        self._ta_permission_helper(status.HTTP_401_UNAUTHORIZED, "true")

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permission class (access by student)
        self.login(**stu_cred)
        self._ta_permission_helper(status.HTTP_403_FORBIDDEN, "true")
        self.logout()

    def test_bulk_register_into_course(self):

        file = os.path.join(settings.BASE_DIR, "main/test_data", "test.csv")

        file_utf8 = SimpleUploadedFile(
            file, open(file, "rb").read(), content_type="application/vnd.ms-excel"
        )
        self.login(**ins_cred)
        data = {"enrollment_file": file_utf8}
        url = reverse("course:course-bulk-register-into-course", args=[1])

        response = self.client.post(url, data, format="multipart")
        print(response.data)
        self.logout()
        try:
            shutil.rmtree(settings.MEDIA_ROOT)
        except OSError:
            pass


class CourseHistoryViewSetTest(APITestCase):
    """Test for `CourseHistoryViewSet`."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_course_history_helper(self, course_id, status_code, user_id, role):
        """Helper function for `test_create_course_history()`.

        Args:
            course_id (int): Course id
            status_code (int): Expected status code of the API call
            user_id (int): User id
            role (str): User role (instructor/ta/student)
        """
        data = {
            "user": user_id,
            "course": course_id,
            "role": role,
            "status": "E",
        }
        url = reverse("course:coursehistory-create-course-history")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["user"], data["user"])
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["role"], data["role"])
            self.assertEqual(response_data["status"], data["status"])

    def test_create_course_history(self):
        """Test: create a course history."""
        course_id = 4  # course with id 4 is created by django fixture

        # Created by instructor
        self.login(**ins_cred)
        self._create_course_history_helper(course_id, status.HTTP_201_CREATED, 1, "I")
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_course_history_helper(course_id, status.HTTP_201_CREATED, 2, "T")
        self.logout()

        # Created by student
        self.login(**stu_cred)
        self._create_course_history_helper(course_id, status.HTTP_201_CREATED, 3, "S")
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_course_history_helper(
            course_id, status.HTTP_400_BAD_REQUEST, 1, "D"
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAOrStudent` permission class
        self._create_course_history_helper(
            course_id, status.HTTP_401_UNAUTHORIZED, 1, "I"
        )

        # `HTTP_403_FORBIDDEN` due to `IntegrityError` of the database
        self.login(**ins_cred)
        with transaction.atomic():
            self._create_course_history_helper(
                course_id, status.HTTP_403_FORBIDDEN, 1, "I"
            )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        course_id = 100
        self.login(**ins_cred)
        self._create_course_history_helper(course_id, status.HTTP_404_NOT_FOUND, 1, "I")
        self.logout()

    def _list_course_histories_helper(self, status_code, course_id):
        """Helper function for `test_list_course_histories()`.

        Args:
            status_code (int): Expected status code of the API call
            course_id (int): Course id
        """
        url = reverse("course:coursehistory-list-course-histories", args=[course_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data["results"]),
                CourseHistory.objects.filter(course_id=course_id).count(),
            )

    def test_list_course_histories(self):
        """Test: list all courses histories."""
        course_id = 1  # course with id 1 is created by django fixture

        # Listed by instructor
        self.login(**ins_cred)
        self._list_course_histories_helper(status.HTTP_200_OK, course_id)
        self.logout()

        # Listed by ta
        self.login(**ta_cred)
        self._list_course_histories_helper(status.HTTP_200_OK, course_id)
        self.logout()

        # Listed by student
        self.login(**stu_cred)
        self._list_course_histories_helper(status.HTTP_200_OK, course_id)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAOrStudent` permission class
        self._list_course_histories_helper(status.HTTP_401_UNAUTHORIZED, course_id)

        # HTTP_403_FORBIDDEN due to `_is_registered()` method
        course_id = 4  # course with id 4 is created by django fixture
        self.login(**ins_cred)
        self._list_course_histories_helper(status.HTTP_403_FORBIDDEN, course_id)
        self.logout()

        # HTTP_404_NOT_FOUND` due to  `Course.DoesNotExist` exception
        course_id = 100
        self.login(**ins_cred)
        self._list_course_histories_helper(status.HTTP_404_NOT_FOUND, course_id)
        self.logout()

    def _retrieve_course_history_helper(self, status_code, course_history_id):
        """Helper function for `test_retrieve_course_history()`.

        Args:
            status_code (int): Expected status code of the API call
            course_history_id (int): Course history id
        """
        url = reverse(
            "course:coursehistory-retrieve-course-history",
            args=[course_history_id],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], course_history_id)

    def test_retrieve_course_history(self):
        """Test to check: retrieve the courses history."""
        course_history_id = 1

        # Retrieved by instructor
        self.login(**ins_cred)
        self._retrieve_course_history_helper(status.HTTP_200_OK, course_history_id)
        self.logout()

        # Retrieved by ta
        self.login(**ta_cred)
        self._retrieve_course_history_helper(status.HTTP_200_OK, course_history_id)
        self.logout()

        # Retrieved by student
        self.login(**stu_cred)
        self._retrieve_course_history_helper(status.HTTP_200_OK, course_history_id)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTAOrStudent` permission class
        self._retrieve_course_history_helper(
            status.HTTP_401_UNAUTHORIZED, course_history_id
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTAOrStudent` permission class
        course_history_id = 5
        self.login(**ins_cred)
        self._retrieve_course_history_helper(
            status.HTTP_403_FORBIDDEN, course_history_id
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        course_history_id = 100
        self.login(**ins_cred)
        self._retrieve_course_history_helper(
            status.HTTP_404_NOT_FOUND, course_history_id
        )
        self.logout()

    def _update_course_history_helper(
        self, status_code, user_id, role, method, user_status="U"
    ):
        """Helper function for `test_update_course_history()` &
        `test_partial_update_course_history()`.

        Args:
            status_code (int): Expected status code of the API call
            user_id (int): User id
            role (str): Role of the user (instructor/ta/student)
            method (str): HTTP method ("PUT" or "PATCH")
            user_status (str, optional): Status of user (enrolled/unerolled/pending).
                Default value is "U".
        """
        course_id = 4  # course with id 4 is created by django fixture
        course_history = CourseHistory.objects.create(
            user_id=user_id,
            course_id=course_id,
            role=role,
            status="E",
        )
        data = {
            "user": user_id,
            "course": course_id,
            "role": role,
            "status": user_status,
        }
        url = reverse(
            "course:coursehistory-update-course-history",
            args=[course_history.id],
        )

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            for field in ["id", "created_on", "modified_on"]:
                response_data.pop(field)
            self.assertEqual(response_data, data)
        course_history.delete()

    def _put_or_patch(self, method):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
        """
        # Updated by instructor
        self.login(**ins_cred)
        self._update_course_history_helper(status.HTTP_200_OK, 1, "I", method)
        self.logout()

        # Updated by ta
        self.login(**ta_cred)
        self._update_course_history_helper(status.HTTP_200_OK, 2, "T", method)
        self.logout()

        # Updated by student
        self.login(**stu_cred)
        self._update_course_history_helper(status.HTTP_200_OK, 3, "S", method)
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_course_history_helper(
            status.HTTP_400_BAD_REQUEST, 1, "I", method, "Enrolled"
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsOwner` permission class
        self._update_course_history_helper(status.HTTP_401_UNAUTHORIZED, 1, "I", method)

        # `HTTP_403_FORBIDDEN` due to `IsOwner` permission class
        self.login(**stu_cred)
        self._update_course_history_helper(status.HTTP_403_FORBIDDEN, 1, "I", method)
        self.logout()

    def test_update_course_history(self):
        """Test: update the course history."""
        self._put_or_patch("PUT")

    def test_partial_update_course_history(self):
        """Test: partial update the course history."""
        self._put_or_patch("PATCH")


class ChapterViewSetTest(APITestCase):
    """Test for `ChapterViewSet`."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "chapters.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_chapter_helper(self, course_id, title, status_code):
        """Helper function for `test_create_chapter()`.

        Args:
            course_id (int): Course id
            title (str): Title of the chapter
            status_code (int): Expected status code of the API call
        """
        data = {
            "course": course_id,
            "title": title,
            "description": "This is the description of the chapter",
        }
        url = reverse("course:chapter-create-chapter")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def test_create_chapter(self):
        """Test: create a chapter."""
        course_id = 1  # course with id 1 is created by django fixture

        # Created by instructor
        self.login(**ins_cred)
        self._create_chapter_helper(course_id, "Chapter 1", status.HTTP_201_CREATED)
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_chapter_helper(course_id, "Chapter 2", status.HTTP_201_CREATED)
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_chapter_helper(course_id, "", status.HTTP_400_BAD_REQUEST)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._create_chapter_helper(
            course_id, "Chapter 3", status.HTTP_401_UNAUTHORIZED
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._create_chapter_helper(course_id, "Chapter 4", status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IntegrityError` of the database
        self.login(**ins_cred)
        with transaction.atomic():
            self._create_chapter_helper(
                course_id, "Chapter 1", status.HTTP_403_FORBIDDEN
            )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the course does not exist
        course_id = 100
        self.login(**ins_cred)
        self._create_chapter_helper(course_id, "Chapter 5", status.HTTP_404_NOT_FOUND)
        self.logout()

    def _list_chapters_helper(self, course_id, status_code):
        """Helper function for `test_list_chapters()`.

        Args:
            course_id (int): Course id
            status_code (int): Expected status code of the API call
        """
        url = reverse("course:chapter-list-chapters", args=[course_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data), Chapter.objects.filter(course_id=course_id).count()
            )

    def test_list_chapters(self):
        """Test: list all chapters."""
        course_id = 1  # course with id 1 is created by django fixture

        # Listed by instructor
        self.login(**ins_cred)
        self._list_chapters_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # Listed by ta
        self.login(**ta_cred)
        self._list_chapters_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # Listed by student
        self.login(**stu_cred)
        self._list_chapters_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._list_chapters_helper(course_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        course_id = 3  # course with id 3 is created by django fixture
        self.login(**ins_cred)
        self._list_chapters_helper(course_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the course does not exist
        course_id = 100
        self.login(**ins_cred)
        self._list_chapters_helper(course_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _retrieve_chapter_helper(self, chapter_id, status_code):
        """Helper function for `test_retrieve_chapter()`.

        Args:
            chapter_id (int): Chapter id
            status_code (int): Expected status code of the API call
        """
        url = reverse("course:chapter-retrieve-chapter", args=[chapter_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], chapter_id)

    def test_retrieve_chapter(self):
        """Test: retrieve the chapter."""
        chapter_id = 1  # chapter with id 1 is created by django fixture

        # Retrieved by instructor
        self.login(**ins_cred)
        self._retrieve_chapter_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by ta
        self.login(**ta_cred)
        self._retrieve_chapter_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by student
        self.login(**stu_cred)
        self._retrieve_chapter_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._retrieve_chapter_helper(chapter_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        chapter_id = 3  # chapter with id 3 is created by django fixture
        self.login(**ins_cred)
        self._list_chapters_helper(chapter_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        chapter_id = 100
        self.login(**ins_cred)
        self._list_chapters_helper(chapter_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _update_chapters_helper(self, chapter_id, title, status_code, method):
        """Helper function for `test_update_chapter()` & `test_partial_update_chapter()`.

        Args:
            chapter_id (int): Chapter id
            title (str): Title of the chapter
            status_code (int): Expected status code of the API call
            method (str): HTTP method ("PUT" or "PATCH")
        """
        course_id = 1  # course with id 1 is created by django fixture
        data = {
            "course": course_id,
            "title": title,
            "description": "Description of the chapter",
        }
        url = reverse(("course:chapter-update-chapter"), args=[chapter_id])

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def _put_or_patch(self, method):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
        """
        chapter_id = Chapter.objects.create(course_id=1, title="Chapter 1").id

        # Updated by instructor
        self.login(**ins_cred)
        self._update_chapters_helper(
            chapter_id, "Chapter 2", status.HTTP_200_OK, method
        )
        self.logout()

        # Updated by ta
        self.login(**ta_cred)
        self._update_chapters_helper(
            chapter_id, "Chapter 3", status.HTTP_200_OK, method
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_chapters_helper(
            chapter_id, "", status.HTTP_400_BAD_REQUEST, method
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._update_chapters_helper(
            chapter_id, "Chapter 4", status.HTTP_401_UNAUTHORIZED, method
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._update_chapters_helper(
            chapter_id, "Chapter 5", status.HTTP_403_FORBIDDEN, method
        )
        self.logout()

        # HTTP_403_FORBIDDEN due to IntegrityError
        self.login(**ins_cred)
        with transaction.atomic():
            self._update_chapters_helper(
                chapter_id, "Chapter-1", status.HTTP_403_FORBIDDEN, method
            )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        chapter_id = 100
        self.login(**ins_cred)
        self._update_chapters_helper(
            chapter_id, "Chapter 6", status.HTTP_404_NOT_FOUND, method
        )
        self.logout()

    def test_update_chapter(self):
        """Test: update the chapter."""
        self._put_or_patch("PUT")

    def test_partial_update_chapter(self):
        """Test: partial update the chapter."""
        self._put_or_patch("PATCH")

    def _delete_chapter_helper(self, title, status_code):
        """Helper function for `test_delete_chapter()`.

        Args:
            title(str): Title of the chapter
            status_code (int): Expected status code of the API call
        """
        chapter_id = Chapter.objects.create(course_id=1, title=title).id
        url = reverse(("course:chapter-delete-chapter"), args=[chapter_id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Chapter.objects.filter(id=chapter_id).count(), 0)

    def test_delete_chapter(self):
        """Test: delete the chapter."""
        # Deleted by instructor
        self.login(**ins_cred)
        self._delete_chapter_helper("Chapter 1", status.HTTP_204_NO_CONTENT)
        self.logout()

        # Deleted by ta
        self.login(**ta_cred)
        self._delete_chapter_helper("Chapter 2", status.HTTP_204_NO_CONTENT)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._delete_chapter_helper("Chapter 3", status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._delete_chapter_helper("Chapter 4", status.HTTP_403_FORBIDDEN)
        self.logout()


class PageViewSetTest(APITestCase):
    """Test for PageViewSetTest."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "pages.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_page_helper(self, course_id, title, status_code):
        """Helper function for `test_create_page()`.

        Args:
            course_id (int): Course id
            title (str): Title of the page
            status_code (int): Expected status code of the API call
        """
        data = {
            "course": course_id,
            "title": title,
            "description": "Page description",
        }
        url = reverse("course:page-create-page")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def test_create_page(self):
        """Test: create a page."""
        course_id = 1  # course with id 1 is created by django fixture

        # Created by instructor
        self.login(**ins_cred)
        self._create_page_helper(course_id, "Page 1", status.HTTP_201_CREATED)
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_page_helper(course_id, "Page 2", status.HTTP_201_CREATED)
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_page_helper(course_id, "", status.HTTP_400_BAD_REQUEST)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._create_page_helper(course_id, "Page 3", status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._create_page_helper(course_id, "Page 4", status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IntegrityError` of the database
        self.login(**ins_cred)
        with transaction.atomic():
            self._create_page_helper(course_id, "Page 1", status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the course does not exist
        course_id = 100
        self.login(**ins_cred)
        self._create_page_helper(course_id, "Page 5", status.HTTP_404_NOT_FOUND)
        self.logout()

    def _list_pages_helper(self, course_id, status_code):
        """Helper function for `test_list_pages()`.

        Args:
            course_id (int): Course id
            status_code (int): Expected status code of the API call
        """
        url = reverse("course:page-list-pages", args=[course_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data), Page.objects.filter(course_id=course_id).count()
            )

    def test_list_pages(self):
        """Test: list all pages."""
        course_id = 1  # course with id 1 is created by django fixture

        # Listed by instructor
        self.login(**ins_cred)
        self._list_pages_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # Listed by ta
        self.login(**ta_cred)
        self._list_pages_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # Listed by student
        self.login(**stu_cred)
        self._list_pages_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._list_pages_helper(course_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        course_id = 3  # course with id 3 is created by django fixture
        self.login(**ins_cred)
        self._list_pages_helper(course_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the course does not exist
        course_id = 100
        self.login(**ins_cred)
        self._list_pages_helper(course_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _retrieve_page_helper(self, page_id, status_code):
        """Helper function for `test_retrieve_page()`.

        Args:
            page_id (int): Page id
            status_code (int): Expected status code of the API call
        """
        url = reverse("course:page-retrieve-page", args=[page_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], page_id)

    def test_retrieve_page(self):
        """Test: retrieve the page."""
        """Test: retrieve the chapter."""
        page_id = 1  # chapter with id 1 is created by django fixture

        # Retrieved by instructor
        self.login(**ins_cred)
        self._retrieve_page_helper(page_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by ta
        self.login(**ta_cred)
        self._retrieve_page_helper(page_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by student
        self.login(**stu_cred)
        self._retrieve_page_helper(page_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._retrieve_page_helper(page_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        page_id = 3  # chapter with id 3 is created by django fixture
        self.login(**ins_cred)
        self._retrieve_page_helper(page_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        page_id = 100
        self.login(**ins_cred)
        self._retrieve_page_helper(page_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _update_page_helper(self, page_id, title, status_code, method):
        """Helper function for `test_update_chapter()` & `test_partial_update_chapter()`.

        Args:
            page_id (int): Page id
            title (str): Title of the page
            status_code (int): Expected status code of the API call
            method (str): HTTP method ("PUT" or "PATCH")
        """
        course_id = 1  # course with id 1 is created by django fixture
        data = {
            "course": course_id,
            "title": title,
            "description": "Description of page",
        }
        url = reverse("course:page-update-page", args=[page_id])

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def _put_or_patch(self, method):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
        """
        page_id = Page.objects.create(course_id=1, title="Page 1").id

        # Updated by instructor
        self.login(**ins_cred)
        self._update_page_helper(page_id, "Page 2", status.HTTP_200_OK, method)
        self.logout()

        # Updated by ta
        self.login(**ta_cred)
        self._update_page_helper(page_id, "Page 3", status.HTTP_200_OK, method)
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_page_helper(page_id, "", status.HTTP_400_BAD_REQUEST, method)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._update_page_helper(
            page_id, "Page 4", status.HTTP_401_UNAUTHORIZED, method
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._update_page_helper(page_id, "Page 5", status.HTTP_403_FORBIDDEN, method)
        self.logout()

        # HTTP_403_FORBIDDEN due to IntegrityError
        self.login(**ins_cred)
        with transaction.atomic():
            self._update_page_helper(
                page_id, "Page-1", status.HTTP_403_FORBIDDEN, method
            )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        page_id = 100
        self.login(**ins_cred)
        self._update_page_helper(page_id, "Page 6", status.HTTP_404_NOT_FOUND, method)
        self.logout()

    def test_update_page(self):
        """Test: update the page."""
        self._put_or_patch("PUT")

    def test_partial_update_page(self):
        """Test: partial update the page."""
        self._put_or_patch("PATCH")

    def _delete_page_helper(self, title, status_code):
        """Helper function for `test_delete_chapter()`.

        Args:
            title(str): Title of the chapter
            status_code (int): Expected status code of the API call
        """
        page = Page.objects.create(course_id=1, title=title)
        url = reverse(("course:page-delete-page"), args=[page.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Page.objects.filter(id=page.id).count(), 0)

    def test_delete_page(self):
        """Test: delete the page."""
        # Deleted by instructor
        self.login(**ins_cred)
        self._delete_page_helper("Page 1", status.HTTP_204_NO_CONTENT)
        self.logout()

        # Deleted by ta
        self.login(**ta_cred)
        self._delete_page_helper("Page 2", status.HTTP_204_NO_CONTENT)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._delete_page_helper("Page 3", status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._delete_page_helper("Page 4", status.HTTP_403_FORBIDDEN)
        self.logout()


class SectionViewSetTest(APITestCase):
    """Test for SectionViewSet."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "chapters.test.yaml",
        "sections.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_section_helper(self, chapter_id, title, status_code):
        """Helper function for `test_create_section()`.

        Args:
            chapter_id (int): Chapter id
            title (str): Title of the section
            status_code (int): Expected status code of the API call
        """
        data = {
            "chapter": chapter_id,
            "title": title,
            "description": "This is the section description",
            "content_sequence": [[1, 2]],  # (a,b) denotes (content type, content id)
        }
        url = reverse("course:section-create-section")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["chapter"], data["chapter"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def test_create_section(self):
        """"Test: create a section."""
        chapter_id = 1  # chapter with id 1 is created by django fixture

        # Created by instructor
        self.login(**ins_cred)
        self._create_section_helper(chapter_id, "Section 1", status.HTTP_201_CREATED)
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_section_helper(chapter_id, "Section 2", status.HTTP_201_CREATED)
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_section_helper(chapter_id, "", status.HTTP_400_BAD_REQUEST)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._create_section_helper(
            chapter_id, "Section 3", status.HTTP_401_UNAUTHORIZED
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._create_section_helper(chapter_id, "Section 4", status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IntegrityError` of the database
        self.login(**ins_cred)
        with transaction.atomic():
            self._create_section_helper(
                chapter_id, "Section 1", status.HTTP_403_FORBIDDEN
            )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the chapter does not exist
        chapter_id = 100
        self.login(**ins_cred)
        self._create_section_helper(chapter_id, "Section 5", status.HTTP_404_NOT_FOUND)
        self.logout()

    def _list_sections_helper(self, chapter_id, status_code):
        """Helper function for `test_list_sections()`.

        Args:
            chapter_id (int): Chapter id
            status_code (int): Expected status code of the API call
        """
        url = reverse("course:section-list-sections", args=[chapter_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data),
                Section.objects.filter(chapter_id=chapter_id).count(),
            )

    def test_list_sections(self):
        """Test: list all sections."""
        chapter_id = 1  # chapter with id 1 is created by django fixture

        # Listed by instructor
        self.login(**ins_cred)
        self._list_sections_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # Listed by ta
        self.login(**ta_cred)
        self._list_sections_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # Listed by student
        self.login(**stu_cred)
        self._list_sections_helper(chapter_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._list_sections_helper(chapter_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        chapter_id = 3  # chapter with id 3 is created by django fixture
        self.login(**ins_cred)
        self._list_sections_helper(chapter_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the course does not exist
        chapter_id = 100
        self.login(**ins_cred)
        self._list_sections_helper(chapter_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _retrieve_section_helper(self, section_id, status_code):
        """Helper function for `test_retrieve_section()`.

        Args:
            section_id (int): Section id
            status_code (int): Expected status code of the API call
        """
        url = reverse("course:section-retrieve-section", args=[section_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], section_id)

    def test_retrieve_section(self):
        """Test: retrieve the section."""
        section_id = 1  # section with id 1 is created by django fixture

        # Retrieved by instructor
        self.login(**ins_cred)
        self._retrieve_section_helper(section_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by ta
        self.login(**ta_cred)
        self._retrieve_section_helper(section_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by student
        self.login(**stu_cred)
        self._retrieve_section_helper(section_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._retrieve_section_helper(section_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        section_id = 3  # section with id 3 is created by django fixture
        self.login(**ins_cred)
        self._retrieve_section_helper(section_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        section_id = 100
        self.login(**ins_cred)
        self._retrieve_section_helper(section_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _update_section_helper(self, section_id, title, status_code, method):
        """Helper function for `test_update_section()` & `test_partial_update_section()`.

        Args:
            section_id (int): Section id
            title (str): Title of the section
            status_code (int): Expected status code of the API call
            method (str): HTTP method ("PUT" or "PATCH")
        """
        data = {
            "chapter": 1,
            "title": title,
            "description": "Section description",
        }
        url = reverse(("course:section-update-section"), args=[section_id])

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["chapter"], data["chapter"])
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def _put_or_patch(self, method):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
        """
        section_id = Section.objects.create(chapter_id=1, title="Section 1").id

        # Updated by instructor
        self.login(**ins_cred)
        self._update_section_helper(section_id, "Section 2", status.HTTP_200_OK, method)
        self.logout()

        # Updated by ta
        self.login(**ta_cred)
        self._update_section_helper(section_id, "Section 3", status.HTTP_200_OK, method)
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_section_helper(section_id, "", status.HTTP_400_BAD_REQUEST, method)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._update_section_helper(
            section_id, "Section 4", status.HTTP_401_UNAUTHORIZED, method
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._update_section_helper(
            section_id, "Section 5", status.HTTP_403_FORBIDDEN, method
        )
        self.logout()

        # HTTP_403_FORBIDDEN due to IntegrityError
        self.login(**ins_cred)
        with transaction.atomic():
            self._update_section_helper(
                section_id, "Section-1", status.HTTP_403_FORBIDDEN, method
            )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        section_id = 100
        self.login(**ins_cred)
        self._update_section_helper(
            section_id, "Section 6", status.HTTP_404_NOT_FOUND, method
        )
        self.logout()

    def test_update_section(self):
        """Test: update the section."""
        self._put_or_patch("PUT")

    def test_partial_update_section(self):
        """Test: partial update the section."""
        self._put_or_patch("PATCH")

    def _delete_section_helper(self, title, status_code):
        """Helper function for `test_delete_section()`.

        Args:
            title(str): Title of the section
            status_code (int): Expected status code of the API call
        """
        section_id = Section.objects.create(chapter_id=1, title=title).id
        url = reverse(("course:section-delete-section"), args=[section_id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Section.objects.filter(id=section_id).count(), 0)

    def test_delete_section(self):
        """Test: delete the section."""
        # Deleted by instructor
        self.login(**ins_cred)
        self._delete_section_helper("Section 1", status.HTTP_204_NO_CONTENT)
        self.logout()

        # Deleted by ta
        self.login(**ta_cred)
        self._delete_section_helper("Section 2", status.HTTP_204_NO_CONTENT)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._delete_section_helper("Section 3", status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._delete_section_helper("Section 4", status.HTTP_403_FORBIDDEN)
        self.logout()


class AnnouncementViewSetTest(APITestCase):
    """Test for AnnouncementViewSetTest."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "announcement.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_announcement_helper(self, course_id, body, status_code):
        """Helper function for `test_create_announcement()`.

        Args:
            course_id (int): Course id
            body (str): Body of the announcement
            status_code (int): Expected status code of the API call
        """
        data = {
            "course": course_id,
            "body": body,
        }
        url = reverse("course:announcement-create-announcement")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["body"], data["body"])

    def test_create_announcement(self):
        """Test: create a announcement."""
        course_id = 1  # course with id 1 is created by django fixture

        # Created by instructor
        self.login(**ins_cred)
        self._create_announcement_helper(course_id, "body 1", status.HTTP_201_CREATED)
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_announcement_helper(course_id, "body 2", status.HTTP_201_CREATED)
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_announcement_helper(course_id, "", status.HTTP_400_BAD_REQUEST)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._create_announcement_helper(
            course_id, "body 3", status.HTTP_401_UNAUTHORIZED
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._create_announcement_helper(course_id, "body 4", status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the course does not exist
        course_id = 100
        self.login(**ins_cred)
        self._create_announcement_helper(course_id, "body 5", status.HTTP_404_NOT_FOUND)
        self.logout()

    def _list_announcements_helper(self, course_id, status_code, latest=False):
        """Helper function for `test_list_announcements()`.

        Args:
            course_id (int): Course id
            status_code (int): Expected status code of the API call
        """
        if latest:
            url = reverse(
                "course:announcement-list-latest-announcements", args=[course_id]
            )
        else:
            url = reverse("course:announcement-list-announcements", args=[course_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            if latest:
                announcement_count = (
                    Announcement.objects.filter(course=course_id)
                    .order_by("-is_pinned", "-id")[:2]
                    .count()
                )
            else:
                announcement_count = Announcement.objects.filter(
                    course_id=course_id
                ).count()
            self.assertEqual(len(response.data), announcement_count)

    def test_list_announcements(self):
        """Test: list all announcements."""
        course_id = 1  # course with id 1 is created by django fixture

        # Listed by instructor
        self.login(**ins_cred)
        self._list_announcements_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # Listed by ta
        self.login(**ta_cred)
        self._list_announcements_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # Listed by student
        self.login(**stu_cred)
        self._list_announcements_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._list_announcements_helper(course_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        course_id = 3  # course with id 3 is created by django fixture
        self.login(**ins_cred)
        self._list_announcements_helper(course_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the course does not exist
        course_id = 100
        self.login(**ins_cred)
        self._list_announcements_helper(course_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def test_list_latest_announcements(self):
        """Test: list latest announcements."""
        course_id = 1  # course with id 1 is created by django fixture

        # Listed by instructor
        self.login(**ins_cred)
        self._list_announcements_helper(course_id, status.HTTP_200_OK, True)
        self.logout()

        # Listed by ta
        self.login(**ta_cred)
        self._list_announcements_helper(course_id, status.HTTP_200_OK, True)
        self.logout()

        # Listed by student
        self.login(**stu_cred)
        self._list_announcements_helper(course_id, status.HTTP_200_OK, True)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._list_announcements_helper(course_id, status.HTTP_401_UNAUTHORIZED, True)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        course_id = 3  # course with id 3 is created by django fixture
        self.login(**ins_cred)
        self._list_announcements_helper(course_id, status.HTTP_403_FORBIDDEN, True)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the course does not exist
        course_id = 100
        self.login(**ins_cred)
        self._list_announcements_helper(course_id, status.HTTP_404_NOT_FOUND, True)
        self.logout()

    def _retrieve_announcement_helper(self, announcement_id, status_code):
        """Helper function for `test_retrieve_announcement()`.

        Args:
            announcement_id (int): Announcement id
            status_code (int): Expected status code of the API call
        """
        url = reverse(
            "course:announcement-retrieve-announcement", args=[announcement_id]
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], announcement_id)

    def test_retrieve_announcement(self):
        """Test: retrieve the announcement."""
        announcement_id = 1  # announcement with id 1 is created by django fixture

        # Retrieved by instructor
        self.login(**ins_cred)
        self._retrieve_announcement_helper(announcement_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by ta
        self.login(**ta_cred)
        self._retrieve_announcement_helper(announcement_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by student
        self.login(**stu_cred)
        self._retrieve_announcement_helper(announcement_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._retrieve_announcement_helper(
            announcement_id, status.HTTP_401_UNAUTHORIZED
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        announcement_id = 3  # announcement with id 3 is created by django fixture
        self.login(**ins_cred)
        self._retrieve_announcement_helper(announcement_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        announcement_id = 100
        self.login(**ins_cred)
        self._retrieve_announcement_helper(announcement_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _update_announcement_helper(self, announcement_id, body, status_code, method):
        """Helper function for `test_update_announcement()` &
        `test_partial_update_announcement()`.

        Args:
            announcement_id (int): Announcement id
            body (str): Body of the announcement
            status_code (int): Expected status code of the API call
            method (str): HTTP method ("PUT" or "PATCH")
        """
        course_id = 1  # course with id 1 is created by django fixture
        data = {
            "course": course_id,
            "body": body,
        }
        url = reverse("course:announcement-update-announcement", args=[announcement_id])

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["body"], data["body"])

    def _put_or_patch(self, method):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
        """
        announcement_id = Announcement.objects.create(course_id=1, body="Body 1").id

        # Updated by instructor
        self.login(**ins_cred)
        self._update_announcement_helper(
            announcement_id, "Body 2", status.HTTP_200_OK, method
        )
        self.logout()

        # Updated by ta
        self.login(**ta_cred)
        self._update_announcement_helper(
            announcement_id, "Body 3", status.HTTP_200_OK, method
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_announcement_helper(
            announcement_id, "", status.HTTP_400_BAD_REQUEST, method
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._update_announcement_helper(
            announcement_id, "Body 4", status.HTTP_401_UNAUTHORIZED, method
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._update_announcement_helper(
            announcement_id, "Body 5", status.HTTP_403_FORBIDDEN, method
        )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        announcement_id = 100
        self.login(**ins_cred)
        self._update_announcement_helper(
            announcement_id, "Body 6", status.HTTP_404_NOT_FOUND, method
        )
        self.logout()

    def test_update_announcement(self):
        """Test: update the announcement."""
        self._put_or_patch("PUT")

    def test_partial_update_announcement(self):
        """Test: partial update the announcement."""
        self._put_or_patch("PATCH")

    def _delete_announcement_helper(self, body, status_code):
        """Helper function for `test_delete_announcement()`.

        Args:
            body(str): Body of the announcement
            status_code (int): Expected status code of the API call
        """
        announcement = Announcement.objects.create(course_id=1, body=body)
        url = reverse(
            ("course:announcement-delete-announcement"), args=[announcement.id]
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Announcement.objects.filter(id=announcement.id).count(), 0)

    def test_delete_announcement(self):
        """Test: delete the announcement."""
        # Deleted by instructor
        self.login(**ins_cred)
        self._delete_announcement_helper("Body 1", status.HTTP_204_NO_CONTENT)
        self.logout()

        # Deleted by ta
        self.login(**ta_cred)
        self._delete_announcement_helper("Body 2", status.HTTP_204_NO_CONTENT)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._delete_announcement_helper("Body 3", status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._delete_announcement_helper("Body 4", status.HTTP_403_FORBIDDEN)
        self.logout()


class ScheduleViewSetTest(APITestCase):
    """Test for `ScheduleViewSet`."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "schedule.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_schedule_helper(
        self, course_id, start_date, end_date, content_list, status_code
    ):
        """Helper function for `test_create_schedule()`.

        Args:
            course_id (int): Course id
            start_date (date): Start date of the schedule
            end_date (date): End date of the schedule
            content_list (array): Array of contents
            status_code (int): Expected status code of the API call
        """
        data = {
            "course": course_id,
            "start_date": start_date,
            "end_date": end_date,
            "content_list": content_list,
        }
        url = reverse("course:schedule-create-schedule")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["start_date"], data["start_date"])
            self.assertEqual(response_data["end_date"], data["end_date"])
            self.assertEqual(response_data["content_list"], data["content_list"])

    def test_create_schedule(self):
        """Test: create a schedule."""
        course_id = 1  # course with id 1 is created by django fixture

        # Created by instructor
        self.login(**ins_cred)
        self._create_schedule_helper(
            course_id,
            "2021-05-12",
            "2021-05-20",
            [[0, 1], [1, 2], [2, 3]],
            status.HTTP_201_CREATED,
        )
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_schedule_helper(
            course_id,
            "2021-05-13",
            "2021-05-20",
            [[0, 5], [1, 2], [2, 3]],
            status.HTTP_201_CREATED,
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_schedule_helper(
            course_id,
            "",
            "2021-05-20",
            [[0, 5], [1, 2], [2, 3]],
            status.HTTP_400_BAD_REQUEST,
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._create_schedule_helper(
            course_id,
            "",
            "2021-05-20",
            [[0, 5], [1, 2], [2, 3]],
            status.HTTP_401_UNAUTHORIZED,
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._create_schedule_helper(
            course_id,
            "",
            "2021-05-20",
            [[0, 5], [1, 2], [2, 3]],
            status.HTTP_403_FORBIDDEN,
        )
        self.logout()

        # `HTTP_403_FORBIDDEN` due to `IntegrityError` of the database
        self.login(**ins_cred)
        with transaction.atomic():
            self._create_schedule_helper(
                course_id,
                "2021-05-12",
                "2021-05-20",
                [[0, 1], [1, 2], [2, 3]],
                status.HTTP_403_FORBIDDEN,
            )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the course does not exist
        course_id = 100
        self.login(**ins_cred)
        self._create_schedule_helper(
            course_id,
            "2021-05-12",
            "2021-05-20",
            [[0, 1], [1, 2], [2, 4]],
            status.HTTP_404_NOT_FOUND,
        )
        self.logout()

    def _list_schedules_helper(self, course_id, status_code):
        """Helper function for `test_list_schedules()`.

        Args:
            course_id (int): Course id
            status_code (int): Expected status code of the API call
        """
        url = reverse("course:schedule-list-schedules", args=[course_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data), Schedule.objects.filter(course_id=course_id).count()
            )

    def test_list_schedules(self):
        """Test: list all schedules."""
        course_id = 1  # course with id 1 is created by django fixture

        # Listed by instructor
        self.login(**ins_cred)
        self._list_schedules_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # Listed by ta
        self.login(**ta_cred)
        self._list_schedules_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # Listed by student
        self.login(**stu_cred)
        self._list_schedules_helper(course_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._list_schedules_helper(course_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `_is_registered()` method
        course_id = 3  # course with id 3 is created by django fixture
        self.login(**ins_cred)
        self._list_schedules_helper(course_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to the course does not exist
        course_id = 100
        self.login(**ins_cred)
        self._list_schedules_helper(course_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _retrieve_schedule_helper(self, schedule_id, status_code):
        """Helper function for `test_retrieve_schedule()`.

        Args:
            schedule_id (int): Schedule id
            status_code (int): Expected status code of the API call
        """
        url = reverse("course:schedule-retrieve-schedule", args=[schedule_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], schedule_id)

    def test_retrieve_schedule(self):
        """Test: retrieve the schedule."""
        schedule_id = 1  # schedule with id 1 is created by django fixture

        # Retrieved by instructor
        self.login(**ins_cred)
        self._retrieve_schedule_helper(schedule_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by ta
        self.login(**ta_cred)
        self._retrieve_schedule_helper(schedule_id, status.HTTP_200_OK)
        self.logout()

        # Retrieved by student
        self.login(**stu_cred)
        self._retrieve_schedule_helper(schedule_id, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._retrieve_schedule_helper(schedule_id, status.HTTP_401_UNAUTHORIZED)

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        schedule_id = 3  # schedule with id 3 is created by django fixture
        self.login(**ins_cred)
        self._retrieve_schedule_helper(schedule_id, status.HTTP_403_FORBIDDEN)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        schedule_id = 100
        self.login(**ins_cred)
        self._retrieve_schedule_helper(schedule_id, status.HTTP_404_NOT_FOUND)
        self.logout()

    def _update_schedule_helper(
        self, schedule_id, start_date, end_date, content_list, status_code, method
    ):
        """Helper function for `test_update_chapter()` & `test_partial_update_chapter()`.

        Args:
            schedule_id (int): schedule id
            start_date (date): Start date of the schedule
            end_date (date): End date of the schedule
            content_list (array): Array of contents
            status_code (int): Expected status code of the API call
            method (str): HTTP method ("PUT" or "PATCH")
        """
        course_id = 1  # course with id 1 is created by django fixture
        data = {
            "course": course_id,
            "start_date": start_date,
            "end_date": end_date,
            "content_list": content_list,
        }
        url = reverse(("course:schedule-update-schedule"), args=[schedule_id])

        if method == "PUT":
            response = self.client.put(url, data)
        else:
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["start_date"], data["start_date"])
            self.assertEqual(response_data["end_date"], data["end_date"])
            self.assertEqual(response_data["content_list"], data["content_list"])

    def _put_or_patch(self, method):
        """Helper function to decide full(PUT) or partial(PATCH) update.

        Args:
            method (str): HTTP method ("PUT" or "PATCH")
        """
        schedule_id = 1

        # Updated by instructor
        self.login(**ins_cred)
        self._update_schedule_helper(
            schedule_id,
            "2021-05-12",
            "2021-05-20",
            [[0, 1], [1, 2], [2, 3]],
            status.HTTP_200_OK,
            method,
        )
        self.logout()

        # Updated by ta
        self.login(**ta_cred)
        self._update_schedule_helper(
            schedule_id,
            "2021-05-12",
            "2021-05-20",
            [[0, 1], [1, 2], [2, 9]],
            status.HTTP_200_OK,
            method,
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._update_schedule_helper(
            schedule_id,
            "",
            "2021-05-20",
            [[0, 1], [1, 2], [2, 3]],
            status.HTTP_400_BAD_REQUEST,
            method,
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._update_schedule_helper(
            schedule_id,
            "2021-05-12",
            "2021-05-20",
            [[0, 1], [1, 2], [2, 3]],
            status.HTTP_401_UNAUTHORIZED,
            method,
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._update_schedule_helper(
            schedule_id,
            "2021-05-12",
            "2021-05-20",
            [[0, 1], [1, 2], [2, 3]],
            status.HTTP_403_FORBIDDEN,
            method,
        )
        self.logout()

        # HTTP_403_FORBIDDEN due to IntegrityError
        self.login(**ins_cred)
        with transaction.atomic():
            self._update_schedule_helper(
                schedule_id,
                "2021-05-04",
                "2021-05-11",
                [],
                status.HTTP_403_FORBIDDEN,
                method,
            )
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `get_object()` method
        schedule_id = 100
        self.login(**ins_cred)
        self._update_schedule_helper(
            schedule_id,
            "2021-05-12",
            "2021-05-20",
            [[0, 1], [1, 2], [2, 3]],
            status.HTTP_404_NOT_FOUND,
            method,
        )
        self.logout()

    def test_update_schedule(self):
        """Test: update the schedule."""
        self._put_or_patch("PUT")

    def test_partial_update_schedule(self):
        """Test: partial update the schedule."""
        self._put_or_patch("PATCH")

    def _delete_schedule_helper(self, start_date, end_date, status_code):
        """Helper function for `test_delete_schedule()`.

        Args:
            start_date (date): Start date of the schedule
            end_date (date): End date of the schedule
            status_code (int): Expected status code of the API call
        """
        schedule_id = Schedule.objects.create(
            course_id=1, start_date=start_date, end_date=end_date
        ).id
        url = reverse(("course:schedule-delete-schedule"), args=[schedule_id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Schedule.objects.filter(id=schedule_id).count(), 0)

    def test_delete_schedule(self):
        """Test: delete the schedule."""
        # Deleted by instructor
        self.login(**ins_cred)
        self._delete_schedule_helper(
            "2021-05-12", "2021-05-20", status.HTTP_204_NO_CONTENT
        )
        self.logout()

        # Deleted by ta
        self.login(**ta_cred)
        self._delete_schedule_helper(
            "2021-05-12", "2021-05-20", status.HTTP_204_NO_CONTENT
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._delete_schedule_helper(
            "2021-05-12", "2021-05-20", status.HTTP_401_UNAUTHORIZED
        )

        # `HTTP_403_FORBIDDEN` due to `IsInstructorOrTA` permission class
        self.login(**stu_cred)
        self._delete_schedule_helper(
            "2021-05-12", "2021-05-21", status.HTTP_403_FORBIDDEN
        )
        self.logout()
