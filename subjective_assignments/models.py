import os

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from programming_assignments.models import Assignment, AssignmentHistory
from utils.utils import get_assignment_folder, get_course_folder


def get_file_full_path(assignment, sub_folder_name, filename):
    course_folder = get_course_folder(assignment.course)
    assignment_folder = get_assignment_folder(assignment, "subjective")
    return os.path.join(course_folder, assignment_folder, sub_folder_name, filename)


def assignment_file_upload_path(instance, filename):
    assignment = instance.assignment
    return get_file_full_path(assignment, "question_files", filename)


class SubjectiveAssignment(Assignment):
    team_size = models.IntegerField()
    question_file = models.FileField(upload_to=assignment_file_upload_path)
    helper_file = models.FileField(upload_to=assignment_file_upload_path)
    files_to_be_submitted = ArrayField(
        models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class SubjectiveAssignmentTeam(models.Model):
    user_ids = ArrayField(models.IntegerField())
    subjective_assignment = models.ForeignKey(
        SubjectiveAssignment, on_delete=models.CASCADE
    )

    def __str__(self):
        return "{}: {}".format(self.user_ids, self.subjective_assignment.name)


class SubjectiveAssignmentHistory(AssignmentHistory):
    marks_obtained = models.FloatField(default=0)
    subjective_assignment_team = models.ForeignKey(
        SubjectiveAssignmentTeam, on_delete=models.CASCADE
    )
