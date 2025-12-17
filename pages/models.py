# models.py

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Task(models.Model):
    STATUS_CHOICES = [
        ('to_do', 'To Do'),
        ('doing', 'Doing'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ]

    SPRINT_CHOICES = [
        ('S1', 'S1'),
        ('S2', 'S2'),
        ('S3', 'S3'),
        ('S4', 'S4'),

    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=False, null=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='to_do')
    sprint = models.CharField(max_length=15, choices=SPRINT_CHOICES, default='S1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    risk_management = models.CharField(max_length=1000, blank=True, null=True) 
    challenges = models.CharField(max_length=1000, blank=True, null=True)
    lesson_learned = models.TextField(blank=True, null=True)
    # NEW: a task this task depends on
    depends_on = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependents',
        help_text='This ticket cannot complete until the selected ticket is done.'
    )
    def clean(self):
        super().clean()
        if self.depends_on and self.status == 'done' and self.depends_on.status != 'done':
            raise ValidationError({
                'depends_on': f'This ticket depends on "{self.depends_on.title}", which is not done yet.'
            })

    def save(self, *args, **kwargs):
        # Ensure validation always runs before saving
        self.full_clean()
        return super().save(*args, **kwargs)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    def user_group_name(self):
        return self.user.group_name
    user_group_name.short_description = 'Group'
