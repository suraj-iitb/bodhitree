from django.db import models
from course.models import Course
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class Email(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='+')
    from_email = models.EmailField(max_length=254)  #link to profile?
    to_email_list = ArrayField(models.EmailField())
    reply_to = models.EmailField(max_length=254, blank=True)  #check null
    cc_list = ArrayField(models.EmailField(), blank=True)
    subject = models.TextField()
    body = models.TextField(blank=True)
    sent_on = models.DateTimeField(auto_now_add=True)
