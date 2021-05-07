from rest_framework import serializers

from .models import Crib, CribReply


class CribSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crib
        fields = "__all__"


class CribReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = CribReply
        fields = "__all__"
