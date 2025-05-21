from rest_framework import serializers
from rest_framework.serializers import Serializer, ModelSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from .models import BaseUser


class UserRegistrationSerializer(Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True, validators=[validate_email])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = BaseUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'password2')
        # Adjust these fields based on your User model

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove password2 as it's not part of the User model
        validated_data.pop('password2')
        user = BaseUser.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login. Requires email and password.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, # Password should not be sent back in response
        required=True,
        style={'input_type': 'password'} # Helps DRF browsable API render it correctly
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # Note: Django's authenticate usually takes 'username'.
            # If your usernames ARE emails (as setup in registration), this works.
            # If usernames are different, you might need to fetch the user by email first
            # and then use user.check_password(password).
            # Or implement a custom authentication backend.
            # For simplicity here, we assume username == email.
            user = authenticate(request=self.context.get('request'), username=email, password=password)

            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')

            # Check if user account is active
            if not user.is_active:
                 msg = 'User account is disabled.'
                 raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        # Add the validated user to the serializer's validated_data
        data['user'] = user
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = '__all__'