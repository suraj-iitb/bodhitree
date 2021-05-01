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
    tags = TagSerializer()

    class Meta:
        model = DiscussionThread
        fields = "__all__"

    def create(self, validated_data):
        tag_data = validated_data.pop("tags")
        discussion_thread = DiscussionThread.objects.create(**validated_data)
        Tag.objects.create(discussion_forum=discussion_thread.discussion_forum.id, **tag_data)
        return discussion_thread

    def update(self, instance, validated_data):
        tag_data = validated_data.pop("tags", {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        discussion_thread = get_object_or_404(DiscussionThread, discussion_forum=instance.discussion_forum.id)
        if tag_data:
            for attr, value in tag_data.items():
                setattr(discussion_thread, attr, value)
            discussion_thread.save()
        return instance


class DiscussionCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionComment
        fields = "__all__"


class DiscussionReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionReply
        fields = "__all__"


