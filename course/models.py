from django.db import models
from django.contrib.postgres.fields import ArrayField

course_types = (
    ('O', 'Open'),
    ('M', 'Moderated')
)

user_roles = (
    ('I', 'Instructor'),
    ('T', 'Teaching Assistant'),
    ('S', 'Student')
)

status_type = (
    ('E', 'Enrolled'),
    ('U', 'Unenrolled'),
    ('P', 'Pending')
)

class Course(models.Model):
    owner = models.IntegerField() # We will replace this with foreign key in future
    code = models.CharField(max_length=8,blank=True)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='course_images', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    course_type = models.CharField(max_length=1, choices=course_types, default='O')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    chapters_sequence = ArrayField(models.IntegerField(), null=True, blank=True)
    
class CourseHistory(models.Model):
    user = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=user_roles, default='S')
    status = models.CharField(max_length=1, choices=status_type, default='P')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

