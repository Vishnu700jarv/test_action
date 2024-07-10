from datetime import timezone
import random
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import  Group, Permission, AbstractUser, BaseUserManager
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        if not mobile:
            raise ValueError(_('The Mobile field must be set'))
        mobile = self.normalize_mobile(mobile)
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_staff=True and is_superuser=True.'))
        return self.create_user(mobile, password, **extra_fields)

    def normalize_mobile(self, mobile):
        return mobile.strip().replace(' ', '')



class CustomUser(AbstractUser):
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sms_notification = models.BooleanField(default=False)
    email_notification = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    user_role = models.CharField(max_length=20, default='user')
    user_image = models.ImageField(upload_to='users/', null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    APPROVAL_CHOICES = [
        ('accepted', 'Accepted'),
        ('disabled', 'Disabled'),
    ]
    approval_status = models.CharField(
        max_length=10,
        choices=APPROVAL_CHOICES,
        default='accepted'
    )
    organization = models.CharField(max_length=200, default='APD')
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="customuser_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_permissions",
        related_query_name="user",
    )

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = "ytaUser"



class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    action = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ytaUserActivity"


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.TextField(blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    customizations = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = "ytaUserProfile"

class Reward(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    points = models.IntegerField()
    description = models.TextField()
    type = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='pending')
    expiration_date = models.DateField()
    redeemed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ytaUserReward"

class OTP(models.Model):
    mobile_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # Check if OTP is older than 5 minutes
        return (datetime.datetime.now(datetime.timezone.utc) - self.created_at) > datetime.timedelta(minutes=5)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        UserActivity.objects.create(user=instance, action="User created")

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    profile, created = Profile.objects.get_or_create(user=instance)
    if not created:
        profile.first_name = instance.first_name if hasattr(instance, 'first_name') else profile.first_name
        profile.last_name = instance.last_name if hasattr(instance, 'last_name') else profile.last_name
        profile.email = instance.email if hasattr(instance, 'email') else profile.email
        profile.phone_number = instance.phone_number if hasattr(instance, 'phone_number') else profile.phone_number
        profile.save()
