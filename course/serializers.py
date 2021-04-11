from rest_framework import serializers

from discussion_forum.models import DiscussionForum
from discussion_forum.serializers import DiscussionForumSerializer

from .models import Chapter, Course, CourseHistory, Page


class CourseSerializer(serializers.ModelSerializer):
    df_settings = DiscussionForumSerializer()

    class Meta:
        model = Course
        fields = "__all__"

    def create(self, validated_data):
        df_settings_data = validated_data.pop("df_settings")
        course = Course.objects.create(**validated_data)
        # for df_setting_data in df_settings_data:
        DiscussionForum.objects.create(course=course, **df_settings_data)
        return course


class CourseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseHistory
        fields = "__all__"


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = "__all__"


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"
