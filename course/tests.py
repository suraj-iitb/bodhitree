from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from course.models import Chapter, Course, CourseHistory, Page, Section
from discussion_forum.models import DiscussionForum
from registration.models import User


ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
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

    def test_get_courses(self):
        """Ensure we can get all Course objects."""
        url = reverse("course:course-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        no_of_courses = Course.objects.all().count()
        self.assertEqual(len(response.data["results"]), no_of_courses)

    def test_get_course(self):
        """Ensure we can get one Course object."""
        course_id = 1
        url = reverse("course:course-detail", kwargs={"pk": course_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], course_id)

    def _create_course_helper(self, status_code, title, owner_id):
        data = {
            "owner": owner_id,
            "code": "101",
            "title": title,
            "description": "This is the description of the course",
            "is_published": False,
            "course_type": "O",
            "chapters_sequence": [1, 2],
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
        """Ensure we can create a new Course object."""
        self.login(**ins_cred)
        self._create_course_helper(status.HTTP_201_CREATED, "Course 1", 1)
        self.logout()
        self.login(**ta_cred)
        self._create_course_helper(status.HTTP_403_FORBIDDEN, "Course 2", 2)
        self.logout()
        self.login(**stu_cred)
        self._create_course_helper(status.HTTP_403_FORBIDDEN, "Course 3", 3)
        self.logout()

    def update_course_helper(self, course, status_code, title, user_id, role):
        course_history = CourseHistory(
            user_id=user_id, course=course, role=role, status="E"
        )
        course_history.save()
        data = {
            "owner": 1,
            "code": "111",
            "title": title,
            "description": "This is the description of the course",
            "is_published": False,
            "course_type": "O",
            "chapters_sequence": [1, 2],
            "institute": 1,
            "department": 1,
            "df_settings": {
                "anonymous_to_instructor": True,
                "send_email_to_all": False,
            },
        }
        url = reverse("course:course-update-course", kwargs={"pk": course.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            response_data = response.data
            for field in ["created_on", "modified_on", "image", "id"]:
                response_data.pop(field)
            self.assertEqual(response_data, data)

    def test_update_course(self):
        """Ensure we can update an existing Course object."""
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
        self.update_course_helper(course, status.HTTP_200_OK, "Course 5", 1, "I")
        self.logout()
        self.login(**ta_cred)
        self.update_course_helper(course, status.HTTP_200_OK, "Course 6", 2, "T")
        self.logout()
        self.login(**stu_cred)
        self.update_course_helper(course, status.HTTP_403_FORBIDDEN, "Course 7", 3, "S")
        self.logout()

    def partial_update_course_helper(self, course, status_code, title, user_id, role):
        course_history = CourseHistory(
            user_id=user_id, course=course, role=role, status="E"
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

    def _test_partial_update_course(self):
        """Ensure we can partially update an existing Course object."""
        course = Course(owner_id=1, title="Course 8", course_type="O")
        course.save()
        discussion_forum = DiscussionForum(
            course=course,
            anonymous_to_instructor="True",
            send_email_to_all="True",
        )
        discussion_forum.save()
        self.login(**ins_cred)
        self._test_partial_update_course(course, status.HTTP_200_OK, "Course 9", 1, "I")
        self.logout()
        self.login(**ta_cred)
        self._test_partial_update_course(
            course, status.HTTP_200_OK, "Course 10", 2, "T"
        )
        self.logout()
        self.login(**stu_cred)
        self._test_partial_update_course(
            course, status.HTTP_403_FORBIDDEN, "Course 11", 3, "S"
        )
        self.logout()

    def _delete_course_helper(self, status_code, title, user_id, role):
        course = Course(owner_id=1, title=title, course_type="O")
        course.save()
        discussion_forum = DiscussionForum(
            course=course,
            anonymous_to_instructor="True",
            send_email_to_all="True",
        )
        discussion_forum.save()
        course_history = CourseHistory(
            user_id=user_id, course_id=course.id, role=role, status="E"
        )
        course_history.save()
        url = reverse(("course:course-delete-course"), kwargs={"pk": course.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Course.objects.filter(id=course.id).count(), 0)

    def test_delete_course(self):
        """Ensure we can delete an existing Course object."""
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
    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.user = User.objects.create_user("test1@test.com", "Test@1001")
        cls.user.save()
        cls.course1 = Course(owner_id=cls.user.id, title="Course1", course_type="O")
        cls.course1.save()
        cls.course_history1 = CourseHistory(
            user_id=cls.user.id, course_id=cls.course1.id, role="I", status="E"
        )
        cls.course_history1.save()

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def test_get_coursehistories(self):
        """
        Ensure we can get all Course objects.
        """
        url = reverse("course:coursehistory-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_coursehistory(self):
        """
        Ensure we can get one Course object.
        """
        url = reverse(
            "course:coursehistory-detail",
            kwargs={"pk": CourseHistoryViewSetTest.course_history1.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_coursehistory(self):
        """
        Ensure we can create a new Course object.
        """
        user = User.objects.create_user("test2@test.com", "Test@1002")
        user.save()
        course1 = Course(owner_id=user.id, title="Course2", course_type="O")
        course1.save()
        self.client.login(email="test2@test.com", password="Test@1002")
        data = {
            "user": user.id,
            "course": course1.id,
            "role": "T",
            "status": "E",
        }
        url = reverse("course:coursehistory-list")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_coursehistories(self):
        """
        Ensure we can update an existing Course object.
        """
        user = User.objects.create_user("test3@test.com", "Test@1003")
        user.save()
        course1 = Course(owner_id=user.id, title="Course1", course_type="O")
        course1.save()
        user2 = User.objects.create_user("test4@test.com", "Test@1004")
        user2.save()
        course2 = Course(owner_id=user2.id, title="Course1", course_type="O")
        course2.save()
        self.client.login(email="test3@test.com", password="Test@1003")
        course_history = CourseHistory(
            user_id=user.id, course_id=course1.id, role="T", status="E"
        )
        course_history.save()
        data = {
            "user": user2.id,
            "course": course2.id,
            "role": "T",
            "status": "E",
        }
        url = reverse(("course:coursehistory-detail"), kwargs={"pk": course_history.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_coursehistory(self):
        """
        Ensure we can partially update an existing Course object.
        """
        user = User.objects.create_user("test5@test.com", "Test@1005")
        user.save()
        course1 = Course(owner_id=user.id, title="Course1", course_type="O")
        course1.save()
        self.client.login(email="test5@test.com", password="Test@1005")
        course_history = CourseHistory(
            user_id=user.id, course_id=course1.id, role="T", status="E"
        )
        course_history.save()
        data = {
            "role": "I",
            "status": "E",
        }
        url = reverse(("course:coursehistory-detail"), kwargs={"pk": course_history.id})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_coursehistory(self):
        """
        Ensure we can delete an existing Course object.
        """
        user = User.objects.create_user("test6@test.com", "Test@1006")
        user.save()
        course1 = Course(owner_id=user.id, title="Course1", course_type="O")
        course1.save()
        self.client.login(email="test6@test.com", password="Test@1006")
        course_history = CourseHistory(
            user_id=user.id, course_id=course1.id, role="T", status="E"
        )
        course_history.save()
        url = reverse(("course:coursehistory-detail"), kwargs={"pk": course_history.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ChapterViewSetTest(APITestCase):
    fixtures = [
        "users.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "chapters.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
        cls.ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
        cls.stu_cred = {"email": "student@bodhitree.com", "password": "student"}

    def get_chapters_helper(self):
        url = reverse("course:chapter-list-chapters", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        length = Chapter.objects.all().count()
        self.assertEqual(len(response.data), length)

    def test_get_chapters(self):
        """
        Ensure we can get all Chapter objects.
        """
        self.client.login(**self.ins_cred)
        self.get_chapters_helper()
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.get_chapters_helper()
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.get_chapters_helper()
        self.client.logout()

    def get_chapter_helper(self, chapter_id):
        url = reverse(
            "course:chapter-retrieve-chapter",
            kwargs={"pk": chapter_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)

    def test_get_chapter(self):
        """
        Ensure we can get one chapter object.
        """
        chapter_id = 1
        self.client.login(**self.ins_cred)
        self.get_chapter_helper(chapter_id)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.get_chapter_helper(chapter_id)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.get_chapter_helper(chapter_id)
        self.client.logout()

    def create_chapter_helper(self, title, status_code):
        data = {
            "title": title,
            "course": 1,
            "description": "This is the description of chapter",
        }
        url = reverse("course:chapter-create-chapter", args=[1])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            return_data = response.data
            for k in ["created_on", "modified_on", "id", "content_sequence"]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_create_chapter(self):
        """
        Ensure we can create a new 'Chapter' object
        """
        self.client.login(**self.ins_cred)
        self.create_chapter_helper("Chapter3", status.HTTP_201_CREATED)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.create_chapter_helper("Chapter4", status.HTTP_201_CREATED)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.create_chapter_helper("Chapter5", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def update_chapters_helper(self, title, status_code):
        chapter1 = Chapter(title="Chapter77", course_id=1)
        chapter1.save()
        data = {
            "title": title,
            "course": 1,
            "description": "Description of chapter n",
        }
        url = reverse(("course:chapter-update-chapter"), kwargs={"pk": chapter1.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in ["created_on", "modified_on", "id", "content_sequence"]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_update_chapters(self):
        """
        Ensure we can update an existing Chapter object.
        """
        self.client.login(**self.ins_cred)
        self.update_chapters_helper("chapter78", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.update_chapters_helper("chapter79", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.update_chapters_helper("chapter80", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def partial_update_helper(self, title, status_code):
        chapter1 = Chapter(title="Chapter77", course_id=1)
        chapter1.save()
        data = {
            "title": title,
        }
        url = reverse(("course:chapter-update-chapter"), kwargs={"pk": chapter1.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in ["created_on", "modified_on", "id", "content_sequence"]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_partial_update_chapter(self):
        """
        Ensure we can partially update an existing Chapter object.
        """
        self.client.login(**self.ins_cred)
        self.update_chapters_helper("chapter78", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.update_chapters_helper("chapter79", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.update_chapters_helper("chapter80", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def delete_chapter_helper(self, title, status_code):
        chapter1 = Chapter(title=title, course_id=1)
        chapter1.save()
        url = reverse(("course:chapter-delete-chapter"), kwargs={"pk": chapter1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        try:
            Chapter.objects.get(id=chapter1.id)
        except ObjectDoesNotExist:
            self.assertEqual(response.status_code, status_code)

    def test_delete_chapter(self):
        """
        Ensure we can delete an existing Chapter object.
        """
        self.client.login(**self.ins_cred)
        self.delete_chapter_helper("chapter98", status.HTTP_204_NO_CONTENT)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.delete_chapter_helper("chapter99", status.HTTP_204_NO_CONTENT)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.delete_chapter_helper("chapter100", status.HTTP_403_FORBIDDEN)
        self.client.logout()


class PageViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.ins_cred = {"email": "ins@ins.com", "password": "ins"}
        cls.ta_cred = {"email": "ta@ta.com", "password": "ta"}
        cls.stu_cred = {"email": "stu@stu.com", "password": "stu"}
        cls.ins = User.objects.create_user(**cls.ins_cred)
        cls.ins.save()
        cls.ta = User.objects.create_user(**cls.ta_cred)
        cls.ta.save()
        cls.stu = User.objects.create_user(**cls.stu_cred)
        cls.stu.save()
        cls.course = Course(owner=cls.ins, title="Course", course_type="O")
        cls.course.save()
        cls.course_history_ins = CourseHistory(
            user=cls.ins, course=cls.course, role="I"
        )
        cls.course_history_ins.save()
        cls.course_history_ta = CourseHistory(user=cls.ta, course=cls.course, role="T")
        cls.course_history_ta.save()
        cls.course_history_stu = CourseHistory(
            user=cls.stu, course=cls.course, role="S"
        )
        cls.course_history_stu.save()
        cls.page = Page(course=cls.course, title="Page 1")
        cls.page.save()

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def add_page_helper(self, status_code, title):
        url = reverse("course:page-add-page", args=[PageViewSetTest.course.id])
        data = {
            "course": PageViewSetTest.course.id,
            "title": title,
            "description": "Page 2 description",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)

    def test_add_page(self):
        self.login(**PageViewSetTest.ins_cred)
        self.add_page_helper(status.HTTP_201_CREATED, "Page 2")
        self.logout()
        self.login(**PageViewSetTest.ta_cred)
        self.add_page_helper(status.HTTP_201_CREATED, "Page 3")
        self.logout()
        self.login(**PageViewSetTest.stu_cred)
        self.add_page_helper(status.HTTP_401_UNAUTHORIZED, "Page 4")
        self.logout()

    def list_pages_helper(self, status_code):
        url = reverse("course:page-list-pages", args=[PageViewSetTest.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)

    def test_list_pages(self):
        self.login(**PageViewSetTest.ins_cred)
        self.list_pages_helper(status.HTTP_200_OK)
        self.logout()
        self.login(**PageViewSetTest.ta_cred)
        self.list_pages_helper(status.HTTP_200_OK)
        self.logout()
        self.login(**PageViewSetTest.stu_cred)
        self.list_pages_helper(status.HTTP_200_OK)
        self.logout()

    def retrieve_page_helper(self, status_code):
        url = reverse(
            ("course:page-retrieve-page"), kwargs={"pk": PageViewSetTest.page.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)

    def test_retrieve_page(self):
        self.login(**PageViewSetTest.ins_cred)
        self.retrieve_page_helper(status.HTTP_200_OK)
        self.logout()
        self.login(**PageViewSetTest.ta_cred)
        self.retrieve_page_helper(status.HTTP_200_OK)
        self.logout()
        self.login(**PageViewSetTest.stu_cred)
        self.retrieve_page_helper(status.HTTP_200_OK)
        self.logout()

    def update_page_helper(self, status_code, title):
        page = Page(course=PageViewSetTest.course, title="Page 5")
        page.save()
        data = {
            "course": PageViewSetTest.course.id,
            "title": title,
            "description": "Description of page",
        }
        url = reverse("course:page-update-page", kwargs={"pk": page.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)

    def test_update_page(self):
        self.login(**PageViewSetTest.ins_cred)
        self.update_page_helper(status.HTTP_200_OK, "Page 6")
        self.logout()
        self.login(**PageViewSetTest.ta_cred)
        self.update_page_helper(status.HTTP_200_OK, "Page 7")
        self.logout()
        self.login(**PageViewSetTest.stu_cred)
        self.update_page_helper(status.HTTP_403_FORBIDDEN, "Page 8")
        self.logout()

    def partial_update_page_helper(self, status_code, title):
        page = Page(course=PageViewSetTest.course, title="Page 9")
        page.save()
        data = {"title": title}
        url = reverse(("course:page-update-page"), kwargs={"pk": page.id})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status_code)

    def test_partial_update_page(self):
        self.login(**PageViewSetTest.ins_cred)
        self.partial_update_page_helper(status.HTTP_200_OK, "Page 10")
        self.logout()
        self.login(**PageViewSetTest.ta_cred)
        self.partial_update_page_helper(status.HTTP_200_OK, "Page 11")
        self.logout()
        self.login(**PageViewSetTest.stu_cred)
        self.partial_update_page_helper(status.HTTP_403_FORBIDDEN, "Page 12")
        self.logout()

    def delete_page_helper(self, status_code):
        page = Page(course=PageViewSetTest.course, title="Page 13")
        page.save()
        url = reverse(("course:page-delete-page"), kwargs={"pk": page.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)

    def test_delete_page(self):
        self.login(**PageViewSetTest.ins_cred)
        self.delete_page_helper(status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**PageViewSetTest.ta_cred)
        self.delete_page_helper(status.HTTP_204_NO_CONTENT)
        self.logout()
        self.login(**PageViewSetTest.stu_cred)
        self.delete_page_helper(status.HTTP_403_FORBIDDEN)
        self.logout()


class SectionViewSetTest(APITestCase):
    fixtures = [
        "users.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "chapters.test.yaml",
        "sections.test.yaml",
    ]

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.ins_cred = {"email": "instructor@bodhitree.com", "password": "instructor"}
        cls.ta_cred = {"email": "ta@bodhitree.com", "password": "ta"}
        cls.stu_cred = {"email": "student@bodhitree.com", "password": "student"}

    def get_sections_helper(self):
        url = reverse("course:section-list-sections", args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        length = Section.objects.all().count()
        self.assertEqual(len(response.data), length)

    def test_get_sections(self):
        """
        Ensure we can get all Sections objects.
        """
        self.client.login(**self.ins_cred)
        self.get_sections_helper()
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.get_sections_helper()
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.get_sections_helper()
        self.client.logout()

    def get_section_helper(self, section_id):
        url = reverse(
            "course:section-retrieve-section",
            kwargs={"pk": section_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)

    def test_get_section(self):
        """
        Ensure we can get one section object.
        """
        section_id = 1
        self.client.login(**self.ins_cred)
        self.get_section_helper(section_id)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.get_section_helper(section_id)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.get_section_helper(section_id)
        self.client.logout()

    def create_section_helper(self, title, status_code):
        data = {
            "chapter": 1,
            "title": title,
            "description": "this is the section description",
            "content_sequence": [
                [1, 2],
            ],
        }
        url = reverse("course:section-create-section", args=[1])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            return_data = response.data
            for k in ["created_on", "modified_on", "id"]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_create_section(self):
        """
        Ensure we can create a new 'Section' object
        """
        self.client.login(**self.ins_cred)
        self.create_section_helper("Section3", status.HTTP_201_CREATED)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.create_section_helper("Section4", status.HTTP_201_CREATED)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.create_section_helper("Section5", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def update_sections_helper(self, title, status_code):
        section1 = Section(title="Section77", chapter_id=1)
        section1.save()
        data = {
            "title": title,
            "chapter": 1,
            "description": "SEction description",
        }
        url = reverse(("course:section-update-section"), kwargs={"pk": section1.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in ["created_on", "modified_on", "id", "content_sequence"]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_update_sections(self):
        """
        Ensure we can update an existing Section object.
        """
        self.client.login(**self.ins_cred)
        self.update_sections_helper("section78", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.update_sections_helper("section79", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.update_sections_helper("section80", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def partial_update_helper(self, title, status_code):
        section1 = Section(title="Section77", chapter_id=1)
        section1.save()
        data = {
            "title": title,
            "description": "New section description",
        }
        url = reverse(("course:section-update-section"), kwargs={"pk": section1.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK:
            return_data = response.data
            for k in ["created_on", "modified_on", "id", "content_sequence", "chapter"]:
                return_data.pop(k)
            self.assertEqual(return_data, data)

    def test_partial_update_section(self):
        """
        Ensure we can partially update an existing Section object.
        """
        self.client.login(**self.ins_cred)
        self.partial_update_helper("Section78", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.partial_update_helper("Section79", status.HTTP_200_OK)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.partial_update_helper("Section80", status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def delete_section_helper(self, title, status_code):
        section1 = Section(title=title, chapter_id=1)
        section1.save()
        url = reverse(("course:section-delete-section"), kwargs={"pk": section1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status_code)
        try:
            Section.objects.get(id=section1.id)
        except ObjectDoesNotExist:
            self.assertEqual(response.status_code, status_code)

    def test_delete_section(self):
        """
        Ensure we can delete an existing Section object.
        """
        self.client.login(**self.ins_cred)
        self.delete_section_helper("section98", status.HTTP_204_NO_CONTENT)
        self.client.logout()
        self.client.login(**self.ta_cred)
        self.delete_section_helper("section99", status.HTTP_204_NO_CONTENT)
        self.client.logout()
        self.client.login(**self.stu_cred)
        self.delete_section_helper("section100", status.HTTP_403_FORBIDDEN)
        self.client.logout()
