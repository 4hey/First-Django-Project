from django.contrib import admin
from django.urls import path, include
from . import views
from .views import ScheduleListView, ScheduleDetailView, ScheduleCreateView, ScheduleUpdateView, ScheduleDeleteView

app_name = 'weatherapp'

urlpatterns = [
    path('', ScheduleListView.as_view(), name='home'),
    path('<int:pk>/', ScheduleDetailView.as_view(), name='detail'),
    path('create/', ScheduleCreateView.as_view(), name='create'),
    path('<int:pk>/update/', ScheduleUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', ScheduleDeleteView.as_view(), name='delete')
]
