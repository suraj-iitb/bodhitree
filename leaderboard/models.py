from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from course.models import Course


class MarksHeader(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sheet_name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    header_list = ArrayField(models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH))
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "sheet_name"], name="unique_sheet"
            )
        ]

    def __str__(self):
        return self.sheet_name


class MarksBody(models.Model):
    marks_header = models.ForeignKey(MarksHeader, on_delete=models.CASCADE)
    student_marks = ArrayField(
        models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} Body".format(self.marks_header.sheet_name)
