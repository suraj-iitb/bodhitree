from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from course.models import Chapter, Course, CourseHistory, Page
from registration.models import User


class CourseViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.user = User.objects.create_user("test1@test.com", "Test@1001")
        cls.user.save()
        cls.course1 = Course(owner_id=cls.user.id, title="Course1", course_type="O")
        cls.course1.save()
        cls.course2 = Course(owner_id=cls.user.id, title="Course2", course_type="M")
        cls.course2.save()

    def test_get_courses(self):
        """
        Ensure we can get all Course objects.
        """
        url = reverse("course:course-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_course(self):
        """
        Ensure we can get one Course object.
        """
        url = reverse(
            "course:course-detail", kwargs={"pk": CourseViewSetTest.course1.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_course(self):
        """
        Ensure we can create a new Course object.
        """
        self.client.login(email="test1@test.com", password="Test@1001")
        data = {
            "owner": CourseViewSetTest.user.id,
            "title": "Course3",
            "course_type": "O",
        }
        url = reverse("course:course-list")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_course(self):
        """
        Ensure we can update an existing Course object.
        """
        self.client.login(email="test1@test.com", password="Test@1001")
        course = Course(
            owner_id=CourseViewSetTest.user.id, title="Course4", course_type="O"
        )
        course.save()
        course_history = CourseHistory(
            user_id=CourseViewSetTest.user.id, course_id=course.id, role="I", status="E"
        )
        course_history.save()
        data = {
            "owner": CourseViewSetTest.user.id,
            "title": "Course5",
            "course_type": "M",
        }
        url = reverse(("course:course-detail"), kwargs={"pk": course.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_course(self):
        """
        Ensure we can partially update an existing Course object.
        """
        self.client.login(email="test1@test.com", password="Test@1001")
        course = Course(
            owner_id=CourseViewSetTest.user.id, title="Course6", course_type="O"
        )
        course.save()
        course_history = CourseHistory(
            user_id=CourseViewSetTest.user.id, course_id=course.id, role="I", status="E"
        )
        course_history.save()
        data = {
            "title": "Course7",
        }
        url = reverse(("course:course-detail"), kwargs={"pk": course.id})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_course(self):
        """
        Ensure we can delete an existing Course object.
        """
        self.client.login(email="test1@test.com", password="Test@1001")
        course = Course(
            owner_id=CourseViewSetTest.user.id, title="Course8", course_type="O"
        )
        course.save()
        course_history = CourseHistory(
            user_id=CourseViewSetTest.user.id, course_id=course.id, role="I", status="E"
        )
        course_history.save()
        url = reverse(("course:course-detail"), kwargs={"pk": course.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


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
    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.user = User.objects.create_user("test1@test.com", "Test@1001")
        cls.user.save()
        cls.course1 = Course(owner_id=cls.user.id, title="Course1", course_type="O")
        cls.course1.save()
        cls.chapter1 = Chapter(title="Chapter1", course_id=cls.course1.id)
        cls.chapter1.save()

    def test_get_chapters(self):
        """
        Ensure we can get all Chapter objects.
        """
        self.client.login(email="test1@test.com", password="Test@1001")
        url = reverse("course:chapter-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_chapter(self):
        """
        Ensure we can get one chapter object.
        """
        self.client.login(email="test1@test.com", password="Test@1001")
        url = reverse(
            "course:chapter-detail",
            kwargs={"pk": ChapterViewSetTest.chapter1.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_chapter(self):
        """
        Ensure we can create a new Chapter object.
        """
        user = User.objects.create_user("test2@test.com", "Test@1002")
        user.save()
        course1 = Course(owner_id=user.id, title="Course2", course_type="O")
        course1.save()
        self.client.login(email="test2@test.com", password="Test@1002")
        data = {
            "title": "Chapter1",
            "course": course1.id,
        }
        url = reverse("course:chapter-list")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_chapters(self):
        """
        Ensure we can update an existing Chapter object.
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
        chapter1 = Chapter(title="Chapter1", course_id=course1.id)
        chapter1.save()
        data = {
            "title": "Chapter2",
            "course": course2.id,
        }
        url = reverse(("course:chapter-detail"), kwargs={"pk": chapter1.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_chapter(self):
        """
        Ensure we can partially update an existing Chapter object.
        """
        user = User.objects.create_user("test5@test.com", "Test@1005")
        user.save()
        course1 = Course(owner_id=user.id, title="Course1", course_type="O")
        course1.save()
        self.client.login(email="test5@test.com", password="Test@1005")
        chapter1 = Chapter(title="Chapter1", course_id=course1.id)
        chapter1.save()
        data = {"title": "Chapter2"}
        url = reverse(("course:chapter-detail"), kwargs={"pk": chapter1.id})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_coursehistory(self):
        """
        Ensure we can delete an existing Chapter object.
        """
        user = User.objects.create_user("test6@test.com", "Test@1006")
        user.save()
        course1 = Course(owner_id=user.id, title="Course1", course_type="O")
        course1.save()
        self.client.login(email="test6@test.com", password="Test@1006")
        chapter1 = Chapter(title="Chapter1", course_id=course1.id)
        chapter1.save()
        url = reverse(("course:chapter-detail"), kwargs={"pk": chapter1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PageViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase.
        """
        cls.user = User.objects.create_user("test1@test.com", "Test@1001")
        cls.user.save()
        cls.course = Course(owner_id=cls.user.id, title="Course", course_type="O")
        cls.course.save()
        cls.course_history = CourseHistory(user=cls.user, course=cls.course)
        cls.course_history.save()
        cls.page = Page(course=cls.course, title="Page 3")
        cls.page.save()

    def test_add_page(self):
        self.client.login(email="test1@test.com", password="Test@1001")
        url = reverse("course:page-add-page", args=[PageViewSetTest.course.id])
        data = {
            "course": PageViewSetTest.course.id,
            "title": "Page1",
            "description": "Page 1 description",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_page_retrieve(self):
        self.client.login(email="test1@test.com", password="Test@1001")
        url = reverse(
            ("course:page-list-pages"), kwargs={"pk": PageViewSetTest.course.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_pages(self):
        self.client.login(email="test1@test.com", password="Test@1001")
        url = reverse("course:page-list-pages", args=[PageViewSetTest.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_page(self):
        self.client.login(email="test1@test.com", password="Test@1001")
        page = Page(course=PageViewSetTest.course, title="Page 6")
        page.save()
        data = {
            "course": PageViewSetTest.course.id,
            "title": "Page 7",
            "description": "Description of page",
        }
        url = reverse("course:page-update-page", kwargs={"pk": page.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_page(self):
        self.client.login(email="test1@test.com", password="Test@1001")
        page = Page(course=PageViewSetTest.course, title="Page 4")
        page.save()
        data = {"title": "Page 5"}
        url = reverse(("course:page-partial-update-page"), kwargs={"pk": page.id})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_page_destroy(self):
        self.client.login(email="test1@test.com", password="Test@1001")
        page = Page(course=PageViewSetTest.course, title="Page 2")
        page.save()
        url = reverse(("course:page-destroy-page"), kwargs={"pk": page.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
