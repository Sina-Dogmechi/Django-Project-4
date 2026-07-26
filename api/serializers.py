from rest_framework import serializers
from home.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_active', 'is_staff', 'date_joined')


# Validators
def clean_email(value):
    if 'admin' in value:
        raise serializers.ValidationError("email cannot contain 'admin'")

class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, validators=[clean_email])
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    # Field-level validation
    def validate_username(self, value):
        if value == 'admin':
            raise serializers.ValidationError('username cant be admin')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('email already exists')
        return value

    # Object-level validation
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords must match')
        return data


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
