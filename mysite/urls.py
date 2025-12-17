from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from pages.views import mentor_page 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('pages/', include('pages.urls')),  # Include the pages app URLs
    path('', lambda request: redirect('login'), name='root'),  # Redirect root URL to login
    path('mentor/', mentor_page, name='mentor_page'),  # Add this line for mentor page

]
