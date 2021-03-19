from django.db import models
from django.conf import settings
from course.models import Course, USER_ROLES, CONTENT_TYPES

class DiscussionForum(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    anonymous_to_instructor = models.BooleanField(default=False)
    send_email_to_all = models.BooleanField(default=False)

    def __str__(self):
        return self.course.title + ': Discussion Forum'

class Content(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    author_category = models.CharField(max_length=1, choices=USER_ROLES, default='S')
    description = models.TextField()
    pinned = models.BooleanField(default=False)
    anonymous_to_student = models.BooleanField(default=False)
    upvote = models.IntegerField(default=0)
    downvote = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description[0:20]

class Tag(models.Model):
    discussion_forum = models.ForeignKey(DiscussionForum, on_delete=models.CASCADE)
    content_id = models.IntegerField()      # refers to multimedia content id. 
    content_type = models.CharField(max_length=1, choices=CONTENT_TYPES)
    tag_name = models.TextField()           # refers to content title

    def __str__(self):
        return self.tag_name[0:20]


class DiscussionThread(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE)
    discussion_forum = models.ForeignKey(DiscussionForum, on_delete=models.CASCADE)
    mark_as_important = models.BooleanField(default=False)
    tag = models.ManyToManyField(Tag)

    def __str__(self):
        return self.description.description[0:20]

class DiscussionComment(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE)
    discussion_thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE)

    def __str__(self):
        return self.description.description[0:20]

class DiscussionReply(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE)
    discussion_comment = models.ForeignKey(DiscussionComment, on_delete=models.CASCADE)

    def __str__(self):
        return self.description.description[0:20]


