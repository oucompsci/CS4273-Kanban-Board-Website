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
    # Logged-in user's group
    user_group = request.user.group_name

    # All tasks belonging to members of this group
    tasks = (
        Task.objects
        .filter(user__group_name=user_group)
        .order_by('sprint', 'id')
    )

    # Members available in assignment dropdowns
    group_members = CustomUser.objects.filter(
        group_name=user_group
    )

    # Scrum Master -> sprint permission
    role_to_sprint = {
        'SM1': 'S1',
        'SM2': 'S2',
        'SM3': 'S3',
        'SM4': 'S4',
    }

    allowed_sprint = role_to_sprint.get(request.user.roles)

    if request.method == 'POST':

        # Which sprint's Update All button was clicked?
        submitted_sprint = request.POST.get('sprint')

        # Security: user must be the Scrum Master for that sprint
        if not allowed_sprint or submitted_sprint != allowed_sprint:
            messages.error(
                request,
                'You do not have permission to update this sprint.'
            )
            return redirect('task_list')

        # Only update tasks from:
        # 1. this user's group
        # 2. the submitted sprint
        sprint_tasks = tasks.filter(
            sprint=submitted_sprint
        )

        updated_count = 0

        try:
            with transaction.atomic():

                for task in sprint_tasks:

                    status = request.POST.get(
                        f'status_{task.id}'
                    )

                    assign_user_id = request.POST.get(
                        f'assign_user_{task.id}'
                    )

                    changed = False


                    # =========================================
                    # STATUS
                    # =========================================

                    # Status dropdown is only submitted for
                    # To Do / Cancel tasks.
                    if status is not None:

                        if status not in ['to_do', 'cancel']:
                            raise ValidationError(
                                f'Invalid status for "{task.title}".'
                            )

                        if task.status != status:
                            task.status = status
                            changed = True


                    # =========================================
                    # ASSIGNED USER
                    # =========================================

                    if assign_user_id:

                        assigned_user = group_members.filter(
                            id=assign_user_id
                        ).first()

                        if not assigned_user:
                            raise ValidationError(
                                f'Invalid assigned user for "{task.title}".'
                            )

                        if task.user_id != assigned_user.id:
                            task.user = assigned_user
                            changed = True


                    # =========================================
                    # SAVE
                    # =========================================

                    if changed:
                        task.save()
                        updated_count += 1


            if updated_count > 0:

                messages.success(
                    request,
                    f'{updated_count} ticket(s) updated successfully '
                    f'for {submitted_sprint}.'
                )

            else:

                messages.info(
                    request,
                    f'No changes detected for {submitted_sprint}.'
                )


        except ValidationError as e:

            if hasattr(e, 'message_dict'):
                error_message = '; '.join(
                    sum(e.message_dict.values(), [])
                )
            else:
                error_message = '; '.join(e.messages)

            messages.error(
                request,
                error_message
            )


        return redirect('task_list')


    return render(
        request,
        'task_list.html',
        {
            'tasks': tasks,
            'group_members': group_members,
        }
    )


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

        # A user may only modify their own tickets.
        task = get_object_or_404(Task, id=task_id, user=request.user)

        # ---------------------------------------------------------
        # Move To Do -> Doing and save initial Risk Management
        # ---------------------------------------------------------
        if action == 'to_do_to_doing':
            risk_management = request.POST.get('risk_management', '').strip()

            if not risk_management:
                messages.error(request, 'You should write at least one risk.')
                return redirect('my_progress')

            task.risk_management = risk_management
            task.status = 'doing'

            try:
                task.save()
                messages.success(
                    request,
                    f'"{task.title}" moved to Doing.'
                )
            except ValidationError as e:
                messages.error(
                    request,
                    '; '.join(sum(e.message_dict.values(), []))
                )

            return redirect('my_progress')

        # ---------------------------------------------------------
        # Edit existing Risk Management
        # ---------------------------------------------------------
        elif action == 'update_risk_management':
            if task.status not in ['doing', 'done']:
                messages.error(
                    request,
                    'Risk Management can only be edited after the ticket has started.'
                )
                return redirect('my_progress')

            risk_management = request.POST.get('risk_management', '').strip()

            if not risk_management:
                messages.error(
                    request,
                    'Risk Management cannot be empty.'
                )
                return redirect('my_progress')

            task.risk_management = risk_management

            try:
                task.save()
                messages.success(
                    request,
                    f'Risk Management updated for "{task.title}".'
                )
            except ValidationError as e:
                messages.error(
                    request,
                    '; '.join(sum(e.message_dict.values(), []))
                )

            return redirect('my_progress')

        # ---------------------------------------------------------
        # Move Doing -> Done and save initial Challenges
        # ---------------------------------------------------------
        elif action == 'doing_to_done':

            # Prevent completion if dependency is unfinished
            if task.depends_on and task.depends_on.status != 'done':
                messages.error(
                    request,
                    f'Cannot mark "{task.title}" as Done because it depends on '
                    f'"{task.depends_on.title}" which is '
                    f'{task.depends_on.get_status_display()}.'
                )
                return redirect('my_progress')

            # Get both fields from the same form
            risk_management = request.POST.get(
                'risk_management', ''
            ).strip()

            challenges = request.POST.get(
                'challenges', ''
            ).strip()

            # Validate Risk Management
            if not risk_management:
                messages.error(
                    request,
                    'Risk Management cannot be empty.'
                )
                return redirect('my_progress')

            # Validate Challenges
            if not challenges:
                messages.error(
                    request,
                    'You should write at least one challenge you faced.'
                )
                return redirect('my_progress')

            # Save both comments
            task.risk_management = risk_management
            task.challenges = challenges

            # Move task to Done
            task.status = 'done'

            try:
                task.save()

                messages.success(
                    request,
                    f'"{task.title}" marked as Done.'
                )

            except ValidationError as e:
                messages.error(
                    request,
                    '; '.join(sum(e.message_dict.values(), []))
                )

            return redirect('my_progress')
        # ---------------------------------------------------------
        # Edit existing Challenges
        # ---------------------------------------------------------
        elif action == 'update_challenges':
            if task.status != 'done':
                messages.error(
                    request,
                    'Challenges can only be edited after the ticket is Done.'
                )
                return redirect('my_progress')

            challenges = request.POST.get('challenges', '').strip()

            if not challenges:
                messages.error(
                    request,
                    'Challenges cannot be empty.'
                )
                return redirect('my_progress')

            task.challenges = challenges

            try:
                task.save()
                messages.success(
                    request,
                    f'Challenges updated for "{task.title}".'
                )
            except ValidationError as e:
                messages.error(
                    request,
                    '; '.join(sum(e.message_dict.values(), []))
                )

            return redirect('my_progress')

        # ---------------------------------------------------------
        # Add or edit Lesson Learned
        # ---------------------------------------------------------
        elif action == 'update_lesson_learned':

            if task.status != 'done':
                messages.error(
                    request,
                    'Progress comments can only be edited after the ticket is Done.'
                )
                return redirect('my_progress')

            # Get all three fields from the same form
            risk_management = request.POST.get(
                'risk_management', ''
            ).strip()

            challenges = request.POST.get(
                'challenges', ''
            ).strip()

            lesson_learned = request.POST.get(
                'lesson_learned', ''
            ).strip()

            # Validate Risk Management
            if not risk_management:
                messages.error(
                    request,
                    'Risk Management cannot be empty.'
                )
                return redirect('my_progress')

            # Validate Challenges
            if not challenges:
                messages.error(
                    request,
                    'Challenges cannot be empty.'
                )
                return redirect('my_progress')

            # Validate Lesson Learned
            if not lesson_learned:
                messages.error(
                    request,
                    'Lesson Learned cannot be empty.'
                )
                return redirect('my_progress')

            # Save all three fields together
            task.risk_management = risk_management
            task.challenges = challenges
            task.lesson_learned = lesson_learned

            try:
                task.save()

                messages.success(
                    request,
                    f'Progress comments updated for "{task.title}".'
                )

            except ValidationError as e:
                messages.error(
                    request,
                    '; '.join(sum(e.message_dict.values(), []))
                )

            return redirect('my_progress')
    # -------------------------------------------------------------
    # GET request
    # -------------------------------------------------------------
    tasks_to_do = (
        Task.objects
        .filter(user=request.user, status='to_do')
        .select_related('depends_on')
    )

    tasks_doing = (
        Task.objects
        .filter(user=request.user, status='doing')
        .select_related('depends_on')
    )

    tasks_done = (
        Task.objects
        .filter(user=request.user, status='done')
        .select_related('depends_on')
    )

    return render(request, 'my_progress.html', {
        'tasks_to_do': tasks_to_do,
        'tasks_doing': tasks_doing,
        'tasks_done': tasks_done,
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
