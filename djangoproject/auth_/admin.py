from django.contrib import admin
from .models import CustomUser, Profile
# from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Profile)
