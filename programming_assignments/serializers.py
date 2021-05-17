from rest_framework import serializers

from .models import AdvancedProgrammingAssignment, SimpleProgrammingAssignment


class SimpleProgrammingAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleProgrammingAssignment
        fields = "__all__"


class AdvancedProgrammingAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancedProgrammingAssignment
        fields = "__all__"
