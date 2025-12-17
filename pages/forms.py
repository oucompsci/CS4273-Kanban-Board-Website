# forms.py
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['description', 'status', 'sprint', 'depends_on']
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'Describe The Ticket in Details..'}),
            'status': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = 'to_do'
        self.fields['status'].disabled = True

        # Filter the depends_on queryset:
        qs = Task.objects.all()
        # limit to same group if we know who is editing
        if self.request_user and getattr(self.request_user, 'group_name', None):
            qs = qs.filter(user__group_name=self.request_user.group_name)
        # when editing, don’t allow selecting itself
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        self.fields['depends_on'].queryset = qs.order_by('sprint', 'title')
        self.fields['depends_on'].required = False
        self.fields['depends_on'].label = 'Depends on'
        self.fields['depends_on'].help_text = '  (optional)'

    def clean(self):
        cleaned = super().clean()
        dep = cleaned.get('depends_on')

        # prevent self-dependency
        if self.instance and dep and dep.pk == self.instance.pk:
            self.add_error('depends_on', 'A ticket cannot depend on itself.')

        # NEW RULE: block marking done if dependency is not done
        # figure out what status will be after saving
        if self.instance:  
            # if editing, new status comes from form data, fallback to existing
            new_status = cleaned.get('status') or self.instance.status
        else:
            new_status = cleaned.get('status')

        if dep and new_status == 'done' and dep.status != 'done':
            self.add_error('depends_on', f'This ticket depends on "{dep.title}", which is not done yet.')

        return cleaned

class UpdateStatusAndPrioritizationForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status', 'sprint']

class UpdateStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=Task.STATUS_CHOICES, attrs={'class': 'status-select'}),
        }

class UpdateRiskManagementForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['risk_management']

class UpdateChallengesForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['challenges']

class UpdateLessonLearnedForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['lesson_learned']

class SprintEvaluationForm(forms.Form):
    sprint1_evaluation = forms.IntegerField(label="Sprint 1 Evaluation", min_value=0, max_value=10, required=False)
    sprint2_evaluation = forms.IntegerField(label="Sprint 2 Evaluation", min_value=0, max_value=10, required=False)
    sprint3_evaluation = forms.IntegerField(label="Sprint 3 Evaluation", min_value=0, max_value=10, required=False)
    sprint4_evaluation = forms.IntegerField(label="Sprint 4 Evaluation", min_value=0, max_value=10, required=False)

