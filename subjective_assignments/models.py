from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from programming_assignments.models import Assignment, AssignmentHistory
from utils.utils import get_assignment_file_upload_path


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
    assignment = models.OneToOneField(Assignment, on_delete=models.CASCADE)
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assignment__course", "assignment__name"],
                name="unique_subjective_assignment",
            )
        ]

    def __str__(self):
        return self.assignment.name


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
    assignment_history = models.OneToOneField(
        AssignmentHistory, on_delete=models.CASCADE
    )
    submitted_file = ArrayField(
        models.FileField(upload_to=subjective_assignment_file_upload_path),
        blank=True,
        null=True,
    )
    marks_obtained = models.FloatField(default=0)
    subjective_assignment_team = models.ForeignKey(
        SubjectiveAssignmentTeam, on_delete=models.CASCADE
    )

    def __str__(self):
        assign_history = self.assignment_history
        return "{}: {}".format(
            assign_history.user.email, assign_history.assignment.name
        )
