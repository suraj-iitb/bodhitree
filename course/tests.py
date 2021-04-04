from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from course.models import Course
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
        course = Course(
            owner_id=CourseViewSetTest.user.id, title="Course4", course_type="O"
        )
        course.save()
        user = User.objects.create_user("test2@test.com", "Test@1002")
        user.save()
        data = {"owner": user.id, "title": "Course5", "course_type": "M"}
        url = reverse(("course:course-detail"), kwargs={"pk": course.id})
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_course(self):
        """
        Ensure we can partially update an existing Course object.
        """
        course = Course(
            owner_id=CourseViewSetTest.user.id, title="Course6", course_type="O"
        )
        course.save()
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
        course = Course(
            owner_id=CourseViewSetTest.user.id, title="Course8", course_type="O"
        )
        course.save()
        url = reverse(("course:course-detail"), kwargs={"pk": course.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
