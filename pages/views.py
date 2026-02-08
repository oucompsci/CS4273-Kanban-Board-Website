from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.forms import UpdateRoleForm
from accounts.models import CustomUser
from .models import Task
from .forms import TaskForm, SprintEvaluationForm, UpdateStatusForm, UpdateRiskManagementForm, UpdateChallengesForm, UpdateLessonLearnedForm
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.db import transaction
from django.http import Http404
from django.utils.html import escape
import json




from django.contrib import messages

@login_required
def account_details(request):
    user = request.user
    same_group_users = CustomUser.objects.filter(group_name=user.group_name).exclude(id=user.id)

    if request.method == 'POST':
        form = UpdateRoleForm(request.POST, instance=user)
        if form.is_valid():
            selected_role = form.cleaned_data['roles']
            if same_group_users.filter(roles=selected_role).exists():
                messages.error(request, f'The role "{selected_role}" is already assigned to another user in your group.')
            else:
                form.save()

    
        repo_link = request.POST.get('repo_link')
        if repo_link:
            user.repo_link = repo_link
            user.save(update_fields=['repo_link'])
        return redirect('account_details')

    else:
        form = UpdateRoleForm(instance=user)

    return render(request, 'account_details.html', {'form': form, 'same_group_users': same_group_users})



@login_required
def task_list(request):
    # Get the group of the logged-in user
    user_group = request.user.group_name

    # Fetch tasks for all members of the same group and sort by sprint
    tasks = Task.objects.filter(user__group_name=user_group).order_by('sprint')

    # Fetch all group members for the dropdown
    group_members = CustomUser.objects.filter(group_name=user_group)

    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id)

        # Update task status and sprint
        task.status = request.POST.get('status')

        # Update assigned user if provided
        assign_user_id = request.POST.get('assign_user')
        if assign_user_id:
            assigned_user = get_object_or_404(CustomUser, id=assign_user_id)
            task.user = assigned_user

        # Save task and refresh page
        task.save()
        return redirect('task_list')

    # Render template with tasks and group members
    return render(request, 'task_list.html', {'tasks': tasks, 'group_members': group_members})

@login_required
def task_create(request):
    # helper to compute next ticket number per sprint for THIS user's group
    def next_num_for(sprint_code: str) -> int:
        return Task.objects.filter(
            user__group_name=request.user.group_name,
            sprint=sprint_code
        ).count() + 1

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                task = form.save(commit=False)
                task.user = request.user

                # Build the title
                sprint_code = form.cleaned_data['sprint']            # e.g. 'S1'
                sprint_num = sprint_code.replace('S', '')            # '1'
                next_num = next_num_for(sprint_code)                 # e.g. 7

                # Compose the title
                task.title = f"CS4273_S{sprint_num}_Ticket {next_num}"

                task.save()
            messages.success(request, f'Ticket "{task.title}" created.')
            return redirect('task_list')
    else:
        form = TaskForm(user=request.user)

    # For the GET (render form), send preview counts for each sprint
    next_counts = {
        'S1': next_num_for('S1'),
        'S2': next_num_for('S2'),
        'S3': next_num_for('S3'),
        'S4': next_num_for('S4'),
    }
    next_counts_json = json.dumps(next_counts)

    return render(request, 'task_form.html', {
        'form': form,
        'next_counts': next_counts,
        'next_counts_json': next_counts_json,
    })

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')  # Redirect to task list after deletion

    return render(request, 'task_confirm_delete.html', {'task': task})

# views.py

@login_required
def my_progress(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        action = request.POST.get('action')

        # Only allow the signed-in user to operate on their own task
        task = get_object_or_404(Task, id=task_id, user=request.user)

        # to_do -> doing
        if action == 'to_do_to_doing':
            risk_management = request.POST.get('risk_management')
            task.risk_management = risk_management
            task.status = 'doing'
            try:
                task.save()
                messages.success(request, f'"{task.title}" moved to Doing.')
            except ValidationError as e:
                messages.error(request, '; '.join(sum(e.message_dict.values(), [])))
            return redirect('my_progress')

        # doing -> done (BLOCK if dependency not done)
        elif action == 'doing_to_done':
            if task.depends_on and task.depends_on.status != 'done':
                messages.error(
                    request,
                    f'Cannot mark "{task.title}" as Done because it depends on '
                    f'"{task.depends_on.title}" which is {task.depends_on.get_status_display()}.'
                )
                return redirect('my_progress')

            challenges = request.POST.get('challenges')
            task.challenges = challenges
            task.status = 'done'
            try:
                task.save()  # if you also add model-level validation, this will raise ValidationError
                messages.success(request, f'"{task.title}" marked as Done.')
            except ValidationError as e:
                messages.error(request, '; '.join(sum(e.message_dict.values(), [])))
            return redirect('my_progress')

        # update lesson learned
        elif action == 'update_lesson_learned':
            lesson_learned = request.POST.get('lesson_learned')
            task.lesson_learned = lesson_learned
            try:
                task.save()
                messages.success(request, f'Lesson learned updated for "{task.title}".')
            except ValidationError as e:
                messages.error(request, '; '.join(sum(e.message_dict.values(), [])))
            return redirect('my_progress')

        # fallback: status form (currently unused in this template flow)
        else:
            form = UpdateStatusForm(request.POST, instance=task)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, f'Status updated for "{task.title}".')
                except ValidationError as e:
                    messages.error(request, '; '.join(sum(e.message_dict.values(), [])))
            return redirect('my_progress')

    # GET: show lists (optimize with select_related for dependency)
    tasks_to_do = Task.objects.filter(user=request.user, status='to_do').select_related('depends_on')
    tasks_doing = Task.objects.filter(user=request.user, status='doing').select_related('depends_on')
    tasks_done  = Task.objects.filter(user=request.user, status='done').select_related('depends_on')

    forms_doing = {t.id: UpdateStatusForm(instance=t) for t in tasks_doing}
    forms_done = {t.id: UpdateStatusForm(instance=t) for t in tasks_done}
    forms_risk_management = {t.id: UpdateRiskManagementForm(instance=t) for t in tasks_to_do}
    forms_challenges = {t.id: UpdateChallengesForm(instance=t) for t in tasks_doing}
    forms_lesson_learned = {t.id: UpdateLessonLearnedForm(instance=t) for t in tasks_done}

    return render(request, 'my_progress.html', {
        'tasks_to_do': tasks_to_do,
        'tasks_doing': tasks_doing,
        'tasks_done': tasks_done,
        'forms_doing': forms_doing,
        'forms_done': forms_done,
        'forms_risk_management': forms_risk_management,
        'forms_challenges': forms_challenges,
        'forms_lesson_learned': forms_lesson_learned,
    })

@login_required
def group_project(request):
    user = request.user
    user_group = user.group_name

    # Get group members excluding the current user
    same_group_users = CustomUser.objects.filter(group_name=user_group)

    tasks_to_do = Task.objects.filter(user__group_name=user_group, status='to_do')
    tasks_doing = Task.objects.filter(user__group_name=user_group, status='doing')
    tasks_done = Task.objects.filter(user__group_name=user_group, status='done')

    return render(request, 'group_project.html', {
        'same_group_users': same_group_users,
        'tasks_to_do': tasks_to_do,
        'tasks_doing': tasks_doing,
        'tasks_done': tasks_done,
    })


@login_required
def individual_progress(request):
    tasks_to_do = Task.objects.filter(user=request.user, status='to_do')
    tasks_doing = Task.objects.filter(user=request.user, status='doing')
    tasks_done = Task.objects.filter(user=request.user, status='done')
    return render(request, 'individual_progress.html', {
                'tasks_to_do': tasks_to_do,
                'tasks_doing': tasks_doing,
                'tasks_done': tasks_done,
    })


@login_required
def overview(request):
    user = request.user
    same_group_users = CustomUser.objects.filter(group_name=user.group_name).exclude(id=user.id)
    tasks_to_do = Task.objects.filter(user__group_name=user.group_name, status='to_do')
    tasks_doing = Task.objects.filter(user__group_name=user.group_name, status='doing')
    tasks_done = Task.objects.filter(user__group_name=user.group_name, status='done')

    return render(request, 'overview.html', {
        'user': user,
        'same_group_users': same_group_users,
        'tasks_to_do': tasks_to_do,
        'tasks_doing': tasks_doing,
        'tasks_done': tasks_done,
    })



@login_required
def mentor_page(request):
    user_group = request.user.group_name

    # Get the selected sprint from the GET parameter
    selected_sprint = request.GET.get('sprint', '')

    # Filter tasks based on group and sprint
    if selected_sprint:
        tasks_to_do = Task.objects.filter(user__group_name=user_group, status='to_do', sprint=selected_sprint)
        tasks_doing = Task.objects.filter(user__group_name=user_group, status='doing', sprint=selected_sprint)
        tasks_done = Task.objects.filter(user__group_name=user_group, status='done', sprint=selected_sprint)
    else:
        tasks_to_do = Task.objects.filter(user__group_name=user_group, status='to_do')
        tasks_doing = Task.objects.filter(user__group_name=user_group, status='doing')
        tasks_done = Task.objects.filter(user__group_name=user_group, status='done')

    return render(request, 'mentor.html', {
        'tasks_to_do': tasks_to_do,
        'tasks_doing': tasks_doing,
        'tasks_done': tasks_done,
        'sprint': selected_sprint,
    })
