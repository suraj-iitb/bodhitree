import os

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from course.models import Course


# can think of better organization of these files
# save it assignment wise
# try to minimize code in below function


def assignment_history_file_upload_path(instance, filename):
    print(instance)
    if type(instance) is SimpleProgrammingAssignment or type(instance) is Testcase:
        course = instance.assignment.course
        assignment = instance.assignment
        course_name = course.title.replace(" ", "_")
        assignment_name = assignment.name.replace(" ", "_")
        assignment_path = (
            str(course.id)
            + "-"
            + course_name
            + "/"
            + str(assignment.id)
            + "-"
            + assignment_name
        )
        return os.path.join(assignment_path + "/question_files/" + filename)
    elif type(instance) is AdvancedProgrammingAssignment:
        course = instance.simple_programming_assignment.assignment.course
        assignment = instance.simple_programming_assignment.assignment
        course_name = course.title.replace(" ", "_")
        assignment_name = assignment.name.replace(" ", "_")
        assignment_path = (
            str(course.id)
            + "-"
            + course_name
            + "/"
            + str(assignment.id)
            + "-"
            + assignment_name
        )
        return os.path.join(assignment_path + "/question_files/" + filename)
    elif type(instance) is SimpleProgrammingAssignmentHistory:
        course = instance.assignment_history.assignment.course
        assignment = instance.assignment_history.assignment
        course_name = course.title.replace(" ", "_")
        assignment_name = assignment.name.replace(" ", "_")
        assignment_path = (
            str(course.id)
            + "-"
            + course_name
            + "/"
            + str(assignment.id)
            + "-"
            + assignment_name
        )
        return os.path.join(assignment_path + "/submission_files/" + filename)


prog_lang = (
    ("C", "C"),
    ("C++", "C++"),
    ("Java", "Java"),
    ("Python", "Python"),
    ("Others", "Others"),
)

policy = (("A", "Automated"), ("P", "Previous"), ("N", "New"))

section_type = (("V", "Visible"), ("H", "Hidden"))


class TAAllocation(models.Model):
    mapping = models.JSONField()


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    extended_date = models.DateField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AssignmentHistory(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    instructor_feedback = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


class SimpleProgrammingAssignment(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    programming_language = models.CharField(
        max_length=10, choices=prog_lang, default="C"
    )
    document = models.FileField(upload_to=assignment_history_file_upload_path)

    def __str__(self):
        return self.assignment.name


class SimpleProgrammingAssignmentHistory(models.Model):
    assignment_history = models.ForeignKey(AssignmentHistory, on_delete=models.CASCADE)
    file_submitted = models.FileField(upload_to=assignment_history_file_upload_path)

    def __str__(self):
        return self.assignment_history.assignment.name


class SimpleProgrammingAssignmentHistoryVersion(models.Model):
    simple_programming_assignment_history = models.ForeignKey(
        SimpleProgrammingAssignmentHistory, on_delete=models.CASCADE
    )


class AdvancedProgrammingAssignment(models.Model):
    simple_programming_assignment = models.ForeignKey(
        SimpleProgrammingAssignment, on_delete=models.CASCADE
    )
    helper_code = models.FileField(upload_to=assignment_history_file_upload_path)
    instruction_solution_code = models.FileField(
        upload_to=assignment_history_file_upload_path
    )
    files_to_be_submitted = ArrayField(
        models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH),
        null=True,
        blank=True,
    )
    ta_allocation_file = models.FileField(
        upload_to=assignment_history_file_upload_path, null=True, blank=True
    )
    ta_allocation = models.ForeignKey(
        TAAllocation, on_delete=models.CASCADE, blank=True, null=True
    )
    policy = models.CharField(max_length=10, choices=policy, default="A")
    execution_time = models.BooleanField(default=False)
    ignore_whitespaces = models.BooleanField(default=False)
    indentation_percentage = models.BooleanField(default=False)


class AdvancedProgrammingAssignmentHistory(models.Model):
    simple_programming_assignment = models.ForeignKey(
        SimpleProgrammingAssignment, on_delete=models.CASCADE
    )
    execution_time = models.FloatField(null=True, blank=True)
    indentation = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.simple_programming_assignment.assignment.name


class AdvancedProgrammingAssignmentHistoryVersion(models.Model):
    advanced_programming_assignment_history = models.ForeignKey(
        AdvancedProgrammingAssignmentHistory, on_delete=models.CASCADE
    )


class AssignmentSection(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField(blank=True)
    section_type = models.CharField(max_length=1, choices=section_type, default="V")
    compiler_command = models.CharField(
        max_length=settings.MAX_CHARFIELD_LENGTH, null=True, blank=True
    )
    execution_command = models.CharField(
        max_length=settings.MAX_CHARFIELD_LENGTH, null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Testcase(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    assignment_section = models.ForeignKey(AssignmentSection, on_delete=models.CASCADE)
    name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    cmd_line_args = ArrayField(
        models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH),
        null=True,
        blank=True,
    )
    marks = models.FloatField(default=0)
    input_file = models.FileField(
        upload_to=assignment_history_file_upload_path, null=True, blank=True
    )
    output_file = models.FileField(
        upload_to=assignment_history_file_upload_path, null=True, blank=True
    )
    is_published = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TestcaseHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    marks_obtained = models.FloatField(default=0)


class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    duration = models.DurationField()
    late_duration = models.DurationField()
    allowed_ip_range = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    def __str__(self):
        return self.course.title + ":" + self.assignment.name


class ExamHistory(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    ip_address = ArrayField(
        models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH),
        null=True,
        blank=True,
    )
    is_paused = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    start_time = models.DateTimeField()
    remaining_time = models.DurationField()
    additional_time = ArrayField(models.FloatField(), null=True, blank=True)
