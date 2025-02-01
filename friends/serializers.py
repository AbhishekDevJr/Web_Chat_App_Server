from rest_framework import serializers
from .models import FriendRequestModel

class FriendRequestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequestModel
        fields = ('sender', 'receiver', 'status', 'timestamp')