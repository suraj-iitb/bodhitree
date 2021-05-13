from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from course.models import Course


class Email(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender"
    )
    from_email = models.EmailField()
    to_email_list = ArrayField(models.EmailField())
    reply_to = models.EmailField(blank=True)
    cc_list = ArrayField(models.EmailField(), blank=True, null=True)
    subject = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    body = models.TextField(blank=True)
    sent_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
