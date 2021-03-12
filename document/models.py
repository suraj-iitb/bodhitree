from django.db import models
from course.models import (
    Chapter, Section
)

def document_upload_path(instance, filename):
    course = instance.chapter.course
    return os.path.join(course.id + '-' + course.title + '/documents')
        
class Document(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    title = models.CharField(max_length=75)
    description = models.TextField(blank=True)
    doc_file = models.FileField(upload_to=document_upload_path)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on= models.DateTimeField(auto_now=True)
