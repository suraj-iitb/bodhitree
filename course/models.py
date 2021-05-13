from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from registration.models import College, Department


COURSE_TYPES = (
    ("O", "Open"),
    ("M", "Moderated"),
)

USER_ROLES = (
    ("I", "Instructor"),
    ("T", "Teaching Assistant"),
    ("S", "Student"),
)

ENROLLMENT_STATUS = (
    ("E", "Enrolled"),
    ("U", "Unenrolled"),
    ("P", "Pending"),
)

CONTENT_TYPES = (
    ("V", "Video"),
    ("D", "Document"),
    ("Q", "Quiz"),
    ("S", "Section"),
)


class Course(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, blank=True)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="course_images", null=True, blank=True)
    is_published = models.BooleanField(default=False)
    course_type = models.CharField(max_length=1, choices=COURSE_TYPES, default="M")
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    chapters_sequence = ArrayField(models.IntegerField(), null=True, blank=True)
    institute = models.ForeignKey(
        College, on_delete=models.CASCADE, null=True, blank=True
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "code", "title"], name="unique_course"
            )
        ]
        ordering = ["-id"]

    def __str__(self):
        return "{}: {}".format(self.code, self.title) if self.code else self.title


class CourseHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=USER_ROLES, default="S")
    status = models.CharField(max_length=1, choices=ENROLLMENT_STATUS, default="P")
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "user"], name="unique_course_history"
            )
        ]
        ordering = ["-id"]

    def __str__(self):
        return "{}: {}".format(self.user, self.course)


class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    content_sequence = ArrayField(
        ArrayField(models.IntegerField(), size=2), null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "title"], name="unique_chapter")
        ]
        ordering = ["-id"]

    def __str__(self):
        return self.title


class Section(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    content_sequence = ArrayField(
        ArrayField(models.IntegerField(), size=2), null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["chapter", "title"], name="unique_section")
        ]

    def __str__(self):
        return self.title


class Notification(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    url = models.URLField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["url"], name="unique_notification")
        ]

    def __str__(self):
        return self.title


class Schedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    content_list = ArrayField(
        ArrayField(models.IntegerField(), size=2), null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "start_date", "end_date", "content_list"],
                name="unique_schedule",
            )
        ]

    def __str__(self):
        return "{}: From:- {} To:- {}".format(
            self.course, self.start_date, self.end_date
        )


class Page(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "title"], name="unique_page")
        ]

    def __str__(self):
        return self.title


class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body
