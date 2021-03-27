# In-built imports
from django.db import models
from django.conf import settings
from datetime import timedelta
import os
# Other imports
from course.models import (Chapter, Section)
from quiz.models import Quiz


def video_upload_path(instance, filename):
    course = instance.chapter.course if instance.chapter else instance.section.chapter.course
    return os.path.join(
        str(course.id) + '.' + course.title, 'video_files', filename)


def video_doc_upload_path(instance, filename):
    course = instance.chapter.course if instance.chapter else instance.section.chapter.course
    return os.path.join(
        str(course.id) + '.' + course.title, 'video_doc_files', filename)


def in_video_quiz_upload_path(instance, filename):
    course = instance.chapter.course if instance.chapter else instance.section.chapter.course
    return os.path.join(
        str(course.id) + '.' + course.title, 'in_video_quiz_files', filename)


class Video(models.Model):
    chapter = models.ForeignKey(Chapter,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True)
    section = models.ForeignKey(Section,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to=video_upload_path)
    doc_file = models.FileField(upload_to=video_doc_upload_path,
                                blank=True,
                                null=True)
    in_video_quiz_file = models.FileField(upload_to=in_video_quiz_upload_path,
                                          blank=True,
                                          null=True)
    video_duration = models.DurationField()
    uploaded_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)


class VideoHistory(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video_watched_duration = models.DurationField(default=timedelta())


marker_type = (
    ('S', 'Section Marker'),
    ('Q', 'Quiz Marker'),
)


class Marker(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    time = models.DurationField()
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SectionMarker(Marker):

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['video', 'time'],
                                    name='unique_section_marker')
        ]


class QuizMarker(Marker):
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['video', 'time'],
                                    name='unique_quiz_marker')
        ]
