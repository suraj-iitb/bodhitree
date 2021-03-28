from django.conf import settings
from django.db import models

from course.models import CONTENT_TYPES, USER_ROLES, Course


class DiscussionForum(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    anonymous_to_instructor = models.BooleanField(default=True)
    send_email_to_all = models.BooleanField(default=False)

    def __str__(self):
        return self.course.title + ": Discussion Forum"


class Content(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    author_category = models.CharField(max_length=1, choices=USER_ROLES)
    description = models.TextField()
    pinned = models.BooleanField(default=False)
    anonymous_to_student = models.BooleanField(default=False)
    upvote = models.IntegerField(default=0)
    downvote = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.description[0:20] + "..."


class Tag(models.Model):
    discussion_forum = models.ForeignKey(DiscussionForum, on_delete=models.CASCADE)
    content_id = models.IntegerField()  # refers to multimedia content id
    content_type = models.CharField(max_length=1, choices=CONTENT_TYPES)
    tag_name = models.TextField()  # refers to content title

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_id", "content_type"], name="unique_tag"
            )
        ]

    def __str__(self):
        return self.tag_name[0:20] + "..."


class DiscussionThread(Content):
    discussion_forum = models.ForeignKey(DiscussionForum, on_delete=models.CASCADE)
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    mark_as_important = models.BooleanField(default=False)
    tag = models.ManyToManyField(Tag, blank=True)


class DiscussionComment(Content):
    discussion_thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE)


class DiscussionReply(Content):
    discussion_comment = models.ForeignKey(DiscussionComment, on_delete=models.CASCADE)
