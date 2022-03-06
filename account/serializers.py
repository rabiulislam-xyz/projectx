from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'phone')

        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if 'password' in attrs:
            attrs['password'] = make_password(attrs['password'])
        return attrs


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')
