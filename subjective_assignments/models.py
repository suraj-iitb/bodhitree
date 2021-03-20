import os
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from programming_assignments.models import Assignment, AssignmentHistory

def assignment_file_upload_path(instance, filename):
        course = instance.assignment.course
        assignment = instance.assignment
        course_name = course.title.replace(" ", "_")
        assignment_name = assignment.name.replace(" ", "_")
        assignment_path = str(course.id) + '-' + course_name + '/' + str(assignment.id) + '-' + assignment_name
        return os.path.join(assignment_path + '/question_files/' + filename) 

class SubjectiveAssignment(models.Model):
    assignment = models.OneToOneField(Assignment,on_delete=models.CASCADE)  
    team_size = models.IntegerField()
    question_file = models.FileField(upload_to=assignment_file_upload_path)
    helper_file = models.FileField(upload_to=assignment_file_upload_path)
    files_to_be_submitted = ArrayField(models.IntegerField(), null=True, blank=True)

    def __str__(self):
        return self.assignment.name 

class SubjectiveAssignmentTeam(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subjective_assignment = models.ForeignKey(SubjectiveAssignment, on_delete=models.CASCADE)

    def __str__(self):
        return self.subjective_assignment.assignment.name + ':' + self.user.email
class SubjectiveAssignmentHistory(models.Model):
    assignment_history = models.OneToOneField(AssignmentHistory, on_delete=models.CASCADE)  
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    marks_obtained = models.FloatField()
    subjective_assignment_team = models.ForeignKey(SubjectiveAssignmentTeam, on_delete=models.CASCADE)
