from django.conf import settings
from django.db import models

from course.models import Course


CRIB_STATUS = (
    ("R", "Resolved"),
    ("U", "Unresolved"),
)


class Crib(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crib_creator"
    )
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=1, choices=CRIB_STATUS, default="U")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.title


class CribReply(models.Model):
    crib = models.ForeignKey(Crib, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.description
