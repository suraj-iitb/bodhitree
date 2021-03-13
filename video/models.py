from django.db import models

# Create your models here.
import os
from django.db import models
from course.models import (
    Chapter, Section
)
from django.conf import settings
from datetime import datetime, timedelta

#can be optimized to 1 function later

def video_upload_path(instance, filename):
    course = instance.chapter.course
    return os.path.join(str(course.id) + '-' + course.title + '/videos/' + filename)

def video_doc_upload_path(instance, filename):
    course = instance.chapter.course
    return os.path.join(str(course.id) + '-' + course.title + '/video_doc_files/' + filename)

def in_video_quiz_upload_path(instance, filename):
    course = instance.chapter.course
    return os.path.join(str(course.id) + '-' + course.title + '/in_video_quiz_files/' + filename)

marker_type = (
    ('S', 'Section marker'),
    ('Q', 'Quiz marker'),
)

#section, chapter can be made null and they can be together not null

class Video(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    title = models.CharField(max_length=75)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to=video_upload_path)
    doc_file = models.FileField(upload_to=video_doc_upload_path, null=True, blank=True)
    invideo_quiz_file = models.FileField(upload_to=in_video_quiz_upload_path, null=True, blank=True)
    video_duration = models.DurationField()                                         
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on= models.DateTimeField(auto_now=True)

class VideoHistory(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video_watched_duration = models.DurationField(default = timedelta(seconds=0))                      

class Marker(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    time = models.DurationField()                               
    marker_type = models.CharField(max_length=1, choices=marker_type, default='Q')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on= models.DateTimeField(auto_now=True)

class SectionMarker(models.Model):
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    title = models.CharField(max_length=75)

class QuizMarker(models.Model):
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    title = models.CharField(max_length=75)                                      
    quiz = models.IntegerField()                                                    #link to quiz later

