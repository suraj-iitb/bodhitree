from django.db import models
from django.conf import settings
from course.models import Course

user_roles = (
    ('I', 'Instructor'),
    ('T', 'Teaching Assistant'),
    ('S', 'Student')
)

class DiscussionForum(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    anonymous_to_instructor = models.BooleanField(default=False)
    send_email_to_all = models.BooleanField(default=False)

class Content(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    author_category = models.CharField(max_length=1, choices=user_roles, default='S')
    content = models.TextField()
    pinned = models.BooleanField(default=False)
    anonymous_to_student = models.BooleanField(default=False)
    upvote = models.IntegerField(default=0)
    downvote = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

class DiscussionThread(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    discussion_forum = models.ForeignKey(DiscussionForum, on_delete=models.CASCADE)
    mark_as_important = models.BooleanField(default=False)

class DiscussionComment(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    discussion_thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE)

class DiscussionReply(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    discussion_comment = models.ForeignKey(DiscussionComment, on_delete=models.CASCADE)

class Tag(models.Model):
    discussion_forum = models.ForeignKey(DiscussionForum, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    tag_name = models.TextField()   #check

class DiscussionThreadTag(models.Model):
    discussion_thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

