import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from course.models import Chapter, Section
from utils.utils import get_course_folder


def document_upload_path(instance, filename):
    course = (
        instance.chapter.course if instance.chapter else instance.section.chapter.course
    )
    course_folder = get_course_folder(course)
    return os.path.join(course_folder, "document_files", filename)


class Document(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, blank=True, null=True
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, blank=True, null=True
    )
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    doc_file = models.FileField(upload_to=document_upload_path)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(chapter__isnull=False) | models.Q(section__isnull=False),
                name="both_not_null_in_doc",
            )
        ]

    def clean(self):
        super().clean()
        if self.chapter is None and self.section is None:
            raise ValidationError("Both Chapter and Section can't be Empty")

    def __str__(self):
        return self.title
