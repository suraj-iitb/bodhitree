from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from course.models import Course, CourseHistory, Page
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


# class ChapterViewSetTest(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         """
#         Set up data for the whole TestCase.
#         """
#         cls.user = User.objects.create_user("test1@test.com", "Test@1001")
#         cls.user.save()
#         cls.course1 = Course(owner_id=cls.user.id, title="Course1", course_type="O")
#         cls.course1.save()
#         cls.chapter1 = Chapter(title="Chapter1", course_id=cls.course1.id)
#         cls.chapter1.save()

#     def test_get_chapters(self):
#         """
#         Ensure we can get all Chapter objects.
#         """
#         self.client.login(email="test1@test.com", password="Test@1001")
#         url = reverse("course:chapter-list")
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_get_chapter(self):
#         """
#         Ensure we can get one chapter object.
#         """
#         self.client.login(email="test1@test.com", password="Test@1001")
#         url = reverse(
#             "course:chapter-detail",
#             kwargs={"pk": ChapterViewSetTest.chapter1.id},
#         )
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_create_chapter(self):
#         """
#         Ensure we can create a new Chapter object.
#         """
#         user = User.objects.create_user("test2@test.com", "Test@1002")
#         user.save()
#         course1 = Course(owner_id=user.id, title="Course2", course_type="O")
#         course1.save()
#         self.client.login(email="test2@test.com", password="Test@1002")
#         data = {
#             "title": "Chapter1",
#             "course": course1.id,
#         }
#         url = reverse("course:chapter-list")
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_update_chapters(self):
#         """
#         Ensure we can update an existing Chapter object.
#         """
#         user = User.objects.create_user("test3@test.com", "Test@1003")
#         user.save()
#         course1 = Course(owner_id=user.id, title="Course1", course_type="O")
#         course1.save()
#         user2 = User.objects.create_user("test4@test.com", "Test@1004")
#         user2.save()
#         course2 = Course(owner_id=user2.id, title="Course1", course_type="O")
#         course2.save()
#         self.client.login(email="test3@test.com", password="Test@1003")
#         chapter1 = Chapter(title="Chapter1", course_id=course1.id)
#         chapter1.save()
#         data = {
#             "title": "Chapter2",
#             "course": course2.id,
#         }
#         url = reverse(("course:chapter-detail"), kwargs={"pk": chapter1.id})
#         response = self.client.put(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_partial_update_chapter(self):
#         """
#         Ensure we can partially update an existing Chapter object.
#         """
#         user = User.objects.create_user("test5@test.com", "Test@1005")
#         user.save()
#         course1 = Course(owner_id=user.id, title="Course1", course_type="O")
#         course1.save()
#         self.client.login(email="test5@test.com", password="Test@1005")
#         chapter1 = Chapter(title="Chapter1", course_id=course1.id)
#         chapter1.save()
#         data = {"title": "Chapter2"}
#         url = reverse(("course:chapter-detail"), kwargs={"pk": chapter1.id})
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_delete_coursehistory(self):
#         """
#         Ensure we can delete an existing Chapter object.
#         """
#         user = User.objects.create_user("test6@test.com", "Test@1006")
#         user.save()
#         course1 = Course(owner_id=user.id, title="Course1", course_type="O")
#         course1.save()
#         self.client.login(email="test6@test.com", password="Test@1006")
#         chapter1 = Chapter(title="Chapter1", course_id=course1.id)
#         chapter1.save()
#         url = reverse(("course:chapter-detail"), kwargs={"pk": chapter1.id})
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


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
