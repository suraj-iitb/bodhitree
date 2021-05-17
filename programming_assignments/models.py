from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models

from course.models import Course
from utils.utils import get_assignment_file_upload_path


def programming_assignment_file_upload_path(instance, filename):
    if type(instance) in [SimpleProgrammingAssignment, AdvancedProgrammingAssignment]:
        assignment = instance
        return get_assignment_file_upload_path(
            assignment, "programming", "question_files", filename
        )
    elif type(instance) is SimpleProgrammingAssignmentHistory:
        assignment = instance.assignment_history.assignment
        return get_assignment_file_upload_path(
            assignment, "programming", "submission_files", filename
        )
    elif type(instance) is Testcase:
        assignment = instance.assignment
        return get_assignment_file_upload_path(
            assignment, "programming", "testcase_files", filename
        )


PROG_LANG = (
    ("C", "C"),
    ("C++", "C++"),
    ("Java", "Java"),
    ("Python", "Python"),
    ("Others", "Others"),
)

TA_POLICY = (
    ("A", "Automated"),
    ("P", "Previous"),
    ("N", "New"),
)

SECTION_TYPE = (
    ("V", "Visible"),
    ("H", "Hidden"),
)


class TAAllocation(models.Model):
    mapping = models.JSONField()


class SimpleProgrammingAssignment(models.Model):
    programming_language = models.CharField(max_length=10, choices=PROG_LANG)
    document = models.FileField(
        upload_to=programming_assignment_file_upload_path, blank=True, null=True
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    extended_date = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SimpleProgrammingAssignmentHistory(models.Model):
    simple_prog_assignment = models.ForeignKey(
        SimpleProgrammingAssignment, on_delete=models.CASCADE
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    instructor_feedback = models.TextField(blank=True)
    file_submitted = models.FileField(upload_to=programming_assignment_file_upload_path)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.user.email, self.simple_prog_assignment.name)


class AdvancedProgrammingAssignment(SimpleProgrammingAssignment):
    helper_code = models.FileField(
        upload_to=programming_assignment_file_upload_path, null=True, blank=True
    )
    instructor_solution_code = models.FileField(
        upload_to=programming_assignment_file_upload_path, null=True, blank=True
    )
    files_to_be_submitted = ArrayField(
        models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH), blank=True
    )
    ta_allocation_file = models.FileField(
        upload_to=programming_assignment_file_upload_path, null=True, blank=True
    )
    ta_allocation = models.ForeignKey(
        TAAllocation, on_delete=models.CASCADE, blank=True, null=True
    )
    policy = models.CharField(max_length=1, choices=TA_POLICY, default="A")
    execution_time_calculate = models.BooleanField(default=False)
    ignore_whitespaces_in_output = models.BooleanField(default=False)
    indentation_percentage_calculate = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class AdvancedProgrammingAssignmentHistory(SimpleProgrammingAssignmentHistory):
    execution_time = models.FloatField(null=True, blank=True)
    indentation_percentage = models.FloatField(null=True, blank=True)

    def __str__(self):
        assign_history = self.simple_prog_assignment
        return "{}: {}".format(self.user.email, assign_history.name)


class AssignmentSection(models.Model):
    assignment = models.ForeignKey(
        SimpleProgrammingAssignment, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    section_type = models.CharField(max_length=1, choices=SECTION_TYPE, default="V")
    compiler_command = models.CharField(
        max_length=settings.MAX_CHARFIELD_LENGTH, blank=True
    )
    execution_command = models.CharField(
        max_length=settings.MAX_CHARFIELD_LENGTH, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Testcase(models.Model):
    assignment = models.ForeignKey(
        SimpleProgrammingAssignment, on_delete=models.CASCADE, blank=True, null=True
    )
    assignment_section = models.ForeignKey(
        AssignmentSection, on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    cmd_line_args = ArrayField(
        models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH),
        null=True,
        blank=True,
    )
    marks = models.FloatField(default=0)
    input_file = models.FileField(
        upload_to=programming_assignment_file_upload_path, null=True, blank=True
    )
    output_file = models.FileField(
        upload_to=programming_assignment_file_upload_path, null=True, blank=True
    )
    is_published = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(assignment__isnull=False)
                | models.Q(assignment_section__isnull=False),
                name="both_not_null_in_testcase",
            )
        ]

    def clean(self):
        super().clean()
        if self.assignment is None and self.assignment_section is None:
            raise ValidationError(
                "Both Assignment and Assignment Section can't be Empty"
            )

    def __str__(self):
        return self.name


class TestcaseHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    testcase = models.ForeignKey(Testcase, on_delete=models.CASCADE)
    marks_obtained = models.FloatField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.user.email, self.testcase.name)


class Exam(models.Model):
    assignment = models.OneToOneField(
        SimpleProgrammingAssignment, on_delete=models.CASCADE
    )
    duration = models.DurationField()
    late_duration = models.DurationField()
    allowed_ip_range = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} Exam".format(self.assignment.name)


class ExamHistory(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = ArrayField(
        models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH), blank=True
    )
    is_paused = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    start_time = models.DateTimeField()
    remaining_time = models.DurationField()
    additional_time = ArrayField(models.FloatField(), null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {} Exam History".format(self.user.email, self.exam.assignment.name)
