from django.urls import path
from .views import account_details, task_list, task_create, task_update, task_delete, my_progress, group_project, overview, mentor_page, individual_progress


urlpatterns = [
    path('account/', account_details, name='account_details'),
    path('tasks/', task_list, name='task_list'),
    path('tasks/create/', task_create, name='task_create'),
    path('tasks/update/<int:pk>/', task_update, name='task_update'),
    path('tasks/delete/<int:pk>/', task_delete, name='task_delete'),
    path('my_progress/', my_progress, name='my_progress'),
    path('group_project/', group_project, name='group_project'),
    path('individual_progress/', individual_progress, name='individual_progress'),
    path('overview/', overview, name='overview'),
    path('mentor/', mentor_page, name='mentor_page'),

  
]

