from rest_framework import serializers

from .models import (
    DiscussionComment,
    DiscussionForum,
    DiscussionReply,
    DiscussionThread,
    Tag,
)


class DiscussionForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionForum
        fields = ["anonymous_to_instructor", "send_email_to_all"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class DiscussionThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionThread
        fields = "__all__"


class DiscussionCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionComment
        fields = "__all__"


class DiscussionReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionReply
        fields = "__all__"
