from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from course.models import Chapter, Course, CourseHistory, Page, Section
from discussion_forum.models import DiscussionForum


# These users are created by django fixtures
# instructor has user id 1
ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
# ta has user id 2
ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
# student has user id 3
stu_cred = {"email": "student@bodhitree.com", "password": "student"}


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
        url = reverse("course:course-detail", kwargs={"pk": course_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], course_id)

    def _create_course_helper(self, status_code, title, owner_id):
        """Helper function to test create course functionality.

        Args:
            status_code (int): expected status code of the API call
            title (str): title of the course
            owner_id (int): user id
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
        self.login(**ins_cred)
        self._create_course_helper(status.HTTP_201_CREATED, "Course 1", 1)
        self.logout()
        self.login(**ta_cred)
        self._create_course_helper(status.HTTP_403_FORBIDDEN, "Course 2", 2)
        self.logout()
        self.login(**stu_cred)
        self._create_course_helper(status.HTTP_403_FORBIDDEN, "Course 3", 3)
        self.logout()

    def _update_course_helper(self, course, status_code, title, user_id, role):
        """Helper function to test update course functionality.

        Args:
            course (Course): `Course` model instance
            status_code (int): expected status code of the API call
            title (str): title of the course
            user_id (int): user id
            role (str): role of the user (instructor/ta/student)
        """
        course_history = CourseHistory(
            user_id=user_id,
            course=course,
            role=role,
            status="E",
        )
        course_history.save()
        data = {
            "owner": 1,
            "code": "111",
            "title": title,
            "description": "This is the description of the course",
            "is_published": False,
            "course_type": "O",
            "chapters_sequence": [],
            "institute": 1,
            "department": 1,
            "df_settings": {
                "anonymous_to_instructor": False,
                "send_email_to_all": False,
            },
        }
        url = reverse("course:course-update-course", kwargs={"pk": course.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            for field in ["id", "image", "created_on", "modified_on"]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_update_course(self):
        """Test to check: update the course."""
        course = Course(
            owner_id=1,
            title="Course 4",
            course_type="O",
        )
        course.save()
        discussion_forum = DiscussionForum(
            course=course,
            anonymous_to_instructor="True",
            send_email_to_all="True",
        )
        discussion_forum.save()
        self.login(**ins_cred)
        self._update_course_helper(course, status.HTTP_200_OK, "Course 5", 1, "I")
        self.logout()
        self.login(**ta_cred)
        self._update_course_helper(course, status.HTTP_200_OK, "Course 6", 2, "T")
        self.logout()
        self.login(**stu_cred)
        self._update_course_helper(
            course, status.HTTP_403_FORBIDDEN, "Course 7", 3, "S"
        )
        self.logout()

    def _partial_update_course_helper(self, course, status_code, title, user_id, role):
        """Helper function to test update course functionality.

        Args:
            course (Course): `Course` model instance
            status_code (int): expected status code of the API call
            title (str): title of the course
            user_id (int): user id
            role (str): role of the user (instructor/ta/student)
        """
        course_history = CourseHistory(
            user_id=user_id,
            course=course,
            role=role,
            status="E",
        )
        course_history.save()
        data = {
            "title": title,
            "course_type": "M",
        }
        url = reverse("course:course-update-course", kwargs={"pk": course.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            self.assertEqual(return_data["title"], data["title"])
            self.assertEqual(return_data["course_type"], data["course_type"])

    def test_partial_update_course(self):
        """Test to check: partial update the course."""
        course = Course(
            owner_id=1,
            title="Course 8",
            course_type="O",
        )
        course.save()
        discussion_forum = DiscussionForum(
            course=course,
            anonymous_to_instructor="True",
            send_email_to_all="True",
        )
        discussion_forum.save()
        self.login(**ins_cred)
        self._partial_update_course_helper(
            course, status.HTTP_200_OK, "Course 9", 1, "I"
        )
        self.logout()
        self.login(**ta_cred)
        self._partial_update_course_helper(
            course, status.HTTP_200_OK, "Course 10", 2, "T"
        )
        self.logout()
        self.login(**stu_cred)
        self._partial_update_course_helper(
            course, status.HTTP_403_FORBIDDEN, "Course 11", 3, "S"
        )
        self.logout()

    def _delete_course_helper(self, status_code, title, user_id, role):
        """Helper function to test delete course functionality

        Args:
            status_code (int): expected status code of the API call
            title (str): title of the course
            user_id (int): user id
            role (str): role of the user (instructor/ta/student)
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
        url = reverse(("course:course-delete-course"), kwargs={"pk": course.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Course.objects.filter(id=course.id).count(), 0)

    def test_delete_course(self):
        """Test to check: delete the course."""
        self.login(**ins_cred)
        self._delete_course_helper(status.HTTP_204_NO_CONTENT, "Course 12", 1, "I")
        self.logout()
        self.login(**ta_cred)
        self._delete_course_helper(status.HTTP_403_FORBIDDEN, "Course 13", 2, "T")
        self.logout()
        self.login(**stu_cred)
        self._delete_course_helper(status.HTTP_403_FORBIDDEN, "Course 14", 3, "S")
        self.logout()


class CourseHistoryViewSetTest(APITestCase):
    """Test for CourseHistoryViewSet."""

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

    def _list_course_histories_helper(self, status_code):
        """Helper function to test list all course histories functionality.

        Args:
            status_code (int): expected status code of the API call
        """
        course_id = 1  # course with id 1 is created by django fixture
        url = reverse(
            "course:coursehistory-list-course-histories", kwargs={"pk": course_id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data["results"]), CourseHistory.objects.all().count()
            )

    def test_list_course_histories(self):
        """Test to check: list all courses histories."""
        self.login(**ins_cred)
        self._list_course_histories_helper(status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._list_course_histories_helper(status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._list_course_histories_helper(status.HTTP_200_OK)
        self.logout()

    def _retrieve_course_history_helper(self, status_code, user_id):
        """Helper function to test retrieve the course history functionality.

        Args:
            status_code (int): expected status code of the API call
            user_id (int): user id
        """
        course_history_id = user_id
        url = reverse(
            "course:coursehistory-retrieve-course-history",
            kwargs={"pk": course_history_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["id"], user_id)

    def test_retrieve_course_history(self):
        """Test to check: retrieve the courses history."""
        self.login(**ins_cred)
        self._retrieve_course_history_helper(status.HTTP_200_OK, 1)
        self.logout()
        self.login(**ta_cred)
        self._retrieve_course_history_helper(status.HTTP_200_OK, 2)
        self.logout()
        self.login(**stu_cred)
        self._retrieve_course_history_helper(status.HTTP_200_OK, 3)
        self.logout()

    def _create_course_history_helper(self, status_code, user_id, role):
        """Helper function to test create course history functionality

        Args:
            status_code (int): expected status code of the API call
            user_id (int): user id
            role (str): user role (instructor/ta/student)
        """
        course_id = 2  # course with id 2 is created by django fixture
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
            for field in ["id", "created_on", "modified_on"]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_create_course_history(self):
        """Test to check: create the course history."""
        self.login(**ins_cred)
        self._create_course_history_helper(status.HTTP_201_CREATED, 1, "I")
        self.logout()
        self.login(**ta_cred)
        self._create_course_history_helper(status.HTTP_201_CREATED, 2, "T")
        self.logout()
        self.login(**stu_cred)
        self._create_course_history_helper(status.HTTP_201_CREATED, 3, "S")
        self.logout()

    def _update_course_history_helper(self, status_code, user_id, role):
        """Helper function to test update course functionality

        Args:
            status_code (int): expected status code of the API call
            user_id (int): user id
            role (str): role of the user (instructor/ta/student)
        """
        course_id = 2  # course with id 2 is created by django fixture
        course_history = CourseHistory(
            user_id=user_id,
            course_id=course_id,
            role=role,
            status="E",
        )
        course_history.save()
        data = {
            "user": user_id,
            "course": course_id,
            "role": role,
            "status": "U",
        }
        url = reverse(
            "course:coursehistory-update-course-history",
            kwargs={"pk": course_history.id},
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            for field in ["id", "created_on", "modified_on"]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_update_course_history(self):
        """Test to check: update the course history."""
        self.login(**ins_cred)
        self._update_course_history_helper(status.HTTP_200_OK, 1, "I")
        self.logout()
        self.login(**ta_cred)
        self._update_course_history_helper(status.HTTP_200_OK, 2, "T")
        self.logout()
        self.login(**stu_cred)
        self._update_course_history_helper(status.HTTP_200_OK, 3, "S")
        self.logout()

    def _partial_update_course_history_helper(self, status_code, user_id, role):
        """Helper function to test partial update course functionality

        Args:
            status_code (int): expected status code of the API call
            user_id (int): user id
            role (str): role of the user (instructor/ta/student)
        """
        course_id = 2  # course with id 2 is created by django fixture
        course_history = CourseHistory(
            user_id=user_id,
            course_id=course_id,
            role=role,
            status="E",
        )
        course_history.save()
        data = {
            "status": "U",
        }
        url = reverse(
            "course:coursehistory-update-course-history",
            kwargs={"pk": course_history.id},
        )
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["status"], data["status"])

    def test_partial_update_course_history(self):
        """Test to check: partial update the course history."""
        self.login(**ins_cred)
        self._partial_update_course_history_helper(status.HTTP_200_OK, 1, "I")
        self.logout()
        self.login(**ta_cred)
        self._partial_update_course_history_helper(status.HTTP_200_OK, 2, "T")
        self.logout()
        self.login(**stu_cred)
        self._partial_update_course_history_helper(status.HTTP_200_OK, 3, "S")
        self.logout()


class ChapterViewSetTest(APITestCase):
    """Test for ChapterViewSetTest."""

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

    def _list_chapters_helper(self):
        """Helper function to test list chapters functionality."""
        course_id = 1  # course with id 1 is created by django fixture
        url = reverse("course:chapter-list-chapters", args=[course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Chapter.objects.all().count())

    def test_list_chapters(self):
        """Test to check: list all chapters."""
        self.login(**ins_cred)
        self._list_chapters_helper()
        self.logout()
        self.login(**ta_cred)
        self._list_chapters_helper()
        self.logout()
        self.login(**stu_cred)
        self._list_chapters_helper()
        self.logout()

    def _retrieve_chapter_helper(self):
        """Helper function to test the retrieve section functionality."""
        chapter_id = 1  # chapter with id 1 is created by django fixture
        url = reverse("course:chapter-retrieve-chapter", args=[chapter_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], chapter_id)

    def test_retrieve_chapter(self):
        """Test to check: retrieve the chapter."""
        self.login(**ins_cred)
        self._retrieve_chapter_helper()
        self.logout()
        self.login(**ta_cred)
        self._retrieve_chapter_helper()
        self.logout()
        self.login(**stu_cred)
        self._retrieve_chapter_helper()
        self.logout()

    def _create_chapter_helper(self, title, status_code):
        """Helper function to test create the chapter functionality.

        Args:
            title (str): title of the chapter
            status_code (int): expected status code of the API call
        """
        course_id = 1  # course with id 1 is created by django fixture
        data = {
            "title": title,
            "course": course_id,
            "description": "This is the description of chapter",
        }
        url = reverse("course:chapter-create-chapter")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            return_data = response.data
            for field in ["id", "content_sequence", "created_on", "modified_on"]:
                return_data.pop(field)
            self.assertEqual(return_data, data)

    def test_create_chapter(self):
        """Test to check: create a chapter."""
        self.login(**ins_cred)
        self._create_chapter_helper("Chapter 3", status.HTTP_201_CREATED)
        self.logout()
        self.login(**ta_cred)
        self._create_chapter_helper("Chapter 4", status.HTTP_201_CREATED)
        self.logout()
        self.login(**stu_cred)
        self._create_chapter_helper("Chapter 5", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _update_chapters_helper(self, chapter, title, status_code):
        """Helper function to test update of the chapter functionality.

        Args:
            chapter (Chapter): `Chapter` model instance
            title (str): title of the chapter
            status_code (int): expected status code of the API call
        """
        data = {
            "title": title,
            "course": 1,
            "description": "Description of the chapter",
        }
        url = reverse(("course:chapter-update-chapter"), args=[chapter.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for field in ["id", "content_sequence", "created_on", "modified_on"]:
                return_data.pop(field)
            self.assertEqual(return_data, data)

    def test_update_chapter(self):
        """Test to check: update the chapter."""
        chapter = Chapter(title="Chapter 6", course_id=1)
        chapter.save()
        self.login(**ins_cred)
        self._update_chapters_helper(chapter, "Chapter 7", status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._update_chapters_helper(chapter, "Chapter 8", status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._update_chapters_helper(chapter, "Chapter 9", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _partial_update_chapter_helper(self, chapter, title, status_code):
        """Helper function to test partial update of the chapter functionality.

        Args:
            chapter (Chapter): `Chapter` model instance
            title (str): title of the chapter
            status_code (int): expected status code of the API call
        """
        data = {
            "title": title,
        }
        url = reverse(("course:chapter-update-chapter"), args=[chapter.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["title"], data["title"])

    def test_partial_update_chapter(self):
        """"Test to check: partial update the chapter."""
        chapter = Chapter(title="Chapter 10", course_id=1)
        chapter.save()
        self.login(**ins_cred)
        self._partial_update_chapter_helper(chapter, "Chapter 11", status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._partial_update_chapter_helper(chapter, "Chapter 12", status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._partial_update_chapter_helper(
            chapter, "Chapter 13", status.HTTP_403_FORBIDDEN
        )
        self.logout()

    def _delete_chapter_helper(self, status_code):
        """Helper function to test delete the chapter functionality.

        Args:
            status_code (int): expected status code of the API call
        """
        chapter = Chapter(title="Chapter 14", course_id=1)
        chapter.save()
        url = reverse(("course:chapter-delete-chapter"), args=[chapter.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Chapter.objects.filter(id=chapter.id).count(), 0)

    def test_delete_chapter(self):
        """Test to check: delete the chapter."""
        self.login(**ins_cred)
        self._delete_chapter_helper(status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**ta_cred)
        self._delete_chapter_helper(status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**stu_cred)
        self._delete_chapter_helper(status.HTTP_403_FORBIDDEN)
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
        self.assertEqual(len(response.data), Page.objects.all().count())

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

    def _list_sections_helper(self):
        """Helper function to test list sections functionality."""
        chapter_id = 1
        url = reverse("course:section-list-sections", args=[chapter_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Section.objects.all().count())

    def test_list_sections(self):
        """Test to check: list all sections."""
        self.login(**ins_cred)
        self._list_sections_helper()
        self.logout()
        self.login(**ta_cred)
        self._list_sections_helper()
        self.logout()
        self.login(**stu_cred)
        self._list_sections_helper()
        self.logout()

    def _retrieve_section_helper(self):
        """Helper function to test the retrieve section functionality."""
        section_id = 1
        url = reverse("course:section-retrieve-section", args=[section_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], section_id)

    def test_retrieve_section(self):
        """Test to check: retrieve the section."""
        self.login(**ins_cred)
        self._retrieve_section_helper()
        self.logout()
        self.login(**ta_cred)
        self._retrieve_section_helper()
        self.logout()
        self.login(**stu_cred)
        self._retrieve_section_helper()
        self.logout()

    def _create_section_helper(self, title, status_code):
        """Helper function to test create the section functionality.

        Args:
            title (str): title of the section
            status_code (int): expected status code of the API call
        """
        data = {
            "chapter": 1,
            "title": title,
            "description": "this is the section description",
            "content_sequence": [[1, 2]],  # (a,b) denotes (content type, content id)
        }
        url = reverse("course:section-create-section")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            return_data = response.data
            for field in ["id", "created_on", "modified_on"]:
                return_data.pop(field)
            self.assertEqual(return_data, data)

    def test_create_section(self):
        """Test to check: create a section."""
        self.login(**ins_cred)
        self._create_section_helper("Section 3", status.HTTP_201_CREATED)
        self.logout()
        self.login(**ta_cred)
        self._create_section_helper("Section 4", status.HTTP_201_CREATED)
        self.logout()
        self.login(**stu_cred)
        self._create_section_helper("Section 5", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _update_section_helper(self, section, title, status_code):
        """Helper function to test update the section functionality.

        Args:
            section (Section): `Section` model instance
            title (str): title of the section
            status_code (int): expected status code of the API call
        """
        data = {
            "title": title,
            "chapter": 1,
            "description": "Section description",
        }
        url = reverse(("course:section-update-section"), args=[section.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for filed in ["id", "content_sequence", "created_on", "modified_on"]:
                return_data.pop(filed)
            self.assertEqual(return_data, data)

    def test_update_section(self):
        """Test to check: update the section."""
        section = Section(title="Section 6", chapter_id=1)
        section.save()
        self.login(**ins_cred)
        self._update_section_helper(section, "Section 7", status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._update_section_helper(section, "Section 8", status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._update_section_helper(section, "Section 9", status.HTTP_403_FORBIDDEN)
        self.logout()

    def _partial_update_section_helper(self, section, title, status_code):
        """Helper function to test partial update the section functionality.

        Args:
            section (Section): `Section` model instance
            title (str): title of the section
            status_code (int): expected status code of the API call
        """
        data = {
            "title": title,
            "description": "New section description",
        }
        url = reverse(("course:section-update-section"), args=[section.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            self.assertEqual(response_data["title"], data["title"])
            self.assertEqual(response_data["description"], data["description"])

    def test_partial_update_section(self):
        """Test to check: partial update the section."""
        section = Section(title="Section 10", chapter_id=1)
        section.save()
        self.login(**ins_cred)
        self._partial_update_section_helper(section, "Section 11", status.HTTP_200_OK)
        self.logout()
        self.login(**ta_cred)
        self._partial_update_section_helper(section, "Section 12", status.HTTP_200_OK)
        self.logout()
        self.login(**stu_cred)
        self._partial_update_section_helper(
            section, "Section 13", status.HTTP_403_FORBIDDEN
        )
        self.logout()

    def _delete_section_helper(self, status_code):
        """Helper function to test delete the section functionality.

        Args:
            status_code (int): expected status code of the API call
        """
        section = Section(title="Section 14", chapter_id=1)
        section.save()
        url = reverse(("course:section-delete-section"), args=[section.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Section.objects.filter(id=section.id).count(), 0)

    def test_delete_section(self):
        """Test to check: delete the section."""
        self.login(**ins_cred)
        self._delete_section_helper(status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**ta_cred)
        self._delete_section_helper(status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**stu_cred)
        self._delete_section_helper(status.HTTP_403_FORBIDDEN)
        self.logout()
