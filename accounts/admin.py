from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['name','username', 'email', 'group_name', 'roles', 'semester','project_title','project_mentor', 'repo_link','is_staff']

admin.site.register(CustomUser, CustomUserAdmin)
