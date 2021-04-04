from rest_framework import serializers

from .models import Course, CourseHistory


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        course_history = CourseHistory(
            user=validated_data["owner"], course=instance, role="I", status="E"
        )
        course_history.save()
        return instance
