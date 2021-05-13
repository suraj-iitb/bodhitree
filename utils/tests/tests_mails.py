from django.core import mail
from django.test import TestCase

from utils.mails import send_mail


class EmailTest(TestCase):
    """Email Test"""

    def test_send_email(self):
        """Test `send_email()`"""
        send_mail(
            "Subject here",
            "Here is the message.",
            "from@example.com",
            ["to1@example.com", "to2@example.com"],
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Subject here")
        self.assertEqual(mail.outbox[0].body, "Here is the message.")
        self.assertEqual(mail.outbox[0].from_email, "from@example.com")
        self.assertEqual(mail.outbox[0].to, ["to1@example.com", "to2@example.com"])
