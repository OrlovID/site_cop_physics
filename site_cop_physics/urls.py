"""
URL configuration for site_cop_physics project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include
from django.urls import path
from lessons import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('lessons/', include('lessons.urls')),
    path('', views.index),
    path('tasks-list', views.tasks_list),
    path('add-task', views.add_task),
    path('send-task', views.send_task),
    path('content-stats', views.show_content_stats),
    path('lesson-random', views.lesson_random),
    path('lesson-random-reset', views.lesson_random_reset),
    path('lesson-settings', views.lesson_settings),
    path('lesson-main', views.lesson_main),
    path('lesson-check-answers', views.lesson_check_answers),
]
