from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'user_group_name', 'sprint','depends_on', 'created_at', 'updated_at','risk_management','challenges','lesson_learned', 'status')
    search_fields = ('title', 'description', 'user__username')
    list_filter = ('created_at', 'updated_at', 'user')

