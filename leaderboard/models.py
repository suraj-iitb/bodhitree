from django.contrib.postgres.fields import ArrayField
from django.db import models

from course.models import Course


class GradesHeader(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sheet_name = models.TextField()
    header_list = ArrayField(models.TextField(), null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sheet_name


class GradesBody(models.Model):
    grades_header = models.ForeignKey(GradesHeader, on_delete=models.CASCADE)
    student_marks = ArrayField(models.IntegerField(), null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
