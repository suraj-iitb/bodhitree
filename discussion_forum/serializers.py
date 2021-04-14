from rest_framework import serializers

from .models import DiscussionForum


class DiscussionForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionForum
        fields = ["anonymous_to_instructor", "send_email_to_all"]
