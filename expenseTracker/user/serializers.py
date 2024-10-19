from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True},
            'mobile_no': {'required': True},
            'name': {'required': True},
        }