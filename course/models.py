from django.db import models
from django.contrib.postgres.fields import ArrayField

course_types = (
    ('O', "Open"),
    ('M', "Moderated")
)
class Course(models.Model):
    owner_id = models.IntegerField() # We will replace this with foreign key in future
    code = models.CharField(max_length=8,blank=True)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='course_images', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    course_type = models.CharField(max_length=1, choices=course_types, default='O')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    chapters_sequence = ArrayField(models.IntegerField(), null=True, blank=True)
    
