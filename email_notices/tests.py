from django.core import mail
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from registration.models import User
from utils import credentials

from .models import Email


ins_cred = credentials.TEST_INSTRUCTOR_CREDENTIALS
ta_cred = credentials.TEST_TA_CREDENTIALS
stu_cred = credentials.TEST_STUDENT_CREDENTIALS


class EmailViewSetTest(APITestCase):
    """Test for `EmailViewSet`."""

    fixtures = [
        "users.test.yaml",
        "departments.test.yaml",
        "colleges.test.yaml",
        "courses.test.yaml",
        "coursehistories.test.yaml",
        "email.test.yaml",
    ]

    def login(self, email, password):
        self.client.login(email=email, password=password)

    def logout(self):
        self.client.logout()

    def _create_email_helper(self, sender, from_email, to, subject, status_code):
        """Helper function `test_create_email()`.

        Args:
            sender (int): sender id
            from_email (email): Section id
            to (array): array of reciever emails
            subject (str): Title of the document
            status_code (int): Expected status code of the API call
        """
        course_id = 1

        data = {
            "course": course_id,
            "sender": sender,
            "from_email": from_email,
            "to": to,
            "subject": subject,
        }
        mail.outbox = []
        url = reverse("email_notices:email-create-email")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_201_CREATED:
            response_data = response.data
            self.assertEqual(response_data["course"], data["course"])
            self.assertEqual(response_data["sender"], data["sender"])
            self.assertEqual(response_data["from_email"], data["from_email"])
            self.assertEqual(response_data["to"], data["to"])
            self.assertEqual(response_data["subject"], data["subject"])
            self.assertEqual(len(mail.outbox), 1)

    def test_create_email(self):
        """Test: create an email."""
        # Created by instructor
        self.login(**ins_cred)
        self._create_email_helper(
            1,
            "ins@bodhitree.com",
            ["user1@bodhitree.com", "user2@bodhitree.com"],
            "Subject of current email",
            status.HTTP_201_CREATED,
        )
        self.logout()

        # Created by ta
        self.login(**ta_cred)
        self._create_email_helper(
            2,
            "ta@bodhitree.com",
            ["user1@bodhitree.com", "user2@bodhitree.com"],
            "Subject of current email",
            status.HTTP_201_CREATED,
        )
        self.logout()

        # `HTTP_400_BAD_REQUEST` due to serialization errors
        self.login(**ins_cred)
        self._create_email_helper(
            2,
            "",
            ["user1@bodhitree.com", "user2@bodhitree.com"],
            "Subject of current email",
            status.HTTP_400_BAD_REQUEST,
        )
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._create_email_helper(
            2,
            "ta2@bodhitree.com",
            ["user1@bodhitree.com", "user2@bodhitree.com"],
            "Subject of current email",
            status.HTTP_401_UNAUTHORIZED,
        )

        # `HTTP_403_FORBIDDEN` due to `_is_instructor_or_ta()` method
        self.login(**stu_cred)
        self._create_email_helper(
            3,
            "student@bodhitree.com",
            ["user1@bodhitree.com", "user2@bodhitree.com"],
            "Subject of current email",
            status.HTTP_403_FORBIDDEN,
        )
        self.logout()

    def _list_emails_helper(self, course_id, user_id, status_code):
        """Helper function for `test_list_emails()`.

        Args:
            course_id (int): Course id
            status_code (int): Expected status code of the API call
        """
        if user_id != 3:
            url = reverse(
                "email_notices:email-list-emails-instructor", args=[course_id]
            )
        else:
            url = reverse("email_notices:email-list-emails-student", args=[course_id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code)
        if status_code == status.HTTP_200_OK and user_id == 3:
            user = User.objects.get(id=user_id)
            self.assertEqual(
                len(response.data),
                Email.objects.filter(
                    course_id=course_id, to__contains=[user.email]
                ).count(),
            )
        elif status_code == status.HTTP_200_OK:
            self.assertEqual(
                len(response.data),
                Email.objects.filter(course_id=course_id).count(),
            )

    def test_list_emails(self):
        """Test: list all emails."""
        course_id = 1

        # List by instructor
        self.login(**ins_cred)
        self._list_emails_helper(course_id, 1, status.HTTP_200_OK)
        self.logout()

        # List by ta
        self.login(**ta_cred)
        self._list_emails_helper(course_id, 2, status.HTTP_200_OK)
        self.logout()

        # `HTTP_401_UNAUTHORIZED` due to `IsInstructorOrTA` permission class
        self._list_emails_helper(course_id, 2, status.HTTP_401_UNAUTHORIZED)

        # List by student
        self.login(**stu_cred)
        self._list_emails_helper(course_id, 3, status.HTTP_200_OK)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        # List by student
        course_id = 100
        self.login(**stu_cred)
        self._list_emails_helper(course_id, 3, status.HTTP_404_NOT_FOUND)
        self.logout()

        # `HTTP_404_NOT_FOUND` due to `Course.DoesNotExist` exception
        # List by instructor
        self.login(**ins_cred)
        self._list_emails_helper(course_id, 1, status.HTTP_404_NOT_FOUND)
        self.logout()
