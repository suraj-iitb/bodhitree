from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

COURSE_TYPES = (
    ('O', 'Open'),
    ('M', 'Moderated')
)

USER_ROLES = (
    ('I', 'Instructor'),
    ('T', 'Teaching Assistant'),
    ('S', 'Student')
)

STATUS_TYPES = (
    ('E', 'Enrolled'),
    ('U', 'Unenrolled'),
    ('P', 'Pending')
)

CONTENT_TYPES = (
    ('V', 'Video'),
    ('D', 'Document'),
    ('Q', 'Quiz'),
    ('S', 'Section')
)

class Course(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=8,blank=True)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='course_images', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    course_type = models.CharField(max_length=1, choices=COURSE_TYPES, default='O')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    chapters_sequence = ArrayField(models.IntegerField(), null=True, blank=True)

    def __str__(self):
        return self.title
    
class CourseHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=USER_ROLES, default='S')
    status = models.CharField(max_length=1, choices=STATUS_TYPES, default='P')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True)
    content_sequence = ArrayField(models.IntegerField(), null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Section(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    name = models.CharField(max_length=75)
    description = models.TextField(blank=True)
    content_sequence = ArrayField(models.IntegerField(), null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Notification(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    url = models.URLField()
    created_on = models.DateTimeField(auto_now_add=True)

class Schedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    content_list = ArrayField(models.IntegerField(), null=True, blank=True)

class Page(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

