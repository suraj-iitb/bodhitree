from rest_framework import serializers

from .models import SimpleProgrammingAssignment


class SimpleProgrammingAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleProgrammingAssignment
        fields = "__all__"
