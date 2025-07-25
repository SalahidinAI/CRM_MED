from rest_framework import serializers
from .models import *


class UserProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'role', 'role_display']
