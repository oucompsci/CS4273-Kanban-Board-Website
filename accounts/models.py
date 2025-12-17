from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    group_name = models.CharField(max_length=255, blank=True, null=True)
    roles = models.CharField(max_length=255, blank=True, null=True)
    semester = models.CharField(max_length=255, blank=True, null=True)
    repo_link = models.URLField(max_length=500, blank=True, null=True)
    project_title = models.CharField(max_length=255, blank=True, null=True)
    project_mentor = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username


