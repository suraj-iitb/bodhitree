from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models

from course.models import Course
from utils.utils import get_assignment_file_upload_path


User = get_user_model()


def subjective_assignment_file_upload_path(instance, filename):
    if type(instance) is SubjectiveAssignment:
        assignment = instance.assignment
        return get_assignment_file_upload_path(
            assignment, "subjective", "question_files", filename
        )
    elif type(instance) is SubjectiveAssignmentHistory:
        assignment = instance.assignment_history.assignment
        return get_assignment_file_upload_path(
            assignment, "subjective", "submission_files", filename
        )


class SubjectiveAssignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    extended_date = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    team_size = models.IntegerField(default=1)
    question_file = models.FileField(upload_to=subjective_assignment_file_upload_path)
    helper_file = models.FileField(
        upload_to=subjective_assignment_file_upload_path, blank=True, null=True
    )
    files_to_be_submitted = ArrayField(
        models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH),
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class SubjectiveAssignmentTeam(models.Model):
    user_ids = ArrayField(models.IntegerField())
    subjective_assignment = models.ForeignKey(
        SubjectiveAssignment, on_delete=models.CASCADE
    )

    def __str__(self):
        return "{}: {}".format(
            self.user_ids, self.subjective_assignment.assignment.name
        )


class SubjectiveAssignmentHistory(models.Model):
    assignment = models.ForeignKey(SubjectiveAssignment, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    instructor_feedback = models.TextField(blank=True)
    submitted_file = ArrayField(
        models.FileField(upload_to=subjective_assignment_file_upload_path),
        blank=True,
        null=True,
    )
    marks_obtained = models.FloatField(default=0)
    subjective_assignment_team = models.ForeignKey(
        SubjectiveAssignmentTeam, on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.user.email, self.assignment.name)
