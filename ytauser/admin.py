from django.contrib import admin

from .models import CustomUser, Profile, UserActivity, Reward,OTP

admin.site.register((CustomUser, UserActivity, Profile, Reward,OTP))
