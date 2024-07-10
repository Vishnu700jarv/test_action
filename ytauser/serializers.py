from rest_framework import serializers
from .models import CustomUser, Profile, UserActivity, Reward
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

User = get_user_model()

class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            mobile=validated_data['mobile'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user
    
class CreateUserWithNPSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile', 'password']

    def validate_password(self, value):
        # You can add custom validation for password here if needed
        return value  # Allow empty password

    def create(self, validated_data):
        # Handle the password explicitly if it's not provided
        password = validated_data.pop('password', '')
        user = User.objects.create_user(
            mobile=validated_data['mobile'],
            password=password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user
class LoginUserSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        mobile = attrs.get('mobile')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), mobile=mobile, password=password)
        if not user:
            msg = _('Unable to log in with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'mobile', 'email', 'password']
    
    def create(self, validated_data):
        user = CustomUser.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            mobile=validated_data['mobile'],
            email=validated_data.get('email', None)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        # Password update should be handled separately in a dedicated view
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user']

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['user', 'action']

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['user', 'points', 'description']
