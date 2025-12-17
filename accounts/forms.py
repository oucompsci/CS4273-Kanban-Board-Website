from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

ROLE_CHOICES = [
    ('None', '---'),
    ('Product Owner', 'Product Owner'),
    ('SM1', 'Sprint Master 1'),
    ('SM2', 'Sprint Master 2'),
    ('SM3', 'Sprint Master 3'),
    ('SM4', 'Sprint Master 4'),
    ('Mentor/Client', 'Mentor/Client'),
]

GROUP_CHOICES = [
    ('Group A', 'Group A'),
    ('Group B', 'Group B'),
    ('Group C', 'Group C'),
    ('Group D', 'Group D'),
    ('Group E', 'Group E'),
    ('Group F', 'Group F'),
    ('Group G', 'Group G'),
    ('Group H', 'Group H'),
    ('Group I', 'Group I'),
    ('Group J', 'Group J'),
    ('Group K', 'Group K'),
    ('Group L', 'Group L'),
    ('Group M', 'Group M'),
    ('Group N', 'Group N'),
   
]

SEMESTER_CHOICES = [
    ('Fall 2025', 'Fall 2025'),
    # Add more semesters as needed
]

class CustomUserCreationForm(UserCreationForm):

    name = forms.CharField(max_length=255, required=True, help_text='Your full name')
    email = forms.EmailField()
    group_name = forms.ChoiceField(choices=GROUP_CHOICES, widget=forms.Select)
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, widget=forms.Select)
#    project_mentor = forms.CharField(max_length=255, required=True)
#    project_title = forms.CharField(max_length=255, required=True)
    code = forms.CharField(max_length=20, required=True, help_text='Enter the registration code')



    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['name','username', 'email', 'password1', 'password2', 'group_name', 'semester','code']

class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField()
    group_name = forms.ChoiceField(choices=GROUP_CHOICES, widget=forms.Select)
    roles = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select)
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, widget=forms.Select) 

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ['username', 'email', 'group_name', 'roles', 'semester']

class UpdateRoleForm(forms.ModelForm):
    roles = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select)

    class Meta:
        model = CustomUser
        fields = ['roles']

