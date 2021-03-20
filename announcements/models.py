from django.db import models
from course.models import Course

class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
