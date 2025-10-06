from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    userid = serializers.IntegerField(read_only=True, source='id')
    
    class Meta:
        model = CustomUser
        fields = ('userid', 'username', 'email', 'password', 'first_name', 'last_name')
        
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A User with give Username already exists in Database.")
        return value
    
    def create(self, validated_data):
        user_new = CustomUser(**validated_data)
        user_new.set_password(validated_data['password'])
        user_new.save()
        return user_new