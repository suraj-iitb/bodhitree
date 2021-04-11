from rest_framework import serializers

from .models import Chapter, Course, CourseHistory, Page


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


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
