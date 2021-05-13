from django.shortcuts import get_object_or_404
from rest_framework import serializers

from discussion_forum.models import DiscussionForum
from discussion_forum.serializers import DiscussionForumSerializer

from .models import (
    Announcement,
    Chapter,
    Course,
    CourseHistory,
    Page,
    Schedule,
    Section,
)


class CourseSerializer(serializers.ModelSerializer):
    df_settings = DiscussionForumSerializer()

    class Meta:
        model = Course
        fields = "__all__"

    def create(self, validated_data):
        df_settings_data = validated_data.pop("df_settings")
        course = Course.objects.create(**validated_data)
        DiscussionForum.objects.create(course=course, **df_settings_data)
        return course

    def update(self, instance, validated_data):
        df_settings_data = validated_data.pop("df_settings", {})

        # HTML checkboxes (For DRF Browsable API) do not send any value,
        # but should be treated as `False` by BooleanField
        # validated_data_keys = validated_data.keys() if validated_data else []
        # course_boolean_fields = ["is_published"]
        # for course_boolean_field in course_boolean_fields:
        #     if course_boolean_field not in validated_data_keys:
        #         validated_data[course_boolean_field]=False
        # df_settings_data_keys = df_settings_data.keys() if df_settings_data else []
        # df_boolean_fields = ["anonymous_to_instructor", "send_email_to_all"]
        # for df_boolean_field in df_boolean_fields:
        #     if df_boolean_field not in df_settings_data_keys:
        #         df_settings_data[df_boolean_field]=False

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        discussion_forum = get_object_or_404(DiscussionForum, course=instance)
        if df_settings_data:
            for attr, value in df_settings_data.items():
                setattr(discussion_forum, attr, value)
            discussion_forum.save()
        return instance


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


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"
