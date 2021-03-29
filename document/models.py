import os

from django.conf import settings
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
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    doc_file = models.FileField(upload_to=document_upload_path)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
