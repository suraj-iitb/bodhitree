import os

from django.conf import settings
from django.db import models

from course.models import Chapter, Section
from quiz.models import Quiz
from utils.utils import get_course_folder


marker_type = (
    ("S", "Section Marker"),
    ("Q", "Quiz Marker"),
)


def get_course(instance):
    course = (
        instance.chapter.course if instance.chapter else instance.section.chapter.course
    )
    return course


def video_upload_path(instance, filename):
    return os.path.join(
        get_course_folder(get_course(instance)), "video_files", filename
    )


def video_doc_upload_path(instance, filename):
    return os.path.join(
        get_course_folder(get_course(instance)), "video_doc_files", filename
    )


def in_video_quiz_upload_path(instance, filename):
    return os.path.join(
        get_course_folder(get_course(instance)), "in_video_quiz_files", filename
    )


class Video(models.Model):
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, blank=True, null=True
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, blank=True, null=True
    )
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to=video_upload_path)
    doc_file = models.FileField(upload_to=video_doc_upload_path, blank=True, null=True)
    in_video_quiz_file = models.FileField(
        upload_to=in_video_quiz_upload_path, blank=True, null=True
    )
    video_duration = models.DurationField()
    uploaded_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class VideoHistory(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video_watched_duration = models.DurationField()

    def __str__(self):
        return "{}: {}".format(self.user.email, self.video.title)


class Marker(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    time = models.DurationField()
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class SectionMarker(Marker):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["video", "time"], name="unique_section_marker"
            )
        ]


class QuizMarker(Marker):
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["video", "time"], name="unique_quiz_marker")
        ]
