from django.db import transaction
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from course.models import Chapter, Course, CourseHistory, Page, Section
from discussion_forum.models import DiscussionForum
from registration.models import SubscriptionHistory
from utils import credentials


ins_cred = credentials.TEST_INSTRUCTOR_CREDENTIALS
ta_cred = credentials.TEST_TA_CREDENTIALS
stu_cred = credentials.TEST_STUDENT_CREDENTIALS


class CourseViewSetTest(APITestCase):
    """Test for CourseViewSet."""

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

    def test_list_courses(self):
        """Test to check: list all courses."""
        url = reverse("course:course-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), Course.objects.all().count())

    def test_retrieve_course(self):
        """Test to check: retrieve a course."""
        course_id = 1  # course with id 1 is created by django fixture
        url = reverse("course:course-detail", args=[course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], course_id)

    def _create_course_helper(self, status_code, title, owner_id):
        """Helper function to test create course functionality.

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
        """Test to check: create a course."""
        # Normal creation
        self.login(**ins_cred)
        self._create_course_helper(status.HTTP_201_CREATED, "Course 1", 1)
        self.logout()

        # The course limit of the subscription is reached
        self.login(**ta_cred)
        self._create_course_helper(status.HTTP_403_FORBIDDEN, "Course 2", 2)
        self.logout()

        # The subscription plan does not exist
        self.login(**stu_cred)
        self._create_course_helper(status.HTTP_403_FORBIDDEN, "Course 3", 3)
        self.logout()

    def _update_course_helper(self, course, status_code, title, user_id, role):
        """Helper function to test update course functionality.

        Args:
            course (Course): `Course` model instance
            status_code (int): Expected status code of the API call
            title (str): Title of the course
            user_id (int): User id
            role (str): Role of the user (instructor/ta/student)
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
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            for field in ["id", "image", "created_on", "modified_on"]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_update_course(self):
        """Test to check: update of the course."""
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

        # Update by instructor
        self.login(**ins_cred)
        self._update_course_helper(course, status.HTTP_200_OK, "Course 5", 1, "I")
        self.logout()

        # Update by ta
        self.login(**ta_cred)
        self._update_course_helper(course, status.HTTP_200_OK, "Course 6", 2, "T")
        self.logout()

        # HTTP_403_FORBIDDEN due to IsInstructorOrTAOrReadOnly permission class
        self.login(**stu_cred)
        self._update_course_helper(
            course, status.HTTP_403_FORBIDDEN, "Course 7", 3, "S"
        )
        self.logout()

        # HTTP_401_UNAUTHORIZED due to IsInstructorOrTAOrReadOnly permission class
        self._update_course_helper(
            course, status.HTTP_401_UNAUTHORIZED, "Course 8", 1, "I"
        )

        # HTTP_403_FORBIDDEN due to IntegrityError of the database
        self.login(**ins_cred)
        with transaction.atomic():
            self._update_course_helper(
                course, status.HTTP_403_FORBIDDEN, "Course", 1, "I"
            )
        self.logout()

        # HTTP_400_BAD_REQUEST due to serialization errors
        self.login(**ins_cred)
        self._update_course_helper(course, status.HTTP_400_BAD_REQUEST, "", 1, "I")
        self.logout()

        # HTTP_403_FORBIDDEN due to SubscriptionHistory expiry/does not exist
        subscription_history = SubscriptionHistory.objects.get(user_id=2)
        subscription_history.delete()
        self.login(**ins_cred)
        self._update_course_helper(
            course, status.HTTP_403_FORBIDDEN, "Course 9", 1, "I"
        )
        self.logout()

    def _partial_update_course_helper(self, course, status_code, title, user_id, role):
        """Helper function to test update course functionality.

        Args:
            course (Course): `Course` model instance
            status_code (int): Expected status code of the API call
            title (str): Title of the course
            user_id (int): User id
            role (str): Role of the user (instructor/ta/student)
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
        }

        url = reverse("course:course-update-course", args=[course.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            self.assertEqual(return_data["title"], data["title"])
            self.assertEqual(return_data["code"], data["code"])
            self.assertEqual(return_data["owner"], data["owner"])

    def test_partial_update_course(self):
        """Test to check: partial update of the course."""
        course = Course(
            owner_id=1,
            title="Course 10",
            course_type="O",
        )
        course.save()
        discussion_forum = DiscussionForum(
            course=course,
            anonymous_to_instructor=True,
            send_email_to_all=True,
        )
        discussion_forum.save()

        # Update by instructor
        self.login(**ins_cred)
        self._partial_update_course_helper(
            course, status.HTTP_200_OK, "Course 11", 1, "I"
        )
        self.logout()

        # Update by ta
        self.login(**ta_cred)
        self._partial_update_course_helper(
            course, status.HTTP_200_OK, "Course 12", 2, "T"
        )
        self.logout()

        # HTTP_403_FORBIDDEN due to IsInstructorOrTAOrReadOnly permission class
        self.login(**stu_cred)
        self._partial_update_course_helper(
            course, status.HTTP_403_FORBIDDEN, "Course 13", 3, "S"
        )
        self.logout()

        # HTTP_401_UNAUTHORIZED due to IsInstructorOrTAOrReadOnly permission class
        self._partial_update_course_helper(
            course, status.HTTP_401_UNAUTHORIZED, "Course 14", 1, "I"
        )

        # HTTP_403_FORBIDDEN due to IntegrityError of the database
        self.login(**ins_cred)
        with transaction.atomic():
            self._partial_update_course_helper(
                course, status.HTTP_403_FORBIDDEN, "Course", 1, "I"
            )
        self.logout()

        # HTTP_400_BAD_REQUEST due to serialization errors
        self.login(**ins_cred)
        self._partial_update_course_helper(
            course, status.HTTP_400_BAD_REQUEST, "", 1, "I"
        )
        self.logout()

        # HTTP_403_FORBIDDEN due to SubscriptionHistory expiry/does not exist
        subscription_history = SubscriptionHistory.objects.get(user_id=2)
        subscription_history.delete()
        self.login(**ins_cred)
        self._partial_update_course_helper(
            course, status.HTTP_403_FORBIDDEN, "Course 15", 1, "I"
        )
        self.logout()

    def _delete_course_helper(self, status_code, title, user_id, role):
        """Helper function to test delete course functionality

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
        """Test to check: delete the course."""
        # Delete by owner
        self.login(**ins_cred)
        self._delete_course_helper(status.HTTP_204_NO_CONTENT, "Course 17", 1, "I")
        self.logout()

        # HTTP_403_FORBIDDEN due to IsOwner permissioon class (delete by ta)
        self.login(**ta_cred)
        self._delete_course_helper(status.HTTP_403_FORBIDDEN, "Course 18", 2, "T")
        self.logout()

        # HTTP_403_FORBIDDEN due to IsOwner permissioon class (delete by student)
        self.login(**stu_cred)
        self._delete_course_helper(status.HTTP_403_FORBIDDEN, "Course 19", 3, "S")
        self.logout()

        # HTTP_401_UNAUTHORIZED due to IsOwner permissioon class
        self._delete_course_helper(status.HTTP_401_UNAUTHORIZED, "Course 16", 1, "I")


# class CourseHistoryViewSetTest(APITestCase):
#     """Test for CourseHistoryViewSet."""

#     fixtures = [
#         "users.test.yaml",
#         "departments.test.yaml",
#         "colleges.test.yaml",
#         "courses.test.yaml",
#         "coursehistories.test.yaml",
#     ]

#     def login(self, email, password):
#         self.client.login(email=email, password=password)

#     def logout(self):
#         self.client.logout()

#     def _list_course_histories_helper(self, status_code, course_id):
#         """Helper function to test list all course histories functionality.

#         Args:
#             status_code (int): Expected status code of the API call
#             course_id (int): Course id
#         """
#         url = reverse("course:coursehistory-list-course-histories", args=[course_id])
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status_code)
#         if response.status_code == status.HTTP_200_OK:
#             self.assertEqual(
#                 len(response.data["results"]),
#                 CourseHistory.objects.filter(course_id=course_id).count(),
#             )

#     def test_list_course_histories(self):
#         """Test to check: list all courses histories."""
#         course_id = 1  # course with id 1 is created by django fixture

#         # Listed by instructor
#         self.login(**ins_cred)
#         self._list_course_histories_helper(status.HTTP_200_OK, course_id)
#         self.logout()

#         # Listed by ta
#         self.login(**ta_cred)
#         self._list_course_histories_helper(status.HTTP_200_OK, course_id)
#         self.logout()

#         # Listed by student
#         self.login(**stu_cred)
#         self._list_course_histories_helper(status.HTTP_200_OK, course_id)
#         self.logout()

#         # HTTP_401_UNAUTHORIZED due to IsInstructorOrTAOrStudent/IsOwner
#         # permission class
#         self._list_course_histories_helper(status.HTTP_401_UNAUTHORIZED, course_id)

#         # HTTP_403_FORBIDDEN due to IsInstructorOrTAOrStudent/IsOwner permission class
#         course_id = 4  # course with id 4 is created by django fixture
#         self.login(**ins_cred)
#         self._list_course_histories_helper(status.HTTP_403_FORBIDDEN, course_id)
#         self.logout()

#     def _retrieve_course_history_helper(self, status_code, course_history_id):
#         """Helper function to test retrieve the course history functionality.

#         Args:
#             status_code (int): Expected status code of the API call
#             course_history_id (int): Course history id
#         """
#         url = reverse(
#             "course:coursehistory-retrieve-course-history",
#             args=[course_history_id],
#         )
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status_code)
#         if response.status_code == status.HTTP_200_OK:
#             self.assertEqual(response.data["id"], course_history_id)

#     def test_retrieve_course_history(self):
#         """Test to check: retrieve the courses history."""
#         # Retrieved by instructor
#         course_history_id = 1
#         self.login(**ins_cred)
#         self._retrieve_course_history_helper(status.HTTP_200_OK, course_history_id)
#         self.logout()

#         # Retrieved by ta
#         course_history_id = 2
#         self.login(**ta_cred)
#         self._retrieve_course_history_helper(status.HTTP_200_OK, course_history_id)
#         self.logout()

#         # Retrieved by student
#         course_history_id = 3
#         self.login(**stu_cred)
#         self._retrieve_course_history_helper(status.HTTP_200_OK, course_history_id)
#         self.logout()

#         # HTTP_401_UNAUTHORIZED due to IsInstructorOrTAOrStudent permission class
#         self._retrieve_course_history_helper(
#             status.HTTP_401_UNAUTHORIZED, course_history_id
#         )

#         # HTTP_404_NOT_FOUND due to CourseHistory object does not exist
#         course_history_id = 60
#         self.login(**ins_cred)
#         self._retrieve_course_history_helper(
#             status.HTTP_404_NOT_FOUND, course_history_id
#         )
#         self.logout()

#     def _create_course_history_helper(self, status_code, user_id, role):
#         """Helper function to test create course history functionality

#         Args:
#             status_code (int): Expected status code of the API call
#             user_id (int): User id
#             role (str): User role (instructor/ta/student)
#         """
#         course_id = 4  # course with id 4 is created by django fixture
#         data = {
#             "user": user_id,
#             "course": course_id,
#             "role": role,
#             "status": "E",
#         }
#         url = reverse("course:coursehistory-create-course-history")
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_201_CREATED:
#             response_data = response.data
#             for field in ["id", "created_on", "modified_on"]:
#                 response_data.pop(field)
#             self.assertEqual(response_data, data)

#     def test_create_course_history(self):
#         """Test to check: create the course history."""
#         # Created by instructor
#         self.login(**ins_cred)
#         self._create_course_history_helper(status.HTTP_201_CREATED, 1, "I")
#         self.logout()

#         # Created by ta
#         self.login(**ta_cred)
#         self._create_course_history_helper(status.HTTP_201_CREATED, 2, "T")
#         self.logout()

#         # Created by student
#         self.login(**stu_cred)
#         self._create_course_history_helper(status.HTTP_201_CREATED, 3, "S")
#         self.logout()

#         # HTTP_401_UNAUTHORIZED due to IsInstructorOrTAOrStudent/IsOwner
#         # permission class
#         self._create_course_history_helper(status.HTTP_401_UNAUTHORIZED, 1, "I")

#         # HTTP_403_FORBIDDEN due to IntegrityError of the database
#         self.login(**ins_cred)
#         with transaction.atomic():
#             self._create_course_history_helper(status.HTTP_403_FORBIDDEN, 1, "I")
#         self.logout()

#         # HTTP_400_BAD_REQUEST due to serialization errors
#         self.login(**ins_cred)
#    self._create_course_history_helper(status.HTTP_400_BAD_REQUEST, 1, "INSTRUCTOR")
#         self.logout()

#     def _update_course_history_helper(
#         self, status_code, user_id, role, user_status="U"
#     ):
#         """Helper function to test update course functionality

#         Args:
#             status_code (int): Expected status code of the API call
#             user_id (int): User id
#             role (str): Role of the user (instructor/ta/student)
#             user_status (str): Status of user (enrolled/unerolled/pending)
#         """
#         course_id = 4  # course with id 4 is created by django fixture
#         course_history, _ = CourseHistory.objects.get_or_create(
#             user_id=user_id,
#             course_id=course_id,
#             role=role,
#             status="E",
#         )
#         data = {
#             "user": user_id,
#             "course": course_id,
#             "role": role,
#             "status": user_status,
#         }
#         url = reverse(
#             "course:coursehistory-update-course-history",
#             args=[course_history.id],
#         )
#         response = self.client.put(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_200_OK:
#             response_data = response.data
#             for field in ["id", "created_on", "modified_on"]:
#                 response_data.pop(field)
#             self.assertEqual(response_data, data)
#         course_history.delete()

#     def test_update_course_history(self):
#         """Test to check: update the course history."""
#         # Updated by instructor
#         self.login(**ins_cred)
#         self._update_course_history_helper(status.HTTP_200_OK, 1, "I")
#         self.logout()

#         # Updated by ta
#         self.login(**ta_cred)
#         self._update_course_history_helper(status.HTTP_200_OK, 2, "T")
#         self.logout()

#         # Updated by student
#         self.login(**stu_cred)
#         self._update_course_history_helper(status.HTTP_200_OK, 3, "S")
#         self.logout()

#         # HTTP_401_UNAUTHORIZED due to IsInstructorOrTAOrStudent/IsOwner
#         # permission class
#         self._update_course_history_helper(status.HTTP_401_UNAUTHORIZED, 1, "I")

#         # HTTP_400_BAD_REQUEST due to serialization errors
#         self.login(**ins_cred)
#         self._update_course_history_helper(
#             status.HTTP_400_BAD_REQUEST, 1, "I", "Enrolled"
#         )
#         self.logout()

#     def _partial_update_course_history_helper(
#         self, status_code, user_id, role, user_status="U"
#     ):
#         """Helper function to test partial update course functionality

#         Args:
#             status_code (int): expected status code of the API call
#             user_id (int): user id
#             role (str): role of the user (instructor/ta/student)
#             user_status (str): Status of user (enrolled/unerolled/pending)
#         """
#         course_id = 4  # course with id 4 is created by django fixture
#         course_history, _ = CourseHistory.objects.get_or_create(
#             user_id=user_id,
#             course_id=course_id,
#             role=role,
#             status="E",
#         )
#         data = {
#             "status": user_status,
#         }
#         url = reverse(
#             "course:coursehistory-update-course-history",
#             args=[course_history.id],
#         )
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status_code)
#         if status_code == status.HTTP_200_OK:
#             self.assertEqual(response.data["status"], data["status"])
#         course_history.delete()

#     def test_partial_update_course_history(self):
#         """Test to check: partial update the course history."""
#         # Updated by instructor
#         self.login(**ins_cred)
#         self._partial_update_course_history_helper(status.HTTP_200_OK, 1, "I")
#         self.logout()

#         # Updated by ta
#         self.login(**ta_cred)
#         self._partial_update_course_history_helper(status.HTTP_200_OK, 2, "T")
#         self.logout()

#         # Updated by student
#         self.login(**stu_cred)
#         self._partial_update_course_history_helper(status.HTTP_200_OK, 3, "S")
#         self.logout()

#         # HTTP_401_UNAUTHORIZED due to IsInstructorOrTAOrStudent/IsOwner
#         # permission class
#     self._partial_update_course_history_helper(status.HTTP_401_UNAUTHORIZED, 1, "I")

#         # HTTP_400_BAD_REQUEST due to serialization errors
#         self.login(**ins_cred)
#         self._partial_update_course_history_helper(
#             status.HTTP_400_BAD_REQUEST, 1, "I", "Enrolled"
#         )
#         self.logout()


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

    def _list_pages_helper(self):
        """Helper function to test list pages functionality."""
        course_id = 1  # course with id 1 is created by django fixture
        url = reverse("course:page-list-pages", args=[course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), Page.objects.filter(course_id=course_id).count()
        )

    def test_list_pages(self):
        """Test to check: list all pages."""
        self.login(**ins_cred)
        self._list_pages_helper()
        self.logout()
        self.login(**ta_cred)
        self._list_pages_helper()
        self.logout()
        self.login(**stu_cred)
        self._list_pages_helper()
        self.logout()

    def _retrieve_page_helper(self):
        """Helper function to test the retrieve section functionality."""
        page_id = 1  # page with id 1 is created by django fixture
        url = reverse("course:page-retrieve-page", args=[page_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], page_id)

    def test_retrieve_page(self):
        """Test to check: retrieve the page."""
        self.login(**ins_cred)
        self._retrieve_page_helper()
        self.logout()
        self.login(**ta_cred)
        self._retrieve_page_helper()
        self.logout()
        self.login(**stu_cred)
        self._retrieve_page_helper()
        self.logout()

    def _create_page_helper(self, title, status_code):
        """Helper function to test create the page functionality.

        Args:
            title (str): title of the page
            status_code (int): expected status code of the API call
        """
        course_id = 1  # course with id 1 is created by django fixture
        url = reverse("course:page-create-page")
        data = {
            "course": course_id,
            "title": title,
            "description": "Page description",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            for field in ["id", "created_on", "modified_on"]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_create_page(self):
        """Test to check: create a page."""
        self.login(**ins_cred)
        self._create_page_helper("Page 3", status.HTTP_201_CREATED)
        self.logout()
        self.login(**ta_cred)
        self._create_page_helper("Page 4", status.HTTP_201_CREATED)
        self.logout()
        self.login(**stu_cred)
        self._create_page_helper("Page 5", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _update_page_helper(self, page, title, status_code):
        """Helper function to test update of the page functionality.

        Args:
            page (Page): `Page` model instance
            title (str): title of the page
            status_code (int): expected status code of the API call
        """
        data = {
            "course": 1,
            "title": title,
            "description": "Description of page",
        }
        url = reverse("course:page-update-page", args=[page.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            for field in ["id", "created_on", "modified_on"]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_update_page(self):
        """Test to check: update the page."""
        page = Page(title="Page 6", course_id=1)
        page.save()
        self.login(**ins_cred)
        self._update_page_helper(page, "Page 7", status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._update_page_helper(page, "Page 8", status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._update_page_helper(page, "Page 9", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _partial_update_page_helper(self, page, title, status_code):
        """Helper function to test partial update of the page functionality.

        Args:
            page (Page): `Page` model instance
            title (str): title of the page
            status_code (int): expected status code of the API call
        """
        data = {
            "title": title,
        }
        url = reverse("course:page-update-page", args=[page.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["title"], data["title"])

    def test_partial_update_page(self):
        """Test to check: partial update of the page."""
        page = Page(title="Page 10", course_id=1)
        page.save()
        self.login(**ins_cred)
        self._partial_update_page_helper(page, "Page 11", status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._partial_update_page_helper(page, "Page 12", status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._partial_update_page_helper(page, "Page 13", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _delete_page_helper(self, status_code):
        """Helper function to test delete the page functionality.

        Args:
            status_code (int): expected status code of the API call
        """
        page = Page(course_id=1, title="Page 14")
        page.save()
        url = reverse(("course:page-delete-page"), args=[page.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Page.objects.filter(id=page.id).count(), 0)

    def test_delete_page(self):
        """Test to check: delete the page."""
        self.login(**ins_cred)
        self._delete_page_helper(status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**ta_cred)
        self._delete_page_helper(status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**stu_cred)
        self._delete_page_helper(status.HTTP_403_FORBIDDEN)
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
