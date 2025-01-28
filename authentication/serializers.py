from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')
        
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A User with give Username already exists in Database.")
        return value
    
    def create(self, validated_data):
        return CustomUser.objects.create(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
        )